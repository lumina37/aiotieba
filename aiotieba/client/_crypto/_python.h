#pragma once

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
