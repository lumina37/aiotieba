////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  WjCryptLib_Aes
//
//  Implementation of AES block cipher. This implementation was modified from LibTomCrypt written by Tom St Denis
//  (https://github.com/libtom). Modified by WaterJuice retaining Public Domain license.
//  Derived from Public Domain source by original authors:
//      Vincent Rijmen <vincent.rijmen@esat.kuleuven.ac.be>
//      Antoon Bosselaers <antoon.bosselaers@esat.kuleuven.ac.be>
//      Paulo Barreto <paulo.barreto@terra.com.br>
//
//  AES is a block cipher that operates on 128 bit blocks. Encryption an Decryption routines use an AesContext which
//  must be initialised with the key. An AesContext can be initialised with a 128, 192, or 256 bit key. Use the
//  AesInitialise[n] functions to initialise the context with the key. Once an AES context is initialised its contents
//  are not changed by the encrypting and decrypting functions. A context only needs to be initialised once for any
//  given key and the context may be used by the encrypt/decrypt functions in simultaneous threads.
//  All operations are performed BYTE wise and this implementation works in both little and endian processors.
//  There are no alignment requirements with the keys and data blocks.
//
//  This is free and unencumbered software released into the public domain - December 2017 waterjuice.org
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#pragma once

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  IMPORTS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <stdint.h>

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  TYPES
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#define AES_KEY_SIZE_128        16
#define AES_KEY_SIZE_192        24
#define AES_KEY_SIZE_256        32
#define AES_BLOCK_SIZE          16

// AesContext - This must be initialised using AesInitialise128, AesInitialise192 or AesInitialise256
// Do not modify the contents of this structure directly.
typedef struct
{
    uint32_t        eK[60];
    uint32_t        dK[60];
    uint_fast32_t   Nr;
} AesContext;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  PUBLIC FUNCTIONS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  AesInitialise
//
//  Initialises an AesContext with an AES Key. KeySize must be 16, 24, or 32 (for 128, 192, or 256 bit key size)
//  Returns 0 if successful, or -1 if invalid KeySize provided
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
int
    AesInitialise
    (
        AesContext*         Context,                // [out]
        void const*         Key,                    // [in]
        uint32_t            KeySize                 // [in]
    );

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  AesEncrypt
//
//  Performs an AES encryption of one block (128 bits) with the AesContext initialised with one of the functions
//  AesInitialise[n]. Input and Output can point to same memory location, however it is more efficient to use
//  AesEncryptInPlace in this situation.
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void
    AesEncrypt
    (
        AesContext const*   Context,                    // [in]
        uint8_t const       Input [AES_BLOCK_SIZE],     // [in]
        uint8_t             Output [AES_BLOCK_SIZE]     // [out]
    );

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  AesDecrypt
//
//  Performs an AES decryption of one block (128 bits) with the AesContext initialised with one of the functions
//  AesInitialise[n]. Input and Output can point to same memory location, however it is more efficient to use
//  AesDecryptInPlace in this situation.
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void
    AesDecrypt
    (
        AesContext const*   Context,                    // [in]
        uint8_t const       Input [AES_BLOCK_SIZE],     // [in]
        uint8_t             Output [AES_BLOCK_SIZE]     // [out]
    );

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  AesEncryptInPlace
//
//  Performs an AES encryption of one block (128 bits) with the AesContext initialised with one of the functions
//  AesInitialise[n]. The encryption is performed in place.
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void
    AesEncryptInPlace
    (
        AesContext const*   Context,                    // [in]
        uint8_t             Block [AES_BLOCK_SIZE]      // [in out]
    );

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  AesDecryptInPlace
//
//  Performs an AES decryption of one block (128 bits) with the AesContext initialised with one of the functions
//  AesInitialise[n]. The decryption is performed in place.
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void
    AesDecryptInPlace
    (
        AesContext const*   Context,                    // [in]
        uint8_t             Block [AES_BLOCK_SIZE]      // [in out]
    );
