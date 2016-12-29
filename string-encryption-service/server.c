/*
 * server.c: server for the string encryption service.
 * Usage: ./server -p port
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <getopt.h>
#include <netdb.h>
#include <wait.h>
#include <errno.h>
#include <ctype.h>
#include <arpa/inet.h>
#include "protocol.h"

/* Maximum client can be queued. */
#define BACKLOG 128

/* Number of alphabet. */
#define N_ALPHA 26

/* Encode the contents in 'buf' with size 'len', by Caesar cipher.
 * It adds 'shift' to the each character in a modular sense,
 * if the character is lowercase alphabet. */
void encode_msg (uint8_t shift, char *buf, size_t len) {
    int idx;
    uint32_t code;
    char enc;

    for (idx = 0; idx < len; idx++) {
        code = (uint32_t) buf[idx];
        if (isalpha(code) && 'a' <= code) {
            enc = (char) (((code - 'a') + shift) % N_ALPHA);
            buf[idx] = ((char) 'a') + enc;
        }
    }
}

/* Decode the contents in 'buf' with size 'len', by Caesar cipher.
 * It subtracts 'shift' to the each character in a modular sense,
 * if the character is lowercase alphabet. */
void decode_msg (uint8_t shift, char *buf, size_t len)
{
    int idx;
    uint32_t code;
    char enc;

    for (idx = 0; idx < len; idx++) {
        code = (uint32_t) buf[idx];
        if (isalpha(code) && 'a' <= code) {
            enc = (char) (((code - 'a') - shift) % N_ALPHA);
            if (enc < 0)
                enc += (char) N_ALPHA;
            buf[idx] = ((char) 'a') + enc;
        }
    }
}

/* Signal handler when SIGCHLD is raised.
 * It reaps all dead processes. */
void sigchld_handler (int s)
{
    /* waitpid() might overwrite errno, so we save and restore it. */
    int saved_errno = errno;
    while(waitpid(-1, NULL, WNOHANG) > 0);
    errno = saved_errno;
}

