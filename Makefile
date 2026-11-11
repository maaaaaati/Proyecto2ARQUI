# Makefile — benchmarks del proyecto gem5 GEMM
#   make          compila las versiones para gem5 (ROI activa) y para QEMU
#   make test     valida todo en QEMU (escalar + SVE con 4 longitudes vectoriales)
#   make clean    borra los binarios
#
# Ruta a la copia de gem5 (cámbiala con: make GEM5=/otra/ruta)
GEM5    ?= $(HOME)/gem5

CC      := aarch64-linux-gnu-gcc
CFLAGS  := -O2 -fno-tree-vectorize -static -Wall
SVEFLAG := -march=armv8-a+sve
M5INC   := -I$(GEM5)/include
M5LIB   := $(GEM5)/util/m5/build/arm64/out/libm5.a

BIN     := bin
PROGS   := gemm_scalar gemm_sve

# bin/gem5/*: con m5_reset_stats/m5_dump_stats -> SOLO para gem5
# bin/qemu/*: sin instrucciones m5 -> para validar en QEMU
GEM5_BINS := $(addprefix $(BIN)/gem5/,$(PROGS))
QEMU_BINS := $(addprefix $(BIN)/qemu/,$(PROGS))

all: $(GEM5_BINS) $(QEMU_BINS)

$(BIN)/gem5 $(BIN)/qemu:
	mkdir -p $@

$(M5LIB):
	@echo "Falta $(M5LIB). Compílala con: cd $(GEM5)/util/m5 && scons build/arm64/out/m5"
	@false

# --- versiones para gem5 (ROI activa) ---
$(BIN)/gem5/gemm_scalar: src/gemm_scalar.c $(M5LIB) | $(BIN)/gem5
	$(CC) $(CFLAGS) -DUSE_M5 $(M5INC) $< -o $@ $(M5LIB) -lm

$(BIN)/gem5/gemm_sve: src/gemm_sve.c $(M5LIB) | $(BIN)/gem5
	$(CC) $(CFLAGS) $(SVEFLAG) -DUSE_M5 $(M5INC) $< -o $@ $(M5LIB) -lm

# --- versiones para QEMU (sin ROI) ---
$(BIN)/qemu/gemm_scalar: src/gemm_scalar.c | $(BIN)/qemu
	$(CC) $(CFLAGS) -fopt-info-vec $< -o $@ -lm

$(BIN)/qemu/gemm_sve: src/gemm_sve.c | $(BIN)/qemu
	$(CC) $(CFLAGS) $(SVEFLAG) $< -o $@ -lm

test: $(QEMU_BINS)
	@for n in 16 64 128; do qemu-aarch64 $(BIN)/qemu/gemm_scalar $$n || exit 1; done
	@for vl in 16 32 64 128; do for n in 16 64 128; do \
	  qemu-aarch64 -cpu max,sve-default-vector-length=$$vl $(BIN)/qemu/gemm_sve $$n || exit 1; \
	done; done
	@echo "Todas las pruebas pasaron."

clean:
	rm -rf $(BIN)

.PHONY: all test clean
