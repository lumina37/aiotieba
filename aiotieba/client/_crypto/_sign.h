#pragma once

#include <stdlib.h> // malloc free
#include <memory.h> // memset memcpy
#include <string.h> // strlen

#include "_python.h"

#include "mbedtls/md5.h"
#include "itoa.h"

#include "_const.h"

PyObject *sign(PyObject *self, PyObject *args);
