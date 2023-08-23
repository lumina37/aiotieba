#include <memory.h> // memset memcpy
#include <string.h> // strlen

#include "mbedtls/md5.h"
#include "rapidjson/itoa.h"

#include "tbcrypto/const.h"

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

PyObject* sign(PyObject* Py_UNUSED(self), PyObject* args)
{
    PyObject* items;

#ifdef TBC_NO_CHECK
    PyArg_ParseTuple(args, "O", &items);
#else
    if (!PyArg_ParseTuple(args, "O", &items)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse args");
        return NULL;
    }
    if (!PyList_Check(items)) {
        PyErr_SetString(PyExc_TypeError, "Input should be List[Tuple[str, str | int]]]");
        return NULL;
    }
#endif

    Py_ssize_t listSize = PyList_GET_SIZE(items);

    mbedtls_md5_context md5Ctx;
    mbedtls_md5_init(&md5Ctx);
    mbedtls_md5_starts(&md5Ctx);
    char itoaBuffer[20];

    for (Py_ssize_t iList = 0; iList < listSize; iList++) {
        PyObject* item = PyList_GET_ITEM(items, iList);

#ifndef TBC_NO_CHECK
        if (!PyTuple_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "List item should be Tuple[str, str | int]");
            return NULL;
        }
#endif

#ifdef TBC_NO_CHECK
        PyObject* pyoKey = PyTuple_GET_ITEM(item, 0);
#else
        PyObject* pyoKey = PyTuple_GetItem(item, 0);
        if (!pyoKey) {
            return NULL; // IndexError
        }
#endif

        char* key;
        size_t keySize;
        __tbc_pyStr2UTF8((const char**)&key, &keySize, pyoKey);

        // Warn: The last NULL is replaced by '=', DO NOT use `strlen` or similar method over `key` afterwards!
        key[keySize] = '=';
        keySize++;

        mbedtls_md5_update(&md5Ctx, (unsigned char*)key, keySize);

#ifdef TBC_NO_CHECK
        PyObject* pyoVal = PyTuple_GET_ITEM(item, 1);
#else
        PyObject* pyoVal = PyTuple_GetItem(item, 1);
        if (!pyoVal) {
            return NULL; // IndexError
        }
#endif
        if (PyUnicode_Check(pyoVal)) {
            const char* val;
            size_t valSize;
            __tbc_pyStr2UTF8(&val, &valSize, pyoVal);
            mbedtls_md5_update(&md5Ctx, (unsigned char*)val, valSize);
        } else {

#ifndef TBC_NO_CHECK
            if (PyLong_Check(pyoVal)) {
#endif

                int64_t ival = PyLong_AsLongLong(pyoVal);
                char* val = itoaBuffer;
                char* valEnd = i64toa(ival, val);
                size_t valSize = valEnd - val;
                mbedtls_md5_update(&md5Ctx, (unsigned char*)val, valSize);

#ifndef TBC_NO_CHECK
            } else {
                PyErr_SetString(PyExc_TypeError, "item[1] should be str or int");
                return NULL;
            }
#endif
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
