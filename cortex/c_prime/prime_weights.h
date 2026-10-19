/*
 * PRIME Moment Attention: Embedded Model Weight mmap Loader
 * =========================================================
 * Locates and zero-copy memory-maps page-aligned model weights directly
 * from the running binary's PKZIP payload.
 */

#ifndef PRIME_WEIGHTS_H
#define PRIME_WEIGHTS_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int fd;
    size_t file_size;
    size_t tensor_offset;
    size_t tensor_bytes;
    const void *mmap_ptr;
    const float *weights;
} prime_weight_bundle_t;

/*
 * Locates entry_name (e.g. "weights.bin") inside self_path (or /proc/self/exe),
 * checks page alignment, and memory-maps it with zero copy.
 *
 * Returns 0 on success, non-zero on failure.
 */
int prime_weights_mmap_embedded(
    const char *self_path,
    const char *entry_name,
    prime_weight_bundle_t *bundle
);

/* Unmaps memory and closes file descriptor */
void prime_weights_close(prime_weight_bundle_t *bundle);

#ifdef __cplusplus
}
#endif

#endif /* PRIME_WEIGHTS_H */
