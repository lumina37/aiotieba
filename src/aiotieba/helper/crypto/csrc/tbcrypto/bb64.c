#include <stdint.h>
#include <string.h>

#include "tbcrypto/bb64.h"

// variant base64 alphabet, completely different from the standard one
static const unsigned char BB64_ALPHABET[] = "qogjOuCRNkfil5p4SQ3LAmxGKZTdesvB6z_YPahMI9t80rJyHW1DEwFbc7nUVX2-";

// seed used by the 32bit word obfuscation
#define BB64_SEED 758653732u

#define BB64_BYTES_PER_GROUP 3
#define BB64_CHARS_PER_GROUP 4

static uint32_t bb64_rotr(uint32_t value, unsigned int bits) { return (value >> bits) | (value << (32u - bits)); }

static uint32_t bb64_key(int mode) {
    const uint32_t rotated = bb64_rotr((uint32_t)mode, 5);
    return rotated ^ (BB64_SEED << (rotated & 0xFu));
}

static unsigned int bb64_mixed_byte(const unsigned char* src, int srcLen, uint32_t key, int index) {
    const unsigned int shift = ((unsigned int)index & 3u) * 8u;

    if (index < (srcLen & ~3)) {
        uint32_t word;
        memcpy(&word, src + (index & ~3), sizeof(word));
        return ((key ^ bb64_rotr(word, 3)) >> shift) & 0xFFu;
    }
    return ((unsigned int)src[index] ^ (key >> shift)) & 0xFFu;
}

static void bb64_encode_group(unsigned int b0, unsigned int b1, unsigned int b2, unsigned int tableOffset,
                              unsigned char* dst) {
    const unsigned int lastSextet = ((b0 >> 6) << 4) | ((b1 >> 6) << 2) | (b2 >> 6);

    dst[0] = BB64_ALPHABET[((b0 & 0x3Fu) + tableOffset) & 0x3Fu];
    dst[1] = BB64_ALPHABET[((b1 & 0x3Fu) + tableOffset) & 0x3Fu];
    dst[2] = BB64_ALPHABET[((b2 & 0x3Fu) + tableOffset) & 0x3Fu];
    dst[3] = BB64_ALPHABET[(lastSextet + tableOffset) & 0x3Fu];
}

void tbc_BB64Encode(const unsigned char* inputArray, int srcLen, int mode, unsigned char* dst) {
    const uint32_t key = bb64_key(mode);
    const unsigned int tableOffset = (unsigned int)mode & 0x3Fu;

    if (srcLen <= 0) {
        dst[0] = 0;
        dst[1] = 0;
        return;
    }

    int index = 0;
    for (; index + BB64_BYTES_PER_GROUP <= srcLen; index += BB64_BYTES_PER_GROUP, dst += BB64_CHARS_PER_GROUP) {
        bb64_encode_group(bb64_mixed_byte(inputArray, srcLen, key, index),
                          bb64_mixed_byte(inputArray, srcLen, key, index + 1),
                          bb64_mixed_byte(inputArray, srcLen, key, index + 2), tableOffset, dst);
    }

    // the trailing bytes are zero-padded to a complete group
    // the client leaves these padding bytes UB, which only matters when srcLen % 3 != 0
    if (index < srcLen) {
        const unsigned int b0 = bb64_mixed_byte(inputArray, srcLen, key, index);
        const unsigned int b1 = (index + 1 < srcLen) ? bb64_mixed_byte(inputArray, srcLen, key, index + 1) : 0u;
        const unsigned int b2 = (index + 2 < srcLen) ? bb64_mixed_byte(inputArray, srcLen, key, index + 2) : 0u;
        bb64_encode_group(b0, b1, b2, tableOffset, dst);
        dst += BB64_CHARS_PER_GROUP;
    }

    dst[0] = (unsigned char)('A' + srcLen % BB64_BYTES_PER_GROUP);
    dst[1] = 0;
}
