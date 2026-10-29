.PHONY: all clean test

all:
	$(MAKE) -C sws all

clean:
	$(MAKE) -C sws clean

test:
	$(MAKE) -C sws test
