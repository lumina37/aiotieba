#define PY_SSIZE_T_CLEAN // use Py_ssize_t instead of int

#ifdef _DEBUG
#undef _DEBUG // use these steps to avoid linking with python_d.lib
#define __RESTORE_DEBUG
#endif
#include <Python.h>
#ifdef __RESTORE_DEBUG
#define _DEBUG
#undef __RESTORE_DEBUG
#endif

#include "_cuid.h"
#include "_zid.h"

static PyObject *inv_rc4(PyObject *self, PyObject *args)
{
	char dst[TBH_INV_RC4_SIZE];
	const char *secKey;
	Py_ssize_t secKeySize;
	const char *xyusMd5;
	Py_ssize_t xyusMd5Size;

	if (!PyArg_ParseTuple(args, "y#y#", &secKey, &secKeySize, &xyusMd5, &xyusMd5Size))
	{
		PyErr_SetString(PyExc_ValueError, "failed to parse args");
		return NULL;
	}

	int err = tbh_invRC4(dst, secKey, xyusMd5);
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

	return Py_BuildValue("y#", dst, TBH_INV_RC4_SIZE);
}

static PyObject *cuid_galaxy2(PyObject *self, PyObject *args)
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

	return Py_BuildValue("s#", dst, TBH_CUID_GALAXY2_SIZE);
}

static PyObject *c3_aid(PyObject *self, PyObject *args)
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

	return Py_BuildValue("s#", dst, TBH_C3_AID_SIZE);
}

static PyMethodDef _crypto_methods[] = {
	{"inv_rc4", (PyCFunction)inv_rc4, METH_O, NULL},
	{"cuid_galaxy2", (PyCFunction)cuid_galaxy2, METH_O, NULL},
	{"c3_aid", (PyCFunction)c3_aid, METH_O, NULL},
	{NULL, NULL, 0, NULL},
};

static PyModuleDef _crypto_module = {
	PyModuleDef_HEAD_INIT,
	"_crypto",
	NULL,
	-1,
	_crypto_methods,
};

PyMODINIT_FUNC PyInit__crypto()
{
	return PyModule_Create(&_crypto_module);
}
