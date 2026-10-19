/*
 * PRIME Moment Attention: Zero-Dependency zipalign
 * =================================================
 * Inspired by Justine Tunney's jart/zipalign and Android zipalign.
 *
 * Appends uncompressed files to an executable/ZIP archive, padding local headers
 * so that file contents begin at exact N-byte page boundaries (e.g. 4096 or 65536).
 * This enables zero-copy mmap() directly into GPU or CPU memory address spaces.
 */

#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>

#define ZIP_LOCAL_HEADER_SIG 0x04034b50
#define ZIP_CENTRAL_HEADER_SIG 0x02014b50
#define ZIP_EOCD_SIG 0x06054b50

static uint32_t compute_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320;
            } else {
                crc >>= 1;
            }
        }
    }
    return ~crc;
}

static void write_u16(uint8_t *buf, uint16_t val) {
    buf[0] = (uint8_t)(val & 0xFF);
    buf[1] = (uint8_t)((val >> 8) & 0xFF);
}

static void write_u32(uint8_t *buf, uint32_t val) {
    buf[0] = (uint8_t)(val & 0xFF);
    buf[1] = (uint8_t)((val >> 8) & 0xFF);
    buf[2] = (uint8_t)((val >> 16) & 0xFF);
    buf[3] = (uint8_t)((val >> 24) & 0xFF);
}

static int safe_write(int fd, const void *buf, size_t count) {
    size_t written = 0;
    while (written < count) {
        ssize_t n = write(fd, (const char*)buf + written, count - written);
        if (n <= 0) return -1;
        written += (size_t)n;
    }
    return 0;
}

