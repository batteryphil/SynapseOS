# PRIME Moment Attention: Zero-Dependency C99 & Cosmopolitan APE

A standalone, zero-dependency C99 implementation of **PRIME Moment Attention** (constant-state 2nd-order Taylor polynomial recurrent attention), featuring:
- **Tiled SIMD Recurrence**: Outer-product register tiling inspired by Justine Tunney's `jart/matmul`.
- **Embedded OpenAI-Compatible REST Server**: Single-file HTTP/1.1 streaming server inspired by `redbean`.
- **Zero-Copy `mmap` Weight Bundling**: Page-aligned PKZIP weight loader inspired by `jart/zipalign` and `llamafile`.
- **Cosmopolitan Libc / APE support**: Build as an **Actually Portable Executable** (`prime.com`) that runs natively on Linux (x86_64, aarch64), macOS (x86_64, Apple Silicon), and Windows with zero external runtime.

---

## Performance & Memory Profile

Benchmarked on host CPU with $H=8$ attention heads, head dimension $D=64$ (total hidden dim 512), $\lambda=0.9995$:

| Metric | Measured Value | Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Recurrent State Memory** | **262.03 KB** (flat) | $\mathcal{O}(1)$ | $(2D^2 + 3D + 1) \times H \times 4$ bytes. Strictly constant from 1 to 10,000,000+ tokens. |
| **Decode Throughput** | **~55,170 tokens/sec** | $\mathcal{O}(1)$ | Single CPU thread, 2-way register-tiled native C99 execution |
| **Decode Step Latency** | **17.95–18.12 µs / token** | $\mathcal{O}(1)$ | Flat latency: step 2,000 (18.2 µs) vs step 10,000 (17.95 µs) |
| **Prefill Throughput** | **~46,500 tokens/sec** | $\mathcal{O}(L)$ | Sequential causal prefill |
| **External Dependencies** | **0** | - | Pure C99 standard library (`-lm` only) |

---

## Three Key Technologies (Inspired by Justine Tunney)

### 1. Register-Tiled SIMD Recurrence (`prime_moment.c`)
- Uses register blocking across outer products ($\mathbf{k}_t \mathbf{v}_t^\top$ and $(\mathbf{k}_t \odot \mathbf{k}_t) \mathbf{v}_t^\top$).
- Input value vector $\mathbf{v}_t[e]$ is loaded once per tile and broadcast across state rows, eliminating 50% of redundant memory loads.
- State matrices $S_1$ and $S_2$ operate within the CPU's L2 cache (262 KB total for 8 heads), allowing continuous non-evicted SIMD execution.

### 2. Embedded OpenAI-Compatible REST Server (`prime_server.c`)
- Built directly into `prime` and `prime.com` using zero-dependency POSIX sockets.
- Start with:
  ```bash
  ./bin/prime --server --port 8080
  # Or with Cosmopolitan APE:
  ./bin/prime.com --server --port 8080
  ```
- **Supported Endpoints**:
  - `GET /health`: Engine status, version, and constant $O(1)$ state memory size.
  - `GET /v1/models`: OpenAI model discovery listing `prime-moment-v2`.
  - `POST /v1/chat/completions`: Full OpenAI chat completions endpoint.
    - Supports `stream: false` (standard JSON completion).
    - Supports `stream: true` (Server-Sent Events streaming with per-step latency telemetry).
  - Handles `OPTIONS` with CORS headers (`Access-Control-Allow-Origin: *`) for browser-based Web UIs.

### 3. Page-Aligned Weight Bundling (`zipalign.c` & `prime_weights.c`)
- Compiles a dedicated `zipalign` tool (`bin/zipalign`) to append uncompressed model weights to the executable.
- Local ZIP headers are padded so tensor data begins at exact **4096-byte page boundaries**.
- At runtime, `prime_weights_mmap_embedded()` locates the embedded ZIP payload and calls `mmap()`:
  - **Zero RAM Duplication**: Weights are mapped directly from disk into CPU/GPU address space.
  - **Zero Startup Latency**: Instantaneous loading without parsing or copying multi-megabyte/gigabyte weight matrices.

---

## Building

```bash
cd c

# Build native binary, Cosmopolitan APE, shared library, and zipalign tool
make all

# Run self-verification suite (verifies numerical stability & zero NaNs/Infs)
make test

# Run 10,000-step streaming decode benchmark
make bench

# Test zipalign and zero-copy mmap weight bundling
make test-bundle
```

---

## CLI Usage

### Benchmark & Diagnostics
```bash
# View all flags
./bin/prime --help

# Run 50,000-step decode benchmark
./bin/prime --heads 8 --dim 64 --tokens 50000 --decay 0.9995

# Enable QK LayerNorm
./bin/prime --heads 16 --dim 64 --tokens 10000 --qk-norm
```

### Starting the REST API Server
```bash
# Start server on port 8080
./bin/prime --server --port 8080

# In another terminal:
# 1. Health check
curl http://localhost:8080/health

# 2. Query models
curl http://localhost:8080/v1/models

# 3. Stream completions via SSE
curl -N -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "prime-moment-v2", "max_tokens": 20, "stream": true}'
```

### Packaging Self-Contained Model Binaries
```bash
# Append model weights to prime.com with 4KB page alignment
./bin/zipalign -a 4096 bin/prime.com model_weights.bin weights.bin

# Test zero-copy mmap from the single-file executable
./bin/prime.com --test-mmap weights.bin
```
