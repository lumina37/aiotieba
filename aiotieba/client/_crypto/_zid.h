#pragma once

#define TBH_CBC_SECKEY_SIZE 16
#define TBH_RC4_SIZE 16

/**
 * @brief RC4 includes an extra XOR against 42
 *
 * @param dst 16 bytes. alloc and free by user
 * @param xyusMd5 16 bytes. alloc and free by user
 * @param cbcSecKey 16 bytes. alloc and free by user
 *
 * @return non 0 if any error
 *
 * @note 12.x loc: com.baidu.sofire.x6.oCOCcooCCoC.ocOOCCoOOCcC.CcooOoocOOo
 */
int tbh_rc4_42(char *dst, const char *xyusMd5, const char *cbcSecKey);
