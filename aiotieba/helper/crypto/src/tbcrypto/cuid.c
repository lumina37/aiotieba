#include <memory.h>  // memset memcpy
#include <stdbool.h> // bool

#include "base32/base32.h"
#include "crc/crc32.h"
#include "mbedtls/md5.h"
#include "mbedtls/sha1.h"

#define XXH_INLINE_ALL
#include "xxHash/xxhash.h"

#include "tbcrypto/const.h"
#include "tbcrypto/error.h"

#include "tbcrypto/cuid.h"

#define HASHER_NUM 4
#define STEP_SIZE 5
#define HASH_SIZE_IN_BIT 32

static const char CUID2_PERFIX[] = {'c', 'o', 'm', '.', 'b', 'a', 'i', 'd', 'u'};
static const char CUID3_PERFIX[] = {'c', 'o', 'm', '.', 'h', 'e', 'l', 'i', 'o', 's'};

static inline void __tbc_update(uint64_t* sec, uint64_t hashVal, uint64_t start, bool flag)
{
    uint64_t end = start + HASH_SIZE_IN_BIT;
    uint64_t secTemp = *sec;
    uint64_t var9 = ((uint64_t)1 << end) - 1;
    uint64_t var5 = (var9 & *sec) >> start;

    if (flag) {
        var5 ^= hashVal;
    } else {
        var5 &= hashVal;
    }

    for (uint64_t i = 0; i < HASH_SIZE_IN_BIT; i++) {
        uint64_t opIdx = start + i;
        if (var5 & (uint64_t)1 << i) {
            secTemp |= (uint64_t)1 << opIdx;
        } else {
            secTemp &= ~((uint64_t)1 << opIdx);
        }
    }

    *sec = secTemp;
}

static inline void __tbc_writeBuffer(unsigned char* buffer, const uint64_t sec)
{
    uint64_t tmpSec = sec;
    for (uint64_t i = 0; i < STEP_SIZE; i++) {
        buffer[i] = (unsigned char)((uint64_t)UINT8_MAX & tmpSec);
        tmpSec >>= 8;
    }
}

void tbc_heliosHash(const unsigned char* src, size_t srcSize, unsigned char* dst)
{
    // init
    uint32_t crc32Val;
    uint32_t xxhash32Val;
    uint64_t sec = ((uint64_t)1 << 40) - 1; // equals to `-1L>>>-40L` in java
    unsigned char buffer[HASHER_NUM * STEP_SIZE];
    memset(buffer, -1, STEP_SIZE); // Now buffer is [-1 * 5, ...]

    // 1st hash with CRC32
    crc32Val = tbc_crc32(src, srcSize, 0);
    crc32Val = tbc_crc32(buffer, STEP_SIZE, crc32Val);
    __tbc_update(&sec, (uint64_t)crc32Val, 8, false);
    __tbc_writeBuffer(buffer + STEP_SIZE, sec); // Now buffer is [-1 * 5, crcrc, ...]

    // 2nd hash with xxHash32
    XXH32_state_t xxState4StepTwo, xxState4StepThree;
    XXH32_reset(&xxState4StepTwo, 0);
    XXH32_update(&xxState4StepTwo, src, srcSize);
    XXH32_update(&xxState4StepTwo, buffer, STEP_SIZE * 2);
    XXH32_copyState(&xxState4StepThree, &xxState4StepTwo);
    xxhash32Val = XXH32_digest(&xxState4StepTwo);
    __tbc_update(&sec, xxhash32Val, 0, true);
    __tbc_writeBuffer(buffer + STEP_SIZE * 2, sec); // Now buffer is [-1[5], crc[5], xxxxx, ...]

    // 3rd hash with xxHash32
    XXH32_update(&xxState4StepThree, buffer + STEP_SIZE * 2, STEP_SIZE);
    xxhash32Val = XXH32_digest(&xxState4StepThree);
    __tbc_update(&sec, xxhash32Val, 1, true);
    __tbc_writeBuffer(buffer + STEP_SIZE * 3, sec); // Now buffer is [-1[5], crc[5], xx[5], xx[5]]

    // 4th hash with CRC32
    crc32Val = tbc_crc32(buffer + STEP_SIZE, STEP_SIZE * 3, crc32Val);
    __tbc_update(&sec, crc32Val, 7, true);

    // write to dst
    __tbc_writeBuffer(dst, sec);
}

