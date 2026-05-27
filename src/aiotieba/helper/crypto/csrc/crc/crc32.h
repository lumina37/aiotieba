/*
** The crc32 is licensed under the Apache License, Version 2.0, and a copy of the license is included in this file.
**
** Author: Wang Yaofu voipman@qq.com
** Description: The source file of class crc32.
**  CRC32 implementation according to IEEE standards.
**  Polynomials are represented in LSB-first form
**  following parameters:
**    Width                      : 32 bit
**    Poly                       : 0xEDB88320
**    Output for "123456789"     : 0xCBF43926
*/

#pragma once

#include <stddef.h> // size_t
#include <stdint.h> // uint32_t

uint32_t tbc_crc32(const unsigned char* src, size_t srcLen, uint32_t prev_val);
