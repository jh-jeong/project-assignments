/*
 * protocol.c: library for the service protocol.
 */
#include <netinet/in.h>
#include <stdio.h>
#include <stdbool.h>
#include "protocol.h"

/* Calculate the checksum of the buffer with given size. */
uint16_t checksum (const char *buf, size_t size) {
    uint64_t sum = 0;
    const uint64_t *b = (uint64_t *) buf;

    uint32_t t1, t2;
    uint16_t t3, t4;

    /* Main loop - 8 bytes at a time */
    while (size >= 8) {
        uint64_t s = *b++;
        sum += s;
        if (sum < s) sum++;
        size -= 8;
    }

    /* Handle tail less than 8-bytes long */
    buf = (const char *) b;
    if (size & 4) {
        uint32_t s = *(uint32_t *) buf;
        sum += s;
        if (sum < s) sum++;
        buf += 4;
        size -= 4;
    }

    if (size & 2) {
        uint16_t s = *(uint16_t *) buf;
        sum += s;
        if (sum < s) sum++;
        buf += 2;
        size -= 2;
    }

    if (size) {
        unsigned char s = *(unsigned char *) buf;
        sum += s;
        if (sum < s) sum++;
    }

    /* Fold down to 16 bits */
    t1 = sum;
    t2 = sum >> 32;
    t1 += t2;
    if (t1 < t2) t1++;
    t3 = t1;
    t4 = t1 >> 16;
    t3 += t4;
    if (t3 < t4) t3++;

    return ~t3;
}

/* Calculate the checksum of a buffer with given size,
 * assuming that there is a protocol message in the buffer.
 * It automatically ignores the checksum field in itself. */
uint16_t checksum_protocol (char *buf, size_t size) {
    uint16_t chks_o, chks_f;
    struct protocol_hdr *hdr = (struct protocol_hdr *) buf;
    chks_o = hdr->checksum;

    hdr->checksum = 0;
    chks_f = checksum(buf, size);
    hdr->checksum = chks_o;

    return chks_f;
}

/* Check whether the protocol header given in the buffer is valid. */
bool verify_header (char *buf) {
    bool result = true;
    uint8_t op;
    uint32_t length;
    struct protocol_hdr *hdr = (struct protocol_hdr *) buf;

    op = hdr->op;
    if (op != OP_DECRYPT && op != OP_ENCRYPT) {
        fprintf(stderr, "Error on verifying a protocol.: "
                "Invalid value of 'op' field.: %d\n", op);
        result = false;
    }

    length = ntohl(hdr->length);
    if (length > PROTOCOL_MAXLEN) {
        fprintf(stderr, "Error on verifying a protocol.: "
                "Maximum length of a protocol is limited by 10M.: %d\n", length);
        result = false;
    }

    if (length < SIZE_HDR) {
        fprintf(stderr, "Error on verifying a protocol.: "
                "The length of a protocol at least the size of header.\n");
        result = false;
    }

    return result;
}

/* Send the contents in buffer to a socket,
 * assuming that there's a protocol message in it. */
ssize_t send_protocol (int sock_fd, char *buf)
{
    struct protocol_hdr *hdr = (struct protocol_hdr *) buf;
    u_int32_t length = ntohl(hdr->length);

    u_int32_t total = 0;        // how many bytes we've sent
    size_t bytes_left = length; // how many we have left to send
    ssize_t n_bytes = 0;

    while(total < length) {
        n_bytes = send(sock_fd, buf+total, bytes_left, 0);
        if (n_bytes <= 0) break;
        total += n_bytes;
        bytes_left -= n_bytes;
    }

    return (n_bytes == -1) ? -1 : (n_bytes == 0) ? 0 : (ssize_t) total;
}

/* Receive the contents from a socket,
 * assuming that the contents we're receiving is a protocol message. */
ssize_t recv_until (int sock_fd, char *buf, size_t length)
{
    uint32_t total = 0;        // how many bytes we've received
    size_t bytes_left = length;    // how many we have left to receive
    ssize_t n_bytes = 0;

    while(total < length) {
        n_bytes = recv(sock_fd, buf+total, bytes_left, 0);
        if (n_bytes <= 0) break;
        total += n_bytes;
        bytes_left -= n_bytes;
    }

    return (n_bytes == -1) ? -1 : (n_bytes == 0) ? 0 : (ssize_t) total;
}