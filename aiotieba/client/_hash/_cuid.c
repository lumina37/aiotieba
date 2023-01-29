#include "_cuid.h"

#define HASHER_NUM 4
#define STEP_SIZE 5
#define HASH_SIZE_IN_BIT 32

static const char HEX_TABLE[] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};

bool __update(uint64_t *sec, uint64_t hashVal, uint64_t start, bool flag)
{
	uint64_t end = start + HASH_SIZE_IN_BIT;
	uint64_t secTemp = *sec;
	uint64_t var9 = ((uint64_t)1 << end) - 1;
	uint64_t var5 = (var9 & *sec) >> start;

	if (flag)
	{
		var5 ^= hashVal;
	}
	else
	{
		var5 &= hashVal;
	}

	for (uint64_t i = 0; i < HASH_SIZE_IN_BIT; i++)
	{
		uint64_t opIdx = start + i;
		if (var5 & (uint64_t)1 << i)
		{
			secTemp |= (uint64_t)1 << opIdx;
		}
		else
		{
			secTemp &= ~((uint64_t)1 << opIdx);
		}
	}

	*sec = secTemp;
	return true;
}

bool __writeBuffer(char *buffer, const uint64_t sec)
{
	uint64_t tmpSec = sec;
	for (uint64_t i = 0; i < STEP_SIZE; i++)
	{
		buffer[i] = (char)((uint64_t)UINT8_MAX & tmpSec);
		tmpSec >>= 8;
	}
	return true;
}

bool tbh_heliosHash(char *dst, const char *src, size_t srcSize)
{
	size_t _buffSize = srcSize + ((size_t)HASHER_NUM * STEP_SIZE);
	char *buffer = (char *)malloc(_buffSize); // internal
	if (!buffer)
	{
		return false;
	}

	memcpy(buffer, src, srcSize); // Now buffer is [src, ...]

	// init
	size_t buffOffset = srcSize;
	memset(buffer + buffOffset, -1, STEP_SIZE); // Now buffer is [src, -1 * 5, ...]
	uint64_t sec = ((uint64_t)1 << 40) - 1;		// equals to `-1L>>>-40L` in java
	uint64_t crc32Val, xxhash32Val;

	// 1st hash with CRC32
	buffOffset += STEP_SIZE;
	crc32Val = (uint64_t)crc32(buffer, buffOffset);
	__update(&sec, crc32Val, 8, false);
	__writeBuffer(buffer + buffOffset, sec); // Now buffer is [src, -1 * 5, crcrc, ...]

	// 2nd hash with xxHash32
	buffOffset += STEP_SIZE;
	xxhash32Val = (uint64_t)XXH32(buffer, buffOffset, 0);
	__update(&sec, xxhash32Val, 0, true);
	__writeBuffer(buffer + buffOffset, sec); // Now buffer is [src, -1[5], crc[5], xxxxx, ...]

	// 3rd hash with xxHash32
	buffOffset += STEP_SIZE;
	xxhash32Val = (uint64_t)XXH32(buffer, buffOffset, 0);
	__update(&sec, xxhash32Val, 1, true);
	__writeBuffer(buffer + buffOffset, sec); // Now buffer is [src, -1[5], crc[5], xx[5], ...]

	// 4th hash with CRC32
	buffOffset += STEP_SIZE;
	crc32Val = (uint64_t)crc32(buffer, buffOffset);
	__update(&sec, crc32Val, 7, true);

	// fill dst
	__writeBuffer(dst, sec);

	// clean up
	free(buffer);
	return true;
}

bool tbh_cuid_galaxy2(char *dst, const char *androidID)
{
	// step 1: build src buffer and compute md5
	const size_t md5BuffSize = sizeof(CUID2_PERFIX) + TBH_ANDROID_ID_SIZE;
	char md5Buffer[sizeof(CUID2_PERFIX) + TBH_ANDROID_ID_SIZE];

	size_t buffOffset = 0;
	memcpy(md5Buffer, CUID2_PERFIX, sizeof(CUID2_PERFIX));
	buffOffset += sizeof(CUID2_PERFIX);
	memcpy(md5Buffer + buffOffset, androidID, TBH_ANDROID_ID_SIZE);

	MD5_HASH md5;
	Md5Calculate(md5Buffer, sizeof(md5Buffer), &md5);

	// step 2: assign md5 hex to dst
	// dst will be [md5 hex, ...]
	size_t dstOffset = 0;
	for (size_t imd5 = 0; imd5 < MD5_HASH_SIZE; imd5++)
	{
		dst[dstOffset] = HEX_TABLE[md5.bytes[imd5] >> 4];
		dstOffset++;
		dst[dstOffset] = HEX_TABLE[md5.bytes[imd5] & 0x0F];
		dstOffset++;
	}

	// step 3: add joining char
	// dst will be [md5 hex, '|V', ...]
	dst[dstOffset] = '|';
	dstOffset++;
	dst[dstOffset] = 'V';
	dstOffset++;

	// step 4: build dst buffer and compute helios hash
	char heHash[TBH_HELIOS_HASH_SIZE];
	bool succeed = tbh_heliosHash(heHash, dst, TBH_MD5_STR_SIZE);
	if (!succeed)
	{
		return false;
	}

	// step 5: assign helios base32 to dst
	// dst will be [md5 hex, '|V', heliosHash base32]
	base32_encode((uint8_t *)heHash, TBH_HELIOS_HASH_SIZE, (dst + dstOffset));

	return true;
}

bool tbh_c3_aid(char *dst, const char *androidID, const char *uuid)
{
	// step 1: set perfix
	// dst will be ['A00-', ...]
	dst[0] = 'A';
	dst[1] = '0';
	dst[2] = '0';
	dst[3] = '-';
	size_t dstOffset = 4;

	// step 2: build src buffer and compute sha1
	char sha1Buffer[sizeof(CUID3_PERFIX) + TBH_ANDROID_ID_SIZE + TBH_UUID_SIZE];

	size_t sha1BuffOffset = 0;
	memcpy(sha1Buffer, CUID3_PERFIX, sizeof(CUID3_PERFIX));
	sha1BuffOffset += sizeof(CUID3_PERFIX);
	memcpy(sha1Buffer + sha1BuffOffset, androidID, TBH_ANDROID_ID_SIZE);
	sha1BuffOffset += TBH_ANDROID_ID_SIZE;
	memcpy(sha1Buffer + sha1BuffOffset, uuid, TBH_UUID_SIZE);

	SHA1_HASH sha1;
	Sha1Calculate(sha1Buffer, sizeof(sha1Buffer), &sha1);

	// step 3: compute sha1 base32 and assign
	// dst will be ['A00-', sha1 base32, ...]
	base32_encode(sha1.bytes, SHA1_HASH_SIZE, (dst + dstOffset));
	dstOffset += TBH_SHA1_BASE32_SIZE;

	// step 4: add joining char
	// dst will be ['A00-', sha1 base32, '-', ...]
	dst[dstOffset] = '-';
	dstOffset++;

	// step 5: build dst buffer and compute helios hash
	char heHash[TBH_HELIOS_HASH_SIZE];
	bool succeed = tbh_heliosHash(heHash, dst, dstOffset);
	if (!succeed)
	{
		return false;
	}

	// step 6: assign helios base32 to dst
	// dst will be ['A00-', sha1 base32, '-', heliosHash base32]
	base32_encode((uint8_t *)heHash, TBH_HELIOS_HASH_SIZE, (dst + dstOffset));

	return true;
}
