#pragma once

#define PY_SSIZE_T_CLEAN // use Py_ssize_t instead of int

#ifdef TBC_FORCE_PYTHON_NODEBUG
#ifdef _DEBUG
#undef _DEBUG // use these steps to avoid linking with python_d.lib
#define __TBC_RESTORE_DEBUG
#endif
#include <Python.h>
#ifdef __TBC_RESTORE_DEBUG
#define _DEBUG
#undef __TBC_RESTORE_DEBUG
#endif
#else
#include <Python.h>
#endif
