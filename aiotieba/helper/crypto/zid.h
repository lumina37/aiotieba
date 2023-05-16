#pragma once

#include "utils.h"

#define TBC_CBC_SECKEY_SIZE 16
#define TBC_RC4_SIZE 16

/**
 * @brief RC4 includes an extra XOR against 42
 *
 * @param xyusMd5Str 32 bytes. alloc and free by user
 * @param cbcSecKey 16 bytes. alloc and free by user
 * @param dst 16 bytes. alloc and free by user
 *
 * @return non 0 if any error
 *
 * @note 12.x loc: com.baidu.sofire.x6.oCOCcooCCoC.ocOOCCoOOCcC.CcooOoocOOo
 */
void tbc_rc4_42(TBC_NOESCAPE const unsigned char* xyusMd5Str, TBC_NOESCAPE const unsigned char* cbcSecKey,
                TBC_NOESCAPE unsigned char* dst);
