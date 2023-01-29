#pragma once

#include <stdlib.h>  // malloc free
#include <stdbool.h> // bool
#include <memory.h>  // memset memcpy

#include "crc32.h"
#include "xxhash.h"
#include "base32.h"
#include "WjCryptLib_Md5.h"
#include "WjCryptLib_Sha1.h"

static const char CUID2_PERFIX[] = {'c', 'o', 'm', '.', 'b', 'a', 'i', 'd', 'u'};
static const char CUID3_PERFIX[] = {'c', 'o', 'm', '.', 'h', 'e', 'l', 'i', 'o', 's'};

#define TBH_UUID_SIZE 36
#define TBH_ANDROID_ID_SIZE 16
#define TBH_MD5_STR_SIZE (MD5_HASH_SIZE * 2)
#define TBH_SHA1_HEX_SIZE (SHA1_HASH_SIZE * 2)
#define TBH_SHA1_BASE32_SIZE (BASE32_LEN(SHA1_HASH_SIZE))
#define TBH_HELIOS_HASH_SIZE 5
#define TBH_HELIOS_BASE32_SIZE (BASE32_LEN(TBH_HELIOS_HASH_SIZE))
#define TBH_CUID_GALAXY2_SIZE (TBH_MD5_STR_SIZE + 2 + TBH_HELIOS_BASE32_SIZE)
#define TBH_C3_AID_SIZE (4 + TBH_SHA1_BASE32_SIZE + 1 + TBH_HELIOS_BASE32_SIZE)

/**
 * @brief impl of TiebaLite tieba/post/utils/helios
 *
 * @param dst 5 bytes. alloc and free by user
 * @param src alloc and free by user
 * @param srcSize size of src. must >= 1
 *
 * @return false if any error
 *
 * @note 12.x loc: com.baidu.tieba.l40.a / com.baidu.tieba.pz.a
 */
bool tbh_heliosHash(char *dst, const char *src, size_t srcSize);

/**
 * @brief compute `cuid_galaxy2`
 *
 * @param dst 42 bytes. alloc and free by user
 * @param androidID 16 bytes. alloc and free by user
 *
 * @return false if any error
 *
 * @note 12.x loc: com.baidu.tieba.oz.m
 */
bool tbh_cuid_galaxy2(char *dst, const char *androidID);

/**
 * @brief compute `c3_aid`
 *
 * @param dst 45 bytes. alloc and free by user
 * @param androidID 16 bytes. alloc and free by user
 * @param uuid 36 bytes. alloc and free by user
 *
 * @return false if any error
 *
 * @note 12.x loc: com.baidu.tieba.r50.f
 */
bool tbh_c3_aid(char *dst, const char *androidID, const char *uuid);
