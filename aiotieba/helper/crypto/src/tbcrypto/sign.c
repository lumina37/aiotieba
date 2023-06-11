#include <memory.h> // memset memcpy
#include <string.h> // strlen

#include "mbedtls/md5.h"
#include "rapidjson/itoa.h"

#include "tbcrypto/const.h"
#include "tbcrypto/utils.h"

#include "tbcrypto/sign.h"

static const unsigned char SIGN_SUFFIX[] = {'t', 'i', 'e', 'b', 'a', 'c', 'l', 'i', 'e', 'n', 't', '!', '!', '!'};

static inline void __tbc_pyStr2UTF8(const char** dst, size_t* dstSize, PyObject* pyoStr)
{
    if (PyUnicode_1BYTE_KIND == PyUnicode_KIND(pyoStr)) {
        (*dst) = PyUnicode_DATA(pyoStr);
        (*dstSize) = PyUnicode_GET_LENGTH(pyoStr);
    } else {
        (*dst) = PyUnicode_AsUTF8(pyoStr);
        (*dstSize) = strlen(*dst);
    }
}

PyObject* sign(TBC_UNUSED PyObject* self, PyObject* args)
{
    PyObject* items;
    if (!PyArg_ParseTuple(args, "O", &items)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse args");
        return NULL;
    }
    if (!PyList_Check(items)) {
        PyErr_SetString(PyExc_TypeError, "Input should be List[Tuple[str, str | int]]]");
        return NULL;
    }

    Py_ssize_t listSize = PyList_GET_SIZE(items);

    mbedtls_md5_context md5Ctx;
    mbedtls_md5_init(&md5Ctx);
    mbedtls_md5_starts(&md5Ctx);
    char itoaBuffer[20];
    const unsigned char equal = '=';

    for (Py_ssize_t iList = 0; iList < listSize; iList++) {
        PyObject* item = PyList_GET_ITEM(items, iList);

        if (!PyTuple_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "List item should be Tuple[str, str | int]");
            return NULL;
        }

        PyObject* pyoKey = PyTuple_GetItem(item, 0);
        if (!pyoKey) {
            return NULL; // IndexError
        }

        const char* key;
        size_t keySize;
        __tbc_pyStr2UTF8(&key, &keySize, pyoKey);
        mbedtls_md5_update(&md5Ctx, (unsigned char*)key, keySize);

        mbedtls_md5_update(&md5Ctx, &equal, sizeof(equal));

        PyObject* pyoVal = PyTuple_GetItem(item, 1);
        if (!pyoVal) {
            return NULL; // IndexError
        }

        if (PyUnicode_Check(pyoVal)) {
            const char* val;
            size_t valSize;
            __tbc_pyStr2UTF8(&val, &valSize, pyoVal);
            mbedtls_md5_update(&md5Ctx, (unsigned char*)val, valSize);
        } else if (PyLong_Check(pyoVal)) {
            int64_t ival = PyLong_AsLongLong(pyoVal);
            char* val = itoaBuffer;
            char* valEnd = i64toa(ival, val);
            size_t valSize = valEnd - val;
            mbedtls_md5_update(&md5Ctx, (unsigned char*)val, valSize);
        } else {
            PyErr_SetString(PyExc_TypeError, "item[1] should be str or int");
            return NULL;
        }
    }

    mbedtls_md5_update(&md5Ctx, SIGN_SUFFIX, sizeof(SIGN_SUFFIX));

    unsigned char md5[TBC_MD5_HASH_SIZE];
    mbedtls_md5_finish(&md5Ctx, md5);

    unsigned char dst[TBC_MD5_STR_SIZE];
    size_t dstOffset = 0;
    for (size_t imd5 = 0; imd5 < TBC_MD5_HASH_SIZE; imd5++) {
        dst[dstOffset] = HEX_LOWERCASE_TABLE[md5[imd5] >> 4];
        dstOffset++;
        dst[dstOffset] = HEX_LOWERCASE_TABLE[md5[imd5] & 0x0F];
        dstOffset++;
    }

    return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBC_MD5_STR_SIZE);
}
