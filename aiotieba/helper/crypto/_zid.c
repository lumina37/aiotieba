#include <memory.h> // memset

#include "_error.h"
#include "_const.h"

#include "_zid.h"

typedef struct rc4_42_context
{
	int x;
	int y;
	unsigned char m[256];
} rc4_42_context;

static inline void rc4_42_setup(rc4_42_context *ctx, const unsigned char *key, unsigned int keylen)
{
	int i, j, a;
	unsigned int k;
	unsigned char *m;

	ctx->x = 0;
	ctx->y = 0;
	m = ctx->m;

	for (i = 0; i < 256; i++)
		m[i] = (unsigned char)i;

	j = k = 0;

	for (i = 0; i < 256; i++, k++)
	{
		if (k >= keylen)
			k = 0;

		a = m[i];
		j = (j + a + key[k]) & 0xFF;
		m[i] = m[j];
		m[j] = (unsigned char)a;
	}
}

static void rc4_42_crypt(rc4_42_context *ctx, size_t length, const unsigned char *input, unsigned char *output)
{
	int x, y, a, b;
	size_t i;
	unsigned char *m;

	x = ctx->x;
	y = ctx->y;
	m = ctx->m;

	for (i = 0; i < length; i++)
	{
		x = (x + 1) & 0xFF;
		a = m[x];
		y = (y + a) & 0xFF;
		b = m[y];

		m[x] = (unsigned char)b;
		m[y] = (unsigned char)a;

		output[i] = (unsigned char)(input[i] ^ m[(unsigned char)(a + b)]);
		output[i] = output[i] ^ 42; // different from general RC4
	}

	ctx->x = x;
	ctx->y = y;
}

int tbc_rc4_42(unsigned char *dst, const unsigned char *xyusMd5Str, const unsigned char *cbcSecKey)
{
	rc4_42_context rc442Ctx;

	rc4_42_setup(&rc442Ctx, xyusMd5Str, TBC_MD5_STR_SIZE);
	rc4_42_crypt(&rc442Ctx, TBC_CBC_SECKEY_SIZE, cbcSecKey, dst);

	return TBC_OK;
}
