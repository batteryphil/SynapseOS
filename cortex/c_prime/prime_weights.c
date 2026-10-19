/*
 * PRIME Moment Attention: Embedded Model Weight mmap Loader
 * =========================================================
 * Zero-copy memory-mapping of page-aligned weights from executable zip container.
 */

#define _POSIX_C_SOURCE 200809L

#include "prime_weights.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>

#define ZIP_EOCD_SIG 0x06054b50
#define ZIP_CENTRAL_SIG 0x02014b50
#define ZIP_LOCAL_SIG 0x04034b50

static uint16_t read_u16(const uint8_t *p) {
    return (uint16_t)(p[0] | (p[1] << 8));
}

static uint32_t read_u32(const uint8_t *p) {
    return (uint32_t)(p[0] | (p[1] << 8) | (p[2] << 16) | (p[3] << 24));
}

int prime_weights_mmap_embedded(
    const char *self_path,
    const char *entry_name,
    prime_weight_bundle_t *bundle
) {
    if (!bundle) return 1;
    memset(bundle, 0, sizeof(*bundle));

    const char *path = self_path;
    if (!path || access(path, R_OK) != 0) {
        path = "/proc/self/exe";
    }

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        perror("open executable for embedded weights");
        return 1;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("fstat executable");
        close(fd);
        return 1;
    }

    size_t file_size = (size_t)st.st_size;
    if (file_size < 22) {
        close(fd);
        return 1;
    }

    /* Scan backwards from end of file for EOCD record (up to 64KB) */
    size_t scan_len = (file_size < 65536) ? file_size : 65536;
    off_t scan_start = (off_t)(file_size - scan_len);

    uint8_t *scan_buf = (uint8_t*)malloc(scan_len);
    if (!scan_buf) {
        close(fd);
        return 1;
    }

    if (lseek(fd, scan_start, SEEK_SET) < 0 ||
        read(fd, scan_buf, scan_len) != (ssize_t)scan_len) {
        free(scan_buf);
        close(fd);
        return 1;
    }

    off_t eocd_pos = -1;
    for (ssize_t i = (ssize_t)scan_len - 22; i >= 0; i--) {
        if (read_u32(scan_buf + i) == ZIP_EOCD_SIG) {
            eocd_pos = scan_start + i;
            break;
        }
    }

    if (eocd_pos < 0) {
        free(scan_buf);
        close(fd);
        return 2; /* No ZIP archive attached */
    }

    size_t eocd_offset_in_buf = (size_t)(eocd_pos - scan_start);
    uint32_t cd_size = read_u32(scan_buf + eocd_offset_in_buf + 12);
    uint32_t cd_offset = read_u32(scan_buf + eocd_offset_in_buf + 16);
    free(scan_buf);

    /* Read Central Directory */
    uint8_t *cd_buf = (uint8_t*)malloc(cd_size);
    if (!cd_buf) {
        close(fd);
        return 1;
    }

    if (lseek(fd, (off_t)cd_offset, SEEK_SET) < 0 ||
        read(fd, cd_buf, cd_size) != (ssize_t)cd_size) {
        free(cd_buf);
        close(fd);
        return 1;
    }

    size_t target_local_offset = 0;
    size_t target_uncomp_size = 0;
    int found = 0;

    size_t cursor = 0;
    while (cursor + 46 <= cd_size) {
        if (read_u32(cd_buf + cursor) != ZIP_CENTRAL_SIG) break;

        uint16_t name_len = read_u16(cd_buf + cursor + 28);
        uint16_t extra_len = read_u16(cd_buf + cursor + 30);
        uint16_t comment_len = read_u16(cd_buf + cursor + 32);
        uint32_t uncomp_size = read_u32(cd_buf + cursor + 24);
        uint32_t local_hdr_offset = read_u32(cd_buf + cursor + 42);

        if (cursor + 46 + name_len <= cd_size) {
            char name_tmp[256];
            size_t copy_len = (name_len < 255) ? name_len : 255;
            memcpy(name_tmp, cd_buf + cursor + 46, copy_len);
            name_tmp[copy_len] = '\0';

            if (entry_name == NULL || strcmp(name_tmp, entry_name) == 0) {
                target_local_offset = local_hdr_offset;
                target_uncomp_size = uncomp_size;
                found = 1;
                break;
            }
        }
        cursor += 46 + name_len + extra_len + comment_len;
    }
    free(cd_buf);

    if (!found) {
        close(fd);
        return 3; /* Entry not found in ZIP */
    }

    /* Read Local File Header to find exact payload offset */
    uint8_t local_hdr[30];
    if (lseek(fd, (off_t)target_local_offset, SEEK_SET) < 0 ||
        read(fd, local_hdr, 30) != 30) {
        close(fd);
        return 1;
    }

    if (read_u32(local_hdr) != ZIP_LOCAL_SIG) {
        close(fd);
        return 1;
    }

    uint16_t loc_name_len = read_u16(local_hdr + 26);
    uint16_t loc_extra_len = read_u16(local_hdr + 28);

    size_t payload_offset = target_local_offset + 30 + loc_name_len + loc_extra_len;

    /* Verify page alignment (must be multiple of system page size, e.g. 4096) */
    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size <= 0) page_size = 4096;

    if (payload_offset % (size_t)page_size != 0) {
        fprintf(stderr, "Warning: Payload offset %zu is not aligned to page size %ld!\n",
                payload_offset, page_size);
        close(fd);
        return 4; /* Misaligned for direct mmap */
    }

    /* Memory-map payload with zero-copy */
    void *map = mmap(NULL, target_uncomp_size, PROT_READ, MAP_SHARED, fd, (off_t)payload_offset);
    if (map == MAP_FAILED) {
        perror("mmap embedded weights");
        close(fd);
        return 1;
    }

    bundle->fd = fd;
    bundle->file_size = file_size;
    bundle->tensor_offset = payload_offset;
    bundle->tensor_bytes = target_uncomp_size;
    bundle->mmap_ptr = map;
    bundle->weights = (const float*)map;

    return 0;
}

void prime_weights_close(prime_weight_bundle_t *bundle) {
    if (!bundle) return;
    if (bundle->mmap_ptr && bundle->tensor_bytes > 0) {
        munmap((void*)bundle->mmap_ptr, bundle->tensor_bytes);
    }
    if (bundle->fd >= 0) {
        close(bundle->fd);
    }
    memset(bundle, 0, sizeof(*bundle));
}
