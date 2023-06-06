#pragma once

#include "base32/base32.h"

#define TBC_UUID_SIZE 36
#define TBC_ANDROID_ID_SIZE 16

#define TBC_MD5_HASH_SIZE 16
#define TBC_MD5_STR_SIZE (TBC_MD5_HASH_SIZE * 2)

#define TBC_SHA1_HASH_SIZE 20
#define TBC_SHA1_HEX_SIZE (TBC_SHA1_HASH_SIZE * 2)
#define TBC_SHA1_BASE32_SIZE (BASE32_LEN(TBC_SHA1_HASH_SIZE))

#define TBC_HELIOS_HASH_SIZE 5
#define TBC_HELIOS_BASE32_SIZE (BASE32_LEN(TBC_HELIOS_HASH_SIZE))

#define TBC_CUID_GALAXY2_SIZE (TBC_MD5_STR_SIZE + 2 + TBC_HELIOS_BASE32_SIZE)
#define TBC_C3_AID_SIZE (4 + TBC_SHA1_BASE32_SIZE + 1 + TBC_HELIOS_BASE32_SIZE)

static const unsigned char HEX_UPPERCASE_TABLE[] = {'0', '1', '2', '3', '4', '5', '6', '7',
                                                    '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};
static const unsigned char HEX_LOWERCASE_TABLE[] = {'0', '1', '2', '3', '4', '5', '6', '7',
                                                    '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};
