#include "_zid.h"

int tbh_rc4(char *dst, const char *xyusMd5, const char *cbcSecKey)
{
	mbedtls_arc4_context rc4Ctx;

	mbedtls_arc4_init(&rc4Ctx);
	mbedtls_arc4_setup(&rc4Ctx, xyusMd5, TBH_MD5_HASH_SIZE);
	mbedtls_arc4_crypt(&rc4Ctx, TBH_CBC_SECKEY_SIZE, cbcSecKey, dst);

	return TBH_OK;
}
