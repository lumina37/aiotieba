#include "_python.h"

#include "_error.h"
#include "_const.h"
#include "_cuid.h"
#include "_zid.h"
#include "_sign.h"

PyObject *cuid_galaxy2(PyObject *self, PyObject *args)
{
	char dst[TBH_CUID_GALAXY2_SIZE];
	const char *androidID;
	Py_ssize_t androidIDSize;

	if (!PyArg_ParseTuple(args, "s#", &androidID, &androidIDSize))
	{
		PyErr_SetString(PyExc_ValueError, "failed to parse args");
		return NULL;
	}

	int err = tbh_cuid_galaxy2(dst, androidID);
	if (err)
	{
		if (err == TBH_MEMORY_ERROR)
		{
			PyErr_NoMemory();
			return NULL;
		}
		else
		{
			PyErr_Format(PyExc_RuntimeError, "mbedtls err. err_code=%d", err);
			return NULL;
		}
	}

	return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBH_CUID_GALAXY2_SIZE);
}

PyObject *c3_aid(PyObject *self, PyObject *args)
{
	char dst[TBH_C3_AID_SIZE];
	const char *androidID;
	Py_ssize_t androidIDSize;
	const char *uuid;
	Py_ssize_t uuidSize;

	if (!PyArg_ParseTuple(args, "s#s#", &androidID, &androidIDSize, &uuid, &uuidSize))
	{
		PyErr_SetString(PyExc_ValueError, "failed to parse args");
		return NULL;
	}

	int err = tbh_c3_aid(dst, androidID, uuid);
	if (err)
	{
		if (err == TBH_MEMORY_ERROR)
		{
			PyErr_NoMemory();
			return NULL;
		}
		else
		{
			PyErr_Format(PyExc_RuntimeError, "mbedtls err. err_code=%d", err);
			return NULL;
		}
	}

	return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBH_C3_AID_SIZE);
}

PyObject *rc4(PyObject *self, PyObject *args)
{
	char dst[TBH_RC4_SIZE];
	const char *xyusMd5;
	Py_ssize_t xyusMd5Size;
	const char *cbcSecKey;
	Py_ssize_t cbcSecKeySize;

	if (!PyArg_ParseTuple(args, "y#y#", &xyusMd5, &xyusMd5Size, &cbcSecKey, &cbcSecKeySize))
	{
		PyErr_SetString(PyExc_ValueError, "failed to parse args");
		return NULL;
	}

	int err = tbh_rc4(dst, xyusMd5, cbcSecKey);
	if (err)
	{
		if (err == TBH_MEMORY_ERROR)
		{
			PyErr_NoMemory();
			return NULL;
		}
		else
		{
			PyErr_Format(PyExc_RuntimeError, "mbedtls err. err_code=%d", err);
			return NULL;
		}
	}

	return PyBytes_FromStringAndSize(dst, TBH_RC4_SIZE);
}

static PyMethodDef crypto_methods[] = {
	{"cuid_galaxy2", (PyCFunction)cuid_galaxy2, METH_VARARGS, NULL},
	{"c3_aid", (PyCFunction)c3_aid, METH_VARARGS, NULL},
	{"rc4", (PyCFunction)rc4, METH_VARARGS, NULL},
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
