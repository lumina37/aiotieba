// Base32 implementation
//
// Copyright 2010 Google Inc.
// Author: Markus Gutschke
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "base32/base32.h"

static unsigned char base32_table[] = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                                       'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '2', '3', '4', '5', '6', '7'};

void tbc_base32_encode(const unsigned char* src, int srcLen, unsigned char* dst)
{
    int count = 0;
    int buffer = src[0];
    int next = 1;
    int bitsLeft = 8;
    while (bitsLeft > 0 || next < srcLen) {
        if (bitsLeft < 5) {
            if (next < srcLen) {
                buffer <<= 8;
                buffer |= src[next++] & 0xFF;
                bitsLeft += 8;
            } else {
                int pad = 5 - bitsLeft;
                buffer <<= pad;
                bitsLeft += pad;
            }
        }
        int index = 0x1F & (buffer >> (bitsLeft - 5));
        bitsLeft -= 5;
        dst[count++] = base32_table[index];
    }
}
