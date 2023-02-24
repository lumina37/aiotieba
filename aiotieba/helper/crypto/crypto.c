#include "_python.h"

#include "_error.h"
#include "_const.h"
#include "_cuid.h"
#include "_zid.h"
#include "_sign.h"

PyObject *cuid_galaxy2(PyObject *self, PyObject *args)
{
	unsigned char dst[TBC_CUID_GALAXY2_SIZE];
	const unsigned char *androidID;
	Py_ssize_t androidIDSize;

	if (!PyArg_ParseTuple(args, "s#", &androidID, &androidIDSize))
	{
		PyErr_SetString(PyExc_ValueError, "failed to parse args");
		return NULL;
	}

	int err = tbc_cuid_galaxy2(dst, androidID);
	if (err)
	{
		PyErr_NoMemory();
		return NULL;
	}

	return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBC_CUID_GALAXY2_SIZE);
}

PyObject *c3_aid(PyObject *self, PyObject *args)
{
	unsigned char dst[TBC_C3_AID_SIZE];
	const unsigned char *androidID;
	Py_ssize_t androidIDSize;
	const unsigned char *uuid;
	Py_ssize_t uuidSize;

	if (!PyArg_ParseTuple(args, "s#s#", &androidID, &androidIDSize, &uuid, &uuidSize))
	{
		PyErr_SetString(PyExc_ValueError, "failed to parse args");
		return NULL;
	}

	int err = tbc_c3_aid(dst, androidID, uuid);
	if (err)
	{
		PyErr_NoMemory();
		return NULL;
	}

	return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBC_C3_AID_SIZE);
}

PyObject *rc4_42(PyObject *self, PyObject *args)
{
	unsigned char dst[TBC_RC4_SIZE];
	const unsigned char *xyusMd5Str;
	Py_ssize_t xyusMd5Size;
	const unsigned char *cbcSecKey;
	Py_ssize_t cbcSecKeySize;

	if (!PyArg_ParseTuple(args, "s#y#", &xyusMd5Str, &xyusMd5Size, &cbcSecKey, &cbcSecKeySize))
	{
		PyErr_SetString(PyExc_ValueError, "failed to parse args");
		return NULL;
	}

	tbc_rc4_42(dst, xyusMd5Str, cbcSecKey);

	return PyBytes_FromStringAndSize((char *)dst, TBC_RC4_SIZE);
}

static PyMethodDef crypto_methods[] = {
	{"cuid_galaxy2", (PyCFunction)cuid_galaxy2, METH_VARARGS, NULL},
	{"c3_aid", (PyCFunction)c3_aid, METH_VARARGS, NULL},
	{"rc4_42", (PyCFunction)rc4_42, METH_VARARGS, NULL},
	{"sign", (PyCFunction)sign, METH_VARARGS, NULL},
	{NULL, NULL, 0, NULL},
};

static PyModuleDef crypto_module = {
	PyModuleDef_HEAD_INIT,
	"crypto",
	NULL,
	-1,
	crypto_methods,
};

PyMODINIT_FUNC PyInit_crypto()
{
	return PyModule_Create(&crypto_module);
}
