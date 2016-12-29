/*
 * protocol.h: header for the protocol.c
 * It defines the main protocol structure in the service.
 */
#ifndef STRING_ENCRYPTION_SERVICE_PROTOCOL_H
#define STRING_ENCRYPTION_SERVICE_PROTOCOL_H

#include <stdbool.h>

/* Maximum length a protocol can have. */
#define PROTOCOL_MAXLEN 10485760

/* Size of the protocol header. */
#define SIZE_HDR (sizeof (struct protocol_hdr))

#define OP_ENCRYPT ((u_int8_t) 0)   /* Encrypt the message */
#define OP_DECRYPT ((u_int8_t) 1)   /* Decrypt the message */

/* Structure of a protocol header. */
struct protocol_hdr {
    uint8_t op;             /* Opertation type */
    uint8_t shift;          /* Number of shifts */
    uint16_t checksum;      /* Checksum of the message */
    uint32_t length;        /* Total length of the message */
};

uint16_t checksum_protocol(char *buf, size_t size);
bool verify_header(char *buf);

ssize_t send_protocol(int sock_fd, char *buf);
ssize_t recv_until(int sock_fd, char *buf, size_t len);

#endif /* STRING_ENCRYPTION_SERVICE_PROTOCOL_H */
