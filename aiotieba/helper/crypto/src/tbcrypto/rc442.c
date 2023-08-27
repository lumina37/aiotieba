#include <stddef.h> // size_t

#include "tbcrypto/const.h"
#include "tbcrypto/error.h"

#include "tbcrypto/rc442.h"

typedef struct rc4_42_context {
    int x;
    int y;
    unsigned char m[256];
} rc4_42_context;

static inline void rc4_42_setup(rc4_42_context* ctx, const unsigned char* key, unsigned int keyLen)
{
    int i, j, a;
    unsigned int k;
    unsigned char* m;

    ctx->x = 0;
    ctx->y = 0;
    m = ctx->m;

    for (i = 0; i < 256; i++)
        m[i] = (unsigned char)i;

    j = k = 0;

    for (i = 0; i < 256; i++, k++) {
        if (k >= keyLen)
            k = 0;

        a = m[i];
        j = (j + a + key[k]) & 0xFF;
        m[i] = m[j];
        m[j] = (unsigned char)a;
    }
}

static inline void rc4_42_crypt(rc4_42_context* ctx, const unsigned char* src, size_t srcLen, unsigned char* dst)
{
    int x, y, a, b;
    size_t i;
    unsigned char* m;

    x = ctx->x;
    y = ctx->y;
    m = ctx->m;

    for (i = 0; i < srcLen; i++) {
        x = (x + 1) & 0xFF;
        a = m[x];
        y = (y + a) & 0xFF;
        b = m[y];

        m[x] = (unsigned char)b;
        m[y] = (unsigned char)a;

        dst[i] = (unsigned char)(src[i] ^ m[(unsigned char)(a + b)]);
        dst[i] = dst[i] ^ 42; // different from general RC4
    }

    ctx->x = x;
    ctx->y = y;
}

void tbc_rc4_42(const unsigned char* xyusMd5Str, const unsigned char* cbcSecKey, unsigned char* dst)
{
    rc4_42_context rc442Ctx;

    rc4_42_setup(&rc442Ctx, xyusMd5Str, TBC_MD5_STR_SIZE);
    rc4_42_crypt(&rc442Ctx, cbcSecKey, TBC_CBC_SECKEY_SIZE, dst);
}
