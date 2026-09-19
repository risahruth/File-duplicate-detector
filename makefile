CC = gcc
CFLAGS = -Wall -Wextra -std=c11

TARGET = duplicate_detector
SOURCE = duplicate_detector.c

all:
	$(CC) $(CFLAGS) $(SOURCE) -o $(TARGET)

clean:
	rm -f $(TARGET)