int main(int argc, char **argv) {
    int alignment = 4096;
    const char *zip_path = NULL;
    const char *asset_path = NULL;
    const char *entry_name = NULL;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-a") == 0 && i + 1 < argc) {
            alignment = atoi(argv[++i]);
        } else if (!zip_path) {
            zip_path = argv[i];
        } else if (!asset_path) {
            asset_path = argv[i];
        } else if (!entry_name) {
            entry_name = argv[i];
        }
    }

    if (!zip_path || !asset_path) {
        fprintf(stderr, "Usage: %s [-a alignment] <archive.com|archive.zip> <file_to_append> [entry_name]\n", argv[0]);
        fprintf(stderr, "  -a <int>   Byte alignment for mmap (default: 4096)\n");
        return 1;
    }

    if (!entry_name) {
        /* Default entry name to basename of asset */
        const char *slash = strrchr(asset_path, '/');
        entry_name = slash ? slash + 1 : asset_path;
    }

    /* Open asset file */
    int asset_fd = open(asset_path, O_RDONLY);
    if (asset_fd < 0) {
        perror("open asset");
        return 1;
    }
    struct stat st;
    if (fstat(asset_fd, &st) < 0) {
        perror("fstat asset");
        close(asset_fd);
        return 1;
    }
    size_t asset_size = (size_t)st.st_size;
    uint8_t *asset_data = (uint8_t*)malloc(asset_size);
    if (!asset_data && asset_size > 0) {
        fprintf(stderr, "Cannot allocate %zu bytes for asset\n", asset_size);
        close(asset_fd);
        return 1;
    }
    if (read(asset_fd, asset_data, asset_size) != (ssize_t)asset_size) {
        perror("read asset");
        free(asset_data);
        close(asset_fd);
        return 1;
    }
    close(asset_fd);

    uint32_t crc = compute_crc32(asset_data, asset_size);

    /* Open archive for appending */
    int zip_fd = open(zip_path, O_RDWR | O_CREAT, 0755);
    if (zip_fd < 0) {
        perror("open zip");
        free(asset_data);
        return 1;
    }

    off_t current_len = lseek(zip_fd, 0, SEEK_END);
    uint16_t name_len = (uint16_t)strlen(entry_name);

    /*
     * Local File Header (30 bytes fixed) + name_len + extra_len
     * We want (current_len + 30 + name_len + extra_len) % alignment == 0.
     */
    size_t base_header_len = 30 + name_len;
    size_t unaligned_offset = (size_t)current_len + base_header_len;
    size_t pad = (alignment - (unaligned_offset % alignment)) % alignment;

    uint16_t extra_len = (uint16_t)pad;

    uint8_t local_hdr[30];
    write_u32(local_hdr + 0, ZIP_LOCAL_HEADER_SIG);
    write_u16(local_hdr + 4, 20);            /* Version needed: 2.0 */
    write_u16(local_hdr + 6, 0);             /* Flags */
    write_u16(local_hdr + 8, 0);             /* Compression: STORED (0) */
    write_u16(local_hdr + 10, 0);            /* Mod time */
    write_u16(local_hdr + 12, 0);            /* Mod date */
    write_u32(local_hdr + 14, crc);          /* CRC-32 */
    write_u32(local_hdr + 18, (uint32_t)asset_size); /* Comp size */
    write_u32(local_hdr + 22, (uint32_t)asset_size); /* Uncomp size */
    write_u16(local_hdr + 26, name_len);
    write_u16(local_hdr + 28, extra_len);

    uint32_t local_header_offset = (uint32_t)current_len;

    /* Write local header */
    safe_write(zip_fd, local_hdr, 30);
    safe_write(zip_fd, entry_name, name_len);

    /* Write padding into extra field */
    if (extra_len > 0) {
        uint8_t *pad_buf = (uint8_t*)calloc(1, extra_len);
        safe_write(zip_fd, pad_buf, extra_len);
        free(pad_buf);
    }

    off_t payload_offset = lseek(zip_fd, 0, SEEK_CUR);
    if ((size_t)payload_offset % alignment != 0) {
        fprintf(stderr, "Error: Alignment calculation error! Offset=%ld, align=%d\n",
                (long)payload_offset, alignment);
        close(zip_fd);
        free(asset_data);
        return 1;
    }

    /* Write asset data */
    safe_write(zip_fd, asset_data, asset_size);
    free(asset_data);

    /* Write Central Directory Header (46 bytes fixed) */
    off_t cd_offset = lseek(zip_fd, 0, SEEK_CUR);
    uint8_t cd_hdr[46];
    write_u32(cd_hdr + 0, ZIP_CENTRAL_HEADER_SIG);
    write_u16(cd_hdr + 4, 0x0314);          /* Made by: UNIX 2.0 */
    write_u16(cd_hdr + 6, 20);              /* Version needed */
    write_u16(cd_hdr + 8, 0);               /* Flags */
    write_u16(cd_hdr + 10, 0);              /* Compression: 0 */
    write_u16(cd_hdr + 12, 0);              /* Time */
    write_u16(cd_hdr + 14, 0);              /* Date */
    write_u32(cd_hdr + 16, crc);
    write_u32(cd_hdr + 20, (uint32_t)asset_size);
    write_u32(cd_hdr + 24, (uint32_t)asset_size);
    write_u16(cd_hdr + 28, name_len);
    write_u16(cd_hdr + 30, 0);              /* Extra field len */
    write_u16(cd_hdr + 32, 0);              /* File comment len */
    write_u16(cd_hdr + 34, 0);              /* Disk start */
    write_u16(cd_hdr + 36, 0);              /* Internal attrs */
    write_u32(cd_hdr + 38, 0100644 << 16);  /* External attrs: regular file */
    write_u32(cd_hdr + 42, local_header_offset);

    safe_write(zip_fd, cd_hdr, 46);
    safe_write(zip_fd, entry_name, name_len);

    /* Write End of Central Directory (EOCD) (22 bytes) */
    size_t cd_size = 46 + name_len;
    uint8_t eocd[22];
    write_u32(eocd + 0, ZIP_EOCD_SIG);
    write_u16(eocd + 4, 0);                 /* Disk number */
    write_u16(eocd + 6, 0);                 /* Start disk */
    write_u16(eocd + 8, 1);                 /* Records on this disk */
    write_u16(eocd + 10, 1);                /* Total records */
    write_u32(eocd + 12, (uint32_t)cd_size);/* Central directory size */
    write_u32(eocd + 16, (uint32_t)cd_offset); /* Central directory offset */
    write_u16(eocd + 20, 0);                /* Comment len */

    safe_write(zip_fd, eocd, 22);
    close(zip_fd);

    printf("[zipalign] Successfully appended '%s' to '%s'\n", entry_name, zip_path);
    printf("  Alignment       : %d bytes\n", alignment);
    printf("  Payload Offset  : %ld bytes (Offset %% %d == 0 -> Zero-Copy mmap verified)\n",
           (long)payload_offset, alignment);
    printf("  Payload Size    : %zu bytes (%.2f KB)\n", asset_size, (double)asset_size / 1024.0);

    return 0;
}
