CC = gcc
CFLAGS = -Wall -Werror -Wextra -std=c11 -Wno-format-truncation -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE
TARGET = sws
OBJS = sws.o request.o response.o cgi.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

%.o: %.c sws.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(TARGET) $(OBJS) *.log

test: $(TARGET)
	chmod +x test_server.sh cgi-bin/*.cgi
	./test_server.sh

.PHONY: all clean test
