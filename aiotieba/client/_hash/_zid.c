#include "_zid.h"

int tbh_invRC4(char *dst, const char *secKey, const char *xyusMd5)
{
	char *sBox = malloc(256);
	if (!sBox)
	{
		return TBH_MEMORY_ERROR;
	}
	for (int i = 0; i < 256; i++)
	{
		sBox[i] = (char)i;
	}

	int iCycle = 0;
	int iMd5 = 0;
	for (int iSBox = 0; iSBox < 256; iSBox++)
	{
		iCycle = (iCycle + xyusMd5[iMd5] + sBox[iSBox]) & 255;
		char tmp = sBox[iSBox];
		sBox[iSBox] = sBox[iCycle];
		sBox[iCycle] = tmp;
		iMd5 = (iMd5 + 1) % TBH_MD5_STR_SIZE;
	}

	int iSwapA = 0;
	int iSwapB = 0;
	for (int iSec = 0; iSec < TBH_SECKEY_SIZE; iSec++)
	{
		iSwapA++;
		iSwapB = (iSwapB + sBox[iSwapA]) & 255;
		char tmp = sBox[iSwapA];
		sBox[iSwapA] = sBox[iSwapB];
		sBox[iSwapB] = tmp;
		dst[iSec] = (char)(sBox[(sBox[iSwapA] + sBox[iSwapB]) & 255] ^ secKey[iSec]);
		dst[iSec] = (char)(dst[iSec] ^ 42);
	}

	return TBH_OK;
}