void tbc_cuid_galaxy2(const unsigned char* androidID, unsigned char* dst)
{
    // step 1: build src buffer and compute md5
    unsigned char md5Buffer[sizeof(CUID2_PERFIX) + TBC_ANDROID_ID_SIZE];

    size_t buffOffset = 0;
    memcpy(md5Buffer, CUID2_PERFIX, sizeof(CUID2_PERFIX));
    buffOffset += sizeof(CUID2_PERFIX);
    memcpy(md5Buffer + buffOffset, androidID, TBC_ANDROID_ID_SIZE);

    unsigned char md5[TBC_MD5_HASH_SIZE];
    mbedtls_md5(md5Buffer, sizeof(md5Buffer), md5);

    // step 2: assign md5 hex to dst
    // dst will be [md5 hex, ...]
    size_t dstOffset = 0;
    for (size_t imd5 = 0; imd5 < TBC_MD5_HASH_SIZE; imd5++) {
        dst[dstOffset] = HEX_UPPERCASE_TABLE[md5[imd5] >> 4];
        dstOffset++;
        dst[dstOffset] = HEX_UPPERCASE_TABLE[md5[imd5] & 0x0F];
        dstOffset++;
    }

    // step 3: add joining char
    // dst will be [md5 hex, '|V', ...]
    dst[dstOffset] = '|';
    dstOffset++;
    dst[dstOffset] = 'V';
    dstOffset++;

    // step 4: build dst buffer and compute helios hash
    unsigned char heHash[TBC_HELIOS_HASH_SIZE];
    tbc_heliosHash(dst, TBC_MD5_STR_SIZE, heHash);

    // step 5: assign helios base32 to dst
    // dst will be [md5 hex, '|V', heliosHash base32]
    tbc_base32_encode(heHash, TBC_HELIOS_HASH_SIZE, (dst + dstOffset));
}

void tbc_c3_aid(const unsigned char* androidID, const unsigned char* uuid, unsigned char* dst)
{
    // step 1: set perfix
    // dst will be ['A00-', ...]
    dst[0] = 'A';
    dst[1] = '0';
    dst[2] = '0';
    dst[3] = '-';
    size_t dstOffset = 4;

    // step 2: build src buffer and compute sha1
    unsigned char sha1Buffer[sizeof(CUID3_PERFIX) + TBC_ANDROID_ID_SIZE + TBC_UUID_SIZE];

    size_t sha1BuffOffset = 0;
    memcpy(sha1Buffer, CUID3_PERFIX, sizeof(CUID3_PERFIX));
    sha1BuffOffset += sizeof(CUID3_PERFIX);
    memcpy(sha1Buffer + sha1BuffOffset, androidID, TBC_ANDROID_ID_SIZE);
    sha1BuffOffset += TBC_ANDROID_ID_SIZE;
    memcpy(sha1Buffer + sha1BuffOffset, uuid, TBC_UUID_SIZE);

    unsigned char sha1[TBC_SHA1_HASH_SIZE];
    mbedtls_sha1(sha1Buffer, sizeof(sha1Buffer), sha1);

    // step 3: compute sha1 base32 and assign
    // dst will be ['A00-', sha1 base32, ...]
    tbc_base32_encode(sha1, TBC_SHA1_HASH_SIZE, (dst + dstOffset));
    dstOffset += TBC_SHA1_BASE32_SIZE;

    // step 4: add joining char
    // dst will be ['A00-', sha1 base32, '-', ...]
    dst[dstOffset] = '-';
    dstOffset++;

    // step 5: build dst buffer and compute helios hash
    unsigned char heHash[TBC_HELIOS_HASH_SIZE];
    tbc_heliosHash(dst, dstOffset, heHash);

    // step 6: assign helios base32 to dst
    // dst will be ['A00-', sha1 base32, '-', heliosHash base32]
    tbc_base32_encode(heHash, TBC_HELIOS_HASH_SIZE, (dst + dstOffset));
}
