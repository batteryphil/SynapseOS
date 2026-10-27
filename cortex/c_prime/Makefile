CC ?= gcc
CFLAGS ?= -O3 -mtune=generic -fopenmp-simd -funroll-loops -fno-math-errno -fno-trapping-math -Wall -Wextra -std=c99
LDFLAGS ?= -lm


COSMOCC ?= $(shell command -v cosmocc 2>/dev/null || echo "/home/phil/.gemini/antigravity/scratch/cosmocc/bin/cosmocc")
COSMO_CFLAGS ?= -O3 -Wall -Wextra -std=c99
COSMO_LDFLAGS ?=

FILCC ?= /home/phil/.gemini/antigravity/scratch/fil-c/build/bin/filcc
FILC_COSMO_CFLAGS ?= --filc-cosmo --filc-ape -O2 -Wall -Wextra

TMPDIR ?= /tmp

BIN_DIR := bin
SRC := prime_moment.c prime_gtrm.c prime_buckingham.c prime_server.c prime_weights.c prime_net.c synapse_sim_core.c main.c
HEADERS := prime_moment.h prime_gtrm.h prime_buckingham.h prime_server.h prime_weights.h prime_net.h synapse_sim_core.h

.PHONY: all native cosmo filc-cosmo shared zipalign test test-bundle bench clean help

all: native shared cosmo filc-cosmo zipalign

native: $(BIN_DIR)/prime

$(BIN_DIR)/prime: $(SRC) $(HEADERS)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ $(SRC) $(LDFLAGS)
	@echo "Built native binary: $@"

zipalign: $(BIN_DIR)/zipalign

$(BIN_DIR)/zipalign: zipalign.c
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ zipalign.c
	@echo "Built zipalign tool: $@"

shared: $(BIN_DIR)/libprime.so $(BIN_DIR)/libsynapse_core.so

$(BIN_DIR)/libprime.so: prime_moment.c synapse_sim_core.c $(HEADERS)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -fPIC -shared -o $@ prime_moment.c synapse_sim_core.c $(LDFLAGS)
	@echo "Built shared library: $@"

$(BIN_DIR)/libsynapse_core.so: prime_moment.c synapse_sim_core.c $(HEADERS)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -fPIC -shared -o $@ prime_moment.c synapse_sim_core.c $(LDFLAGS)
	@echo "Built C99 simulation & PRIME shared library: $@"

cosmo: $(BIN_DIR)/prime.com $(BIN_DIR)/synapse_core.com

$(BIN_DIR)/prime.com: $(SRC) $(HEADERS)
	@mkdir -p $(BIN_DIR)
	$(COSMOCC) $(COSMO_CFLAGS) -o $@ $(SRC) $(COSMO_LDFLAGS)
	@echo "Built Cosmopolitan APE binary: $@"

$(BIN_DIR)/synapse_core.com: synapse_cosmo_bench.c prime_moment.c synapse_sim_core.c $(HEADERS)
	@mkdir -p $(BIN_DIR)
	$(COSMOCC) $(COSMO_CFLAGS) -o $@ synapse_cosmo_bench.c prime_moment.c synapse_sim_core.c $(COSMO_LDFLAGS)
	@echo "Built Cosmopolitan APE C99 Core Engine: $@"

filc-cosmo: $(BIN_DIR)/synapse_core_filc.com

$(BIN_DIR)/synapse_core_filc.com: synapse_cosmo_bench.c prime_moment.c synapse_sim_core.c $(HEADERS)
	@mkdir -p $(BIN_DIR)
	$(FILCC) $(FILC_COSMO_CFLAGS) -o $@ synapse_cosmo_bench.c prime_moment.c synapse_sim_core.c -lm
	@echo "Built Memory-Safe Fil-C Cosmopolitan APE: $@"

$(BIN_DIR)/zipalign.com: zipalign.c
	@mkdir -p $(BIN_DIR)
	$(COSMOCC) $(COSMO_CFLAGS) -o $@ zipalign.c
	@echo "Built Cosmopolitan APE zipalign tool: $@"

cosmo-bundle: $(BIN_DIR)/prime.com $(BIN_DIR)/zipalign.com
	@echo "Creating dummy weights for bundling..."
	@python3 -c "import struct; f=open('$(BIN_DIR)/dummy_weights.bin','wb'); f.write(struct.pack('4f', 0.1234, 0.5678, 0.9012, 0.3456)); f.close()"
	@cp $(BIN_DIR)/prime.com $(BIN_DIR)/prime_bundled.com
	TMPDIR=$$(pwd)/../tmp HOME=$$(pwd)/../tmp sh $(BIN_DIR)/zipalign.com -a 4096 $(BIN_DIR)/prime_bundled.com $(BIN_DIR)/dummy_weights.bin weights.bin
	@echo "Testing bundled APE..."
	TMPDIR=$$(pwd)/../tmp HOME=$$(pwd)/../tmp sh $(BIN_DIR)/prime_bundled.com --test-mmap weights.bin

test: native
	$(BIN_DIR)/prime --verify

test-bundle: native zipalign
	@python3 -c "import struct; f=open('bin/dummy_weights.bin','wb'); f.write(struct.pack('4f', 0.1234, 0.5678, 0.9012, 0.3456)); f.close()"
	@cp $(BIN_DIR)/prime $(BIN_DIR)/prime_bundled
	$(BIN_DIR)/zipalign -a 4096 $(BIN_DIR)/prime_bundled bin/dummy_weights.bin weights.bin
	$(BIN_DIR)/prime_bundled --test-mmap weights.bin

bench: native
	$(BIN_DIR)/prime --heads 8 --dim 64 --tokens 10000

clean:
	rm -rf $(BIN_DIR) *.o

help:
	@echo "Available targets:"
	@echo "  make native  - Build native binary using host GCC"
	@echo "  make cosmo   - Build portable .com binary using Cosmopolitan cosmocc"
	@echo "  make test    - Run self-verification tests"
	@echo "  make bench   - Run benchmark with 10k tokens"
	@echo "  make clean   - Remove build artifacts"
