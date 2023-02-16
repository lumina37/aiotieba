#include <stdlib.h> // malloc free
#include <memory.h> // memset memcpy
#include <string.h> // strlen

#include "mbedtls/md5.h"
#include "rapidjson/internal/itoa.h"

#include "_const.h"

#include "_sign.h"

static const unsigned char SIGN_SUFFIX[] = {'t', 'i', 'e', 'b', 'a', 'c', 'l', 'i', 'e', 'n', 't', '!', '!', '!'};

static inline void __pyStr2UTF8(const char **dst, size_t *dstSize, PyObject *pyoStr)
{
    if (PyUnicode_1BYTE_KIND == PyUnicode_KIND(pyoStr))
    {
        (*dst) = PyUnicode_DATA(pyoStr);
        (*dstSize) = PyUnicode_GET_LENGTH(pyoStr);
    }
    else
    {
        (*dst) = PyUnicode_AsUTF8(pyoStr);
        (*dstSize) = strlen(*dst);
    }
}

PyObject *sign(PyObject *self, PyObject *args)
{
    PyObject *items;
    if (!PyArg_ParseTuple(args, "O", &items))
    {
        PyErr_SetString(PyExc_ValueError, "failed to parse args");
        return NULL;
    }
    Py_ssize_t listSize = PyList_GET_SIZE(items);

    mbedtls_md5_context md5Ctx;
    mbedtls_md5_init(&md5Ctx);
    mbedtls_md5_starts(&md5Ctx);
    char itoaBuffer[20];
    unsigned char equal = '=';
    for (Py_ssize_t iList = 0; iList < listSize; iList++)
    {
        PyObject *item = PyList_GET_ITEM(items, iList);

        const char *key;
        size_t keySize;
        PyObject *pyoKey = PyTuple_GET_ITEM(item, 0);
        __pyStr2UTF8(&key, &keySize, pyoKey);
        mbedtls_md5_update(&md5Ctx, (unsigned char *)key, keySize);

        mbedtls_md5_update(&md5Ctx, &equal, sizeof(equal));

        PyObject *pyoVal = PyTuple_GET_ITEM(item, 1);
        if (PyUnicode_Check(pyoVal))
        {
            const char *val;
            size_t valSize;
            __pyStr2UTF8(&val, &valSize, pyoVal);
            mbedtls_md5_update(&md5Ctx, (unsigned char *)val, valSize);
        }
        else
        {
            int64_t ival = PyLong_AsLongLong(pyoVal);
            char *val = itoaBuffer;
            char *valEnd = i64toa(ival, val);
            size_t valSize = valEnd - val;
            mbedtls_md5_update(&md5Ctx, (unsigned char *)val, valSize);
        }
    }

    mbedtls_md5_update(&md5Ctx, SIGN_SUFFIX, sizeof(SIGN_SUFFIX));

    unsigned char md5[TBC_MD5_HASH_SIZE];
    mbedtls_md5_finish(&md5Ctx, md5);

    unsigned char dst[TBC_MD5_STR_SIZE];
    size_t dstOffset = 0;
    for (size_t imd5 = 0; imd5 < TBC_MD5_HASH_SIZE; imd5++)
    {
        dst[dstOffset] = HEX_LOWCASE_TABLE[md5[imd5] >> 4];
        dstOffset++;
        dst[dstOffset] = HEX_LOWCASE_TABLE[md5[imd5] & 0x0F];
        dstOffset++;
    }

    return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBC_MD5_STR_SIZE);
}
