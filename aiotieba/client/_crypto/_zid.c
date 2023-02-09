#include "_zid.h"

int tbh_invRC4(char *dst, const char *secKey, const char *xyusMd5)
{
	uint8_t *sBox = malloc(256);
	if (!sBox)
	{
		return TBH_MEMORY_ERROR;
	}
	for (size_t i = 0; i < 256; i++)
	{
		sBox[i] = (uint8_t)i;
	}

	size_t iMd5 = 0;
	size_t iCycle = 0;
	for (size_t iSBox = 0; iSBox < 256; iSBox++)
	{
		iCycle = (iCycle + (uint8_t)xyusMd5[iMd5] + (uint8_t)sBox[iSBox]) & 255;
		char tmp = sBox[iSBox];
		sBox[iSBox] = sBox[iCycle];
		sBox[iCycle] = tmp;
		iMd5 = (iMd5 + 1) % TBH_MD5_STR_SIZE;
	}

	size_t iSwapA = 0;
	size_t iSwapB = 0;
	for (size_t iSec = 0; iSec < TBH_SECKEY_SIZE; iSec++)
	{
		iSwapA++;
		iSwapB = (iSwapB + sBox[iSwapA]) & 255;
		uint8_t tmp = sBox[iSwapA];
		sBox[iSwapA] = sBox[iSwapB];
		sBox[iSwapB] = tmp;
		dst[iSec] = (char)(sBox[(sBox[iSwapA] + sBox[iSwapB]) & 255] ^ (uint8_t)secKey[iSec]);
		dst[iSec] = (char)(dst[iSec] ^ 42);
	}

	return TBH_OK;
}
