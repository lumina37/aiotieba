#pragma once


#define BB64_LEN(len) (4 * ((len + 2) / 3u) + 1)

void tbc_BB64Encode(unsigned char *inputArray, int srcLen, int mode, unsigned char *dst);