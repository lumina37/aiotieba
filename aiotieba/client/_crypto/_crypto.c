#undef _DEBUG
#include <Python.h>
#define _DEBUG 1

PyObject *hello_world()
{
	return Py_BuildValue("s", "Hello World");
}

static PyMethodDef _crypto_methods[] = {
	{"hello_world", (PyCFunction)hello_world, METH_O, NULL},
	{NULL, NULL, 0, NULL},
};

static PyModuleDef _crypto_module = {
	PyModuleDef_HEAD_INIT,
	"_crypto",
	"haha",
	-1,
	_crypto_methods,
};

PyMODINIT_FUNC PyInit__crypto()
{
	return PyModule_Create(&_crypto_module);
}
