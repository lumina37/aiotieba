#include "tbcrypto/bb64.h"

#include <string.h>
#include <stdlib.h>

#define LAST_IND(x,part_type)    (sizeof(x)/sizeof(part_type) - 1)
#if defined(__BYTE_ORDER) && __BYTE_ORDER == __BIG_ENDIAN
#  define LOW_IND(x,part_type)   LAST_IND(x,part_type)
#  define HIGH_IND(x,part_type)  0
#else
#  define HIGH_IND(x,part_type)  LAST_IND(x,part_type)
#  define LOW_IND(x,part_type)   0
#endif

#define _BYTE unsigned char

#define LOBYTE(x)  BYTEn(x,LOW_IND(x,_BYTE))
#define HIBYTE(x)  BYTEn(x,HIGH_IND(x,_BYTE))

#define BYTEn(x, n)   (*((_BYTE*)&(x)+n))

#define BYTE1(x) BYTEn(x, 1)

#define BYTE2(x) BYTEn(x, 2)


unsigned char* B6417 = "qogjOuCRNkfil5p4SQ3LAmxGKZTdesvB6z_YPahMI9t80rJyHW1DEwFbc7nUVX2-";

unsigned int BB64ResultLen(int srcLen)
{
    return 4 * ((srcLen + 2) / 3u) + 2;
}

unsigned char* B6411(unsigned char* result, unsigned char a2, int a3) //int result
{
    while ( a3 )
    {
        --a3;
        *(unsigned char *)(result + a3) = a2;
    }
    return result;
}

unsigned char* B6412(unsigned char* result, const unsigned char* a2, int a3)
{
    while ( a3 )
    {
        --a3;
        *(unsigned char *)(result + a3) = *(unsigned char *)(a2 + a3);
    }
    return result;
}

unsigned char* B6413(int *a1, int a2, int a3)
{
    int v3; // r6
    int v4; // r8
    int v7; // r7
    unsigned char* result; // r0
    int i; // r3

    v3 = a2 & 0x3F;
    v4 = 64 - v3;
    v7 = (a2 << (32 - 5) | (a2 >> 5));
    B6412((unsigned char*)(a1 + 33), &B6417[v3], v4);
    result = B6412((unsigned char *)a1 + v4 + 132, B6417, v3);
    *a1 = v7 ^ (758653732 << (v7 & 0xF));
    if ( a3 )
    {
        result = B6411((unsigned char *) (a1 + 1), 64, 128);
        for ( i = 0; i != 64; ++i )
            *((unsigned char *)a1 + *((unsigned char *)a1 + i + 132) + 4) = i;
    }
    return result;
}

int* B6419(const int *a1, int *a2, unsigned int a3)
{
    unsigned int v3; // r3
    int v4; // r4
    int *result; // r0

    v3 = a3 >> 2;
    v4 = *a1;
    for ( result = a2; result != &a2[a3 >> 2]; ++result )
        *result = v4 ^ (*result << (32 - 3) | (*result >> 3));
    if ( v3 < (a3 + 3) >> 2 )
        a2[v3] ^= v4;
    return result;
}


unsigned char* B6414(unsigned char* a1, const unsigned char *a2, int *a3)
{
    unsigned int v3; // r5
    unsigned int v4; // r4
    unsigned int v5; // r3
    unsigned char* v6; // r1
    unsigned char* result; // r0
    int v8; // [sp+4h] [bp-14h]

    v3 = (unsigned int)*a2;
    v4 = (unsigned int)a2[1];
    LOBYTE(v8) = *(unsigned char *)((v3 & 0x3F) + a1 + 132);
    BYTE1(v8) = *(unsigned char *)((v4 & 0x3F) + a1 + 132);
    v5 = (unsigned int)a2[2];
    v6 = (v5 & 0x3F) + a1;
    result = a1 + ((4 * (v4 >> 6)) | (16 * (v3 >> 6)) | (v5 >> 6));
    BYTE2(v8) = *(_BYTE *)(v6 + 132);
    HIBYTE(v8) = *(_BYTE *)(result + 132);
    *a3 = v8;
    return result;
}


unsigned int GC02(unsigned char * preResultArray, unsigned int inputArrayLen, int mode)
{
    unsigned int v5; // r9
    unsigned int v6; // r5
    unsigned int v7; // r8
    unsigned int v8; // r7
    unsigned char* v9; // r11
    unsigned char* v10; // r10
    int i; // r8
    unsigned int result; // r0
    unsigned char v13[4] = {0}; // [sp+Ch] [bp-F4h] BYREF
    unsigned char v14[196]; // [sp+10h] [bp-F0h] BYREF

    if ( !inputArrayLen || !preResultArray )
        return -1;
    v5 = inputArrayLen % 3;
    v6 = inputArrayLen / 3;
    v7 = 4 * (inputArrayLen / 3);
    B6413((int *) v14, mode, 0);
    B6419((int *) v14, (int *) preResultArray, inputArrayLen);
    if ( v5 )
    {
        B6412(v13, preResultArray + 3 * v6, v5);
        B6414(v14, (unsigned char*)v13, (int *) (preResultArray + 3 * v6 + v6));
        v8 = v7 + 4;
    }
    else
    {
        v8 = 4 * (inputArrayLen / 3);
    }
    v9 = preResultArray + 3 * v6;
    v10 = preResultArray + v7 - 4;
    for ( i = 0; ; ++i )
    {
        v9 -= 3;
        if ( i == v6 )
            break;
        B6414(v14, v9, (int *) (v10 - 4 * i));
    }
    *(unsigned char *)(preResultArray + v8) = v5 + 65;
    result = v8 + 2;
    *(unsigned char *)(preResultArray + v8 + 1) = 0;
    return result;
}



void tbc_BB64Encode(unsigned char *inputArray, int srcLen, int mode, unsigned char *dst)
{
    signed int inputArrayLen; // r8
    void *v12; // r5
    int v13; // r0
    unsigned char* resultArray; // r7

    inputArrayLen = srcLen; //GetArrayLength

    unsigned int resultLen = BB64ResultLen(inputArrayLen);
    v12 = (unsigned char *)malloc(resultLen);
    memset(v12, 0, resultLen);
    memcpy(v12, inputArray, inputArrayLen);
    v13 = GC02(v12, inputArrayLen, mode);
    memcpy(dst, (unsigned char *)v12, resultLen*sizeof(unsigned char ));//memcpy
    free(v12);
}
