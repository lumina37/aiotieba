#pragma once

#include <stdlib.h>  // malloc free
#include <stdbool.h> // bool
#include <memory.h>  // memset memcpy

#include "_error.h"
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
 * @return non 0 if any error
 *
 * @note 12.x loc: com.baidu.sofire.x6.oCOCcooCCoC.ocOOCCoOOCcC.CcooOoocOOo
 */
int tbh_invRC4(char *dst, const char *secKey, const char *xyusMd5);
