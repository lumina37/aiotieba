#include "tbcrypto/pywrap.h"

#include "tbcrypto/bb64.h"
#include "tbcrypto/const.h"
#include "tbcrypto/cuid.h"
#include "tbcrypto/rc442.h"

PyObject* cuid_galaxy2(PyObject* Py_UNUSED(self), PyObject* const* args, Py_ssize_t nargs) {
    if (nargs != 1) {
        PyErr_Format(PyExc_TypeError, "Expected 1 argument, got %zd", nargs);
        return NULL;
    }

    unsigned char dst[TBC_CUID_GALAXY2_SIZE];
    const unsigned char* androidID = PyUnicode_DATA(args[0]);
    const Py_ssize_t androidIDSize = PyUnicode_GET_LENGTH(args[0]);

    if (androidIDSize != TBC_ANDROID_ID_SIZE) {
        PyErr_Format(PyExc_ValueError, "Invalid size of android_id. Expect %zd, got %zd", TBC_ANDROID_ID_SIZE,
                     androidIDSize);
        return NULL;
    }

    tbc_cuid_galaxy2(androidID, dst);

    return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBC_CUID_GALAXY2_SIZE);
}

PyObject* c3_aid(PyObject* Py_UNUSED(self), PyObject* const* args, Py_ssize_t nargs) {
    if (nargs != 2) {
        PyErr_Format(PyExc_TypeError, "Expected 2 arguments, got %zd", nargs);
        return NULL;
    }

    unsigned char dst[TBC_C3_AID_SIZE];
    const unsigned char* androidID = PyUnicode_DATA(args[0]);
    const Py_ssize_t androidIDSize = PyUnicode_GET_LENGTH(args[0]);
    const unsigned char* uuid = PyUnicode_DATA(args[1]);
    const Py_ssize_t uuidSize = PyUnicode_GET_LENGTH(args[1]);

    if (androidIDSize != TBC_ANDROID_ID_SIZE) {
        PyErr_Format(PyExc_ValueError, "Invalid size of android_id. Expect %zd, got %zd", TBC_ANDROID_ID_SIZE,
                     androidIDSize);
        return NULL;
    }
    if (uuidSize != TBC_UUID_SIZE) {
        PyErr_Format(PyExc_ValueError, "Invalid size of uuid. Expect %zd, got %zd", TBC_UUID_SIZE, uuidSize);
        return NULL;
    }

    tbc_c3_aid(androidID, uuid, dst);

    return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBC_C3_AID_SIZE);
}

PyObject* rc4_42(PyObject* Py_UNUSED(self), PyObject* const* args, Py_ssize_t nargs) {
    if (nargs != 2) {
        PyErr_Format(PyExc_TypeError, "Expected 2 arguments, got %zd", nargs);
        return NULL;
    }

    unsigned char dst[TBC_RC4_SIZE];
    const unsigned char* xyusMd5Str = PyUnicode_DATA(args[0]);
    const Py_ssize_t xyusMd5Size = PyUnicode_GET_LENGTH(args[0]);
    const unsigned char* cbcSecKey = (unsigned char*)PyBytes_AS_STRING(args[1]);
    Py_ssize_t cbcSecKeySize = PyBytes_GET_SIZE(args[1]);

    if (xyusMd5Size != TBC_MD5_STR_SIZE) {
        PyErr_Format(PyExc_ValueError, "Invalid size of xyus_md5. Expect %zd, got %zd", TBC_MD5_STR_SIZE, xyusMd5Size);
        return NULL;
    }
    if (cbcSecKeySize != TBC_CBC_SECKEY_SIZE) {
        PyErr_Format(PyExc_ValueError, "Invalid size of cbc_sec_key. Expect %zd, got %zd", TBC_CBC_SECKEY_SIZE,
                     cbcSecKeySize);
        return NULL;
    }

    tbc_rc4_42(xyusMd5Str, cbcSecKey, dst);

    // py315: should use [`PyBytesWriter`](https://peps.python.org/pep-0782/) instead
    return PyBytes_FromStringAndSize((char*)dst, TBC_RC4_SIZE);
}

PyObject* enuid(PyObject* Py_UNUSED(self), PyObject* const* args, Py_ssize_t nargs) {
    if (nargs != 1) {
        PyErr_Format(PyExc_TypeError, "Expected 1 argument, got %zd", nargs);
        return NULL;
    }

    unsigned char dst[TBC_ENUID_SIZE + 1];
    const unsigned char* cuid2 = PyUnicode_DATA(args[0]);
    const Py_ssize_t cuid2Size = PyUnicode_GET_LENGTH(args[0]);

    if (cuid2Size != TBC_CUID_GALAXY2_SIZE) {
        PyErr_Format(PyExc_ValueError, "Invalid size of cuid_galaxy2. Expect %zd, got %zd", TBC_CUID_GALAXY2_SIZE,
                     cuid2Size);
        return NULL;
    }

    tbc_BB64Encode(cuid2, (int)cuid2Size, 0, dst);

    return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBC_ENUID_SIZE);
}

static PyMethodDef crypto_methods[] = {
    {"cuid_galaxy2", (PyCFunction)cuid_galaxy2, METH_FASTCALL, NULL},
    {"c3_aid", (PyCFunction)c3_aid, METH_FASTCALL, NULL},
    {"rc4_42", (PyCFunction)rc4_42, METH_FASTCALL, NULL},
    {"enuid", (PyCFunction)enuid, METH_FASTCALL, NULL},
    {NULL, NULL, 0, NULL},
};

static PyModuleDef crypto_module = {PyModuleDef_HEAD_INIT, "crypto", NULL, -1, crypto_methods};

PyMODINIT_FUNC PyInit_crypto(void) {
    PyObject* mod = PyModule_Create(&crypto_module);
    if (mod == NULL) {
        return NULL;
    }

#ifdef Py_GIL_DISABLED
    PyUnstable_Module_SetGIL(mod, Py_MOD_GIL_NOT_USED);
#endif

    return mod;
}
