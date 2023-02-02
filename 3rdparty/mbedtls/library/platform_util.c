/*
 * Common and shared functions used by multiple modules in the Mbed TLS
 * library.
 *
 *  Copyright The Mbed TLS Contributors
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Licensed under the Apache License, Version 2.0 (the "License"); you may
 *  not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 *  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

/*
 * Ensure gmtime_r is available even with -std=c99; must be defined before
 * mbedtls_config.h, which pulls in glibc's features.h. Harmless on other platforms.
 */
#if !defined(_POSIX_C_SOURCE)
#define _POSIX_C_SOURCE 200112L
#endif

#include "common.h"

#include "mbedtls/platform_util.h"
#include "mbedtls/platform.h"

#include <stddef.h>
#include <string.h>

#if !defined(MBEDTLS_PLATFORM_ZEROIZE_ALT)
/*
 * This implementation should never be optimized out by the compiler
 *
 * This implementation for mbedtls_platform_zeroize() was inspired from Colin
 * Percival's blog article at:
 *
 * http://www.daemonology.net/blog/2014-09-04-how-to-zero-a-buffer.html
 *
 * It uses a volatile function pointer to the standard memset(). Because the
 * pointer is volatile the compiler expects it to change at
 * any time and will not optimize out the call that could potentially perform
 * other operations on the input buffer instead of just setting it to 0.
 * Nevertheless, as pointed out by davidtgoldblatt on Hacker News
 * (refer to http://www.daemonology.net/blog/2014-09-05-erratum.html for
 * details), optimizations of the following form are still possible:
 *
 * if( memset_func != memset )
 *     memset_func( buf, 0, len );
 *
 * Note that it is extremely difficult to guarantee that
 * mbedtls_platform_zeroize() will not be optimized out by aggressive compilers
 * in a portable way. For this reason, Mbed TLS also provides the configuration
 * option MBEDTLS_PLATFORM_ZEROIZE_ALT, which allows users to configure
 * mbedtls_platform_zeroize() to use a suitable implementation for their
 * platform and needs.
 */
static void *(*const volatile memset_func)(void *, int, size_t) = memset;

void mbedtls_platform_zeroize(void *buf, size_t len)
{
    MBEDTLS_INTERNAL_VALIDATE(len == 0 || buf != NULL);

    if (len > 0) {
        memset_func(buf, 0, len);
    }
}
#endif /* MBEDTLS_PLATFORM_ZEROIZE_ALT */

/*
 * Provide external definitions of some inline functions so that the compiler
 * has the option to not inline them
 */
extern inline void mbedtls_xor(unsigned char *r,
                               const unsigned char *a,
                               const unsigned char *b,
                               size_t n);

extern inline uint16_t mbedtls_get_unaligned_uint16(const void *p);

extern inline void mbedtls_put_unaligned_uint16(void *p, uint16_t x);

extern inline uint32_t mbedtls_get_unaligned_uint32(const void *p);

extern inline void mbedtls_put_unaligned_uint32(void *p, uint32_t x);

extern inline uint64_t mbedtls_get_unaligned_uint64(const void *p);

extern inline void mbedtls_put_unaligned_uint64(void *p, uint64_t x);