/* get sockaddr, IPv4 or IPv6. */
void *get_in_addr(struct sockaddr *sa)
{
    if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

/* Main logic of the CLI server interface. */
int main (int argc, char *argv[]) {
    int arg, status;
    char *port = NULL;

    int listen_fd = 0, data_fd;
    int yes = 1;
    struct addrinfo hints, *server_info, *ptr_ai;

    struct sigaction sa;

    struct sockaddr_storage client_addr;
    socklen_t sin_size;

    /* Parse the arguments given by the command line */
    while ((arg = getopt(argc, argv, "p:")) != -1) {
        switch (arg) {
            case 'p':   /* Port */
                port = optarg;
                break;
            case '?':   /* Otherwise */
                if (strchr("p", optopt))
                    fprintf(stderr, "Argument -%c requires an argument.\n", optopt);
                else
                    fprintf(stderr, "Invalid argument -%c.\n", optopt);
                exit(EINVAL);
            default:    /* Unreachable */
                abort();
        }
    }

    /* Case when the argument -p is missing. */
    if (port == NULL) {
        fprintf(stderr, "Usage: server -p port\n");
        exit(ENOEXEC);
    }

    /* Open the socket. */
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;
    hints.ai_flags = AI_PASSIVE;

    if ((status = getaddrinfo(NULL, port, &hints, &server_info)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(status));
        exit(status);
    }
    for(ptr_ai = server_info; ptr_ai != NULL; ptr_ai = ptr_ai->ai_next) {
        if ((listen_fd = socket(ptr_ai->ai_family,
                              ptr_ai->ai_socktype,
                              ptr_ai->ai_protocol)) == -1) {
            perror("server: socket");
            continue;
        }
        if (setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int)) == -1) {
            perror("setsockopt");
            exit(1);
        }
        if (bind(listen_fd, ptr_ai->ai_addr, ptr_ai->ai_addrlen) == -1) {
            close(listen_fd);
            perror("server: bind");
            continue;
        }
        break;
    }
    if (ptr_ai == NULL)  {
        fprintf(stderr, "server: failed to bind\n");
        exit(1);
    }

    freeaddrinfo(server_info);

    /* Listen on the socket with 'BACKLOG'. */
    if (listen(listen_fd, BACKLOG) == -1) {
        perror("listen");
        exit(1);
    }

    /* Set the signal handler for SIGCHLD. */
    sa.sa_handler = sigchld_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    if (sigaction(SIGCHLD, &sa, NULL) == -1) {
        perror("sigaction");
        exit(1);
    }

    printf("server: waiting for connections...\n");

    /* Loop infinitely, repeat accept() for the incoming clients. */
    while (1) {
        char ip[INET6_ADDRSTRLEN];

        sin_size = sizeof client_addr;
        data_fd = accept(listen_fd, (struct sockaddr *) &client_addr, &sin_size);
        if (data_fd == -1) {
            perror("accept");
            exit(1);
        }

        inet_ntop(client_addr.ss_family,
                  get_in_addr((struct sockaddr *) &client_addr),
                  ip, sizeof ip);
        printf("server: got connection from %s\n", ip);

        /* Logic for child processes */
        if (!fork()) {
            char *buf = (char *) malloc(PROTOCOL_MAXLEN);
            struct protocol_hdr *hdr = NULL;
            uint16_t chks_o, chks_t;
            uint32_t length, len_data;
            int idx;
            ssize_t res;

            memset(buf, 0, PROTOCOL_MAXLEN);

            close(listen_fd); /* child doesn't need the listener */

            while (1) {
                /* Receive the header data from client, to identify metadata. */
                res = recv_until(data_fd, buf, SIZE_HDR);
                if (res == -1) {
                    perror("server: recv");
                    break;
                }
                else if (res == 0) {
                    printf("%s: Connection is closed.\n", ip);
                    close(data_fd);
                    exit(0);
                }

                /* Verify the header. */
                if (!verify_header(buf)) {
                    fprintf(stderr, "%s: Invalid protocol is received.\n", ip);
                    break;
                }

                hdr = (struct protocol_hdr *) buf;
                length = ntohl(hdr->length);
                len_data = length - SIZE_HDR;

                printf("%s: request: \n"
                               "\top: %d, shift: %d, length: %d, checksum: %x\n",
                       ip, hdr->op, hdr->shift, length, hdr->checksum);

                /* Receive the remaining data. */
                res = recv_until(data_fd, buf + SIZE_HDR, len_data);
                if (res == -1) {
                    perror("server: recv");
                    break;
                }
                else if (res == 0) {
                    printf("%s: Connection is closed.\n", ip);
                    close(data_fd);
                    exit(0);
                }

                /* Compare the checksum. */
                chks_o = hdr->checksum;
                chks_t = checksum_protocol(buf, length);
                if (chks_o != chks_t) {
                    fprintf(stderr, "%s: Error on verifying a protocol.: "
                            "Checksum mismatch.: %x != %x\n", ip, chks_o, chks_t);
                    break;
                }

                /* Transform upper-case letters to lower-case letters in the message. */
                for (idx = SIZE_HDR; idx < length; idx++) {
                    buf[idx] = (char) tolower(buf[idx]);
                }

                /* Perform encryption or decryption. */
                switch (hdr->op) {
                    case OP_ENCRYPT:
                        encode_msg(hdr->shift, buf + SIZE_HDR, len_data);
                        break;
                    case OP_DECRYPT:
                        decode_msg(hdr->shift, buf + SIZE_HDR, len_data);
                        break;
                    default:
                        abort();
                }

                /* Update the checksum field. */
                hdr->checksum = checksum_protocol(buf, length);

                /* Reply to the client with encrypted or decrypted message. */
                res = send_protocol(data_fd, buf);
                if (res == -1) {
                    perror("server: send");
                    break;
                }
                else if (res == 0) {
                    printf("%s: Connection is closed.\n", ip);
                    close(data_fd);
                    exit(0);
                }
            }

            /* Clean up the resources. */
            close(data_fd);
            free(buf);
            exit(1);
        }
        close(data_fd);  /* parent doesn't need this. */
    }
}