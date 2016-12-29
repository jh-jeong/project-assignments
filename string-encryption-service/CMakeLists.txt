cmake_minimum_required(VERSION 3.6)
project(string_encryption_service)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES
    client.c
    server.c
    server_select.c protocol.h protocol.c)

add_executable(string_encryption_service ${SOURCE_FILES})