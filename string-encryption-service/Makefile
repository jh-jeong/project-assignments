# the compiler: gcc for C program, define as g++ for C++
CC = gcc

# compiler flags:
#  -g    adds debugging information to the executable file
#  -Wall turns on most, but not all, compiler warnings
CFLAGS  = -g -Wall

all: client server

client: client.c protocol.c
	$(CC) $(CFLAGS) -o client client.c protocol.c

server: server.c protocol.c
	$(CC) $(CFLAGS) -o server server.c protocol.c

clean:
	$(RM) client server

