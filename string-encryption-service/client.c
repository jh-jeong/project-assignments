/*
 * client.c: client for the string encryption service.
 * Usage: ./client -h host -p port [-o operation] [-s shift]
 */
#include <stdio.h>
#include <unistd.h>
#include <getopt.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <errno.h>
#include <limits.h>
#include "protocol.h"

#define BUF_MAXLEN (PROTOCOL_MAXLEN - SIZE_HDR)

/* Main logic of the CLI client interface.
 * This client will not terminate until EOF is received,
 * or the whole connection is refused. */
int main (int argc, char *argv[]) {
    int arg, status;
    ssize_t n_bytes;
    long arg_l;
    ssize_t res;

    uint8_t op = 0;
    uint8_t shift = 0;
    uint32_t length;

    int sock_fd = 0;
    char *host = NULL, *port = NULL, *endptr = NULL;
    struct addrinfo hints, *server_info, *ptr_ai;

    struct protocol_hdr p_hdr, *hdr_recv;

    char *buf_data = (char *) malloc(BUF_MAXLEN);       /* Buffer for the message contents. */
    char *buf_send = (char *) malloc(PROTOCOL_MAXLEN);  /* Buffer for sending messages. */
    char *buf_recv = (char *) malloc(PROTOCOL_MAXLEN);  /* Buffer for receiving messages. */

    memset(buf_send, 0, PROTOCOL_MAXLEN);
    memset(buf_recv, 0, PROTOCOL_MAXLEN);

    /* Parse the arguments given by the command line */
    while ((arg = getopt(argc, argv, "h:p:o:s:")) != -1) {
        switch (arg) {
            case 'h':   /* Host */
                host = optarg;
                break;
            case 'p':   /* Port */
                port = optarg;
                break;
            case 'o':   /* Operation type */
                if (strcmp(optarg, "0") == 0)
                    op = OP_ENCRYPT;
                else if (strcmp(optarg, "1") == 0)
                    op = OP_DECRYPT;
                else {
                    fprintf(stderr, "Argument -o should be one of 0 (encrypt) or 1 (decrypt).\n");
                    exit(EINVAL);
                }
                break;
            case 's':   /* Shift */
                arg_l = strtol(optarg, &endptr, 10);
                if (errno == ERANGE) {
                    perror("Argument -s");
                    exit(EINVAL);
                }
                else if (endptr == NULL)
                    abort();
                else if (*endptr != 0) {
                    fprintf(stderr, "Argument -s contains a non-digit character.\n");
                    exit(EINVAL);
                }

                if (arg_l < 0) {
                    fprintf(stderr, "Argument -s should be a non-negative.\n");
                    exit(EINVAL);
                }
                if (arg_l > UCHAR_MAX) {
                    fprintf(stderr, "Argument -s ranges in unsigned 8-bits integer.\n");
                    exit(EINVAL);
                }
                shift = (uint8_t) arg_l;
                break;
            case '?':   /* Otherwise */
                if (strchr("hpos", optopt))
                    fprintf(stderr, "Argument -%c requires an argument.\n", optopt);
                else
                    fprintf(stderr, "Invalid argument -%c.\n", optopt);
                exit(EINVAL);
            default:    /* Unreachable */
                abort();
        }
    }

    /* Case when either -h or -p option is missing. */
    if (host == NULL || port == NULL) {
        fprintf(stderr, "Usage: client -h host -p port [-o operation] [-s shift]\n");
        exit(ENOEXEC);
    }

    /* Find information of the server and connect to it. */
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;
    hints.ai_flags = AI_V4MAPPED;

    if ((status = getaddrinfo(host, port, &hints, &server_info)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(status));
        exit(status);
    }
    for (ptr_ai = server_info; ptr_ai != NULL; ptr_ai = ptr_ai->ai_next) {
        if ((sock_fd = socket(ptr_ai->ai_family,
                              ptr_ai->ai_socktype,
                              ptr_ai->ai_protocol)) == -1) {
            perror("client: socket");
            continue;
        }

        if (connect(sock_fd, ptr_ai->ai_addr, ptr_ai->ai_addrlen) == -1) {
            close(sock_fd);
            perror("client: connect");
            continue;
        }
        break;
    }
    if (ptr_ai == NULL) {
        fprintf(stderr, "client: failed to connect\n");
        exit(errno);
    }
    freeaddrinfo(server_info);

    /* Set up the header of the protocol to be sent. */
    p_hdr.op = op;
    p_hdr.shift = shift;

    /* Loop until EOF is received at stdin. */
    while ((n_bytes = read(STDIN_FILENO, buf_data, BUF_MAXLEN)) > 0) {
        size_t size_data = (size_t) n_bytes;

        p_hdr.checksum = 0;
        length = (uint32_t) (SIZE_HDR + size_data);
        p_hdr.length = htonl(length);

        memcpy(buf_send, &p_hdr, SIZE_HDR);
        memcpy(buf_send + SIZE_HDR, buf_data, (size_t) size_data);

        /* Calculate checksum of the protocol. */
        p_hdr.checksum = checksum_protocol(buf_send, length);
        memcpy(buf_send, &p_hdr, SIZE_HDR);

        /* Send the protocol to the server. */
        res = send_protocol(sock_fd, buf_send);
        if (res == -1) {
            perror("client: send");
            close(sock_fd);
            exit(errno);
        }
        else if (res == 0) {
            fprintf(stderr, "Connection is closed by the server.\n");
            close(sock_fd);
            exit(1);
        }

        /* Receive the header data from server, to identify metadata. */
        res = recv_until(sock_fd, buf_recv, SIZE_HDR);
        if (res == -1) {
            perror("client: recv");
            close(sock_fd);
            exit(errno);
        }
        else if (res == 0) {
            fprintf(stderr, "Connection is closed by the server.\n");
            close(sock_fd);
            exit(1);
        }

        hdr_recv = (struct protocol_hdr *) buf_recv;

        if (length != ntohl(hdr_recv->length)) {
            fprintf(stderr, "Sent and received protocol does not match in length.\n");
            close(sock_fd);
            exit(1);
        }

        /* Receive the encrypted data from server. */
        res = recv_until(sock_fd, buf_recv, size_data);
        if (res == -1) {
            perror("client: recv");
            close(sock_fd);
            exit(errno);
        }
        else if (res == 0) {
            fprintf(stderr, "Connection is closed by the server.\n");
            close(sock_fd);
            exit(1);
        }

        /* Print the encrypted message. */
        write(STDOUT_FILENO, buf_recv, size_data);
    }

    if (n_bytes < 0) {
        perror("client: read from stdin");
        close(sock_fd);
        exit(1);
    }

    /* Clean up the resources. */
    close(sock_fd);
    free(buf_data);
    free(buf_send);
    free(buf_recv);
    return 0;
}
