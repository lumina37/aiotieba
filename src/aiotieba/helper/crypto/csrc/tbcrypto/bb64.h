#pragma once

/**
 * @brief variant base64 encode. the result is padded with a marker ('A' 'B' 'C' for 0 1 2 trailing bytes) and a '\0'
 *
 * @param inputArray alloc and free by user
 * @param srcLen size of inputArray
 * @param mode alphabet offset. 0 in current usage
 * @param dst 4 * ((srcLen + 2) / 3) + 2 bytes. alloc and free by user
 *
 * @note 22.11 loc: com.baidu.util.Base64Encoder#nativeB64Encode (libbase64encoder_v2_0.so)
 */
void tbc_BB64Encode(const unsigned char* inputArray, int srcLen, int mode, unsigned char* dst);
