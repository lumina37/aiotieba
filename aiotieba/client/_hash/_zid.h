#pragma once

#include <stdlib.h>  // malloc free
#include <stdbool.h> // bool
#include <memory.h>  // memset memcpy

#include "_const.h"

#define TBH_SECKEY_SIZE 16
#define TBH_INV_RC4_SIZE 16

/**
 * @brief seems to be a variety of RC4
 *
 * @param dst 16 bytes. alloc and free by user
 * @param secKey 16 bytes. alloc and free by user
 * @param xyusMd5 32 bytes. alloc and free by user
 *
 * @return false if any error
 *
 * @note 9.1 loc: com.baidu.sofire.i.h.a
 */
bool tbh_invRC4(char *dst, const char *secKey, const char *xyusMd5);
