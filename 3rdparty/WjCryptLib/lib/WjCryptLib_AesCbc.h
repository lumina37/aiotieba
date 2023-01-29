////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  WjCryptLib_AesCbc
//
//  Implementation of AES CBC cipher.
//
//  Depends on: CryptoLib_Aes
//
//  AES CBC is a cipher using AES in Cipher Block Chaining mode. Encryption and decryption must be performed in
//  multiples of the AES block size (128 bits).
//  This implementation works on both little and big endian architectures.
//
//  This is free and unencumbered software released into the public domain - March 2018 waterjuice.org
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#pragma once

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  IMPORTS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <stdint.h>
#include "WjCryptLib_Aes.h"

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  TYPES
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#define AES_CBC_IV_SIZE             AES_BLOCK_SIZE

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  TYPES
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// AesCbcContext
// Do not modify the contents of this structure directly.
typedef struct
{
    AesContext      Aes;
    uint8_t         PreviousCipherBlock [AES_BLOCK_SIZE];
} AesCbcContext;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  PUBLIC FUNCTIONS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  AesCbcInitialise
//
//  Initialises an AesCbcContext with an already initialised AesContext and a IV. This function can quickly be used
//  to change the IV without requiring the more lengthy processes of reinitialising an AES key.
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void
    AesCbcInitialise
    (
        AesCbcContext*      Context,                // [out]
        AesContext const*   InitialisedAesContext,  // [in]
        uint8_t const       IV [AES_CBC_IV_SIZE]    // [in]
    );

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  AesCbcInitialiseWithKey
//
//  Initialises an AesCbcContext with an AES Key and an IV. This combines the initialising an AES Context and then
//  running AesCbcInitialise. KeySize must be 16, 24, or 32 (for 128, 192, or 256 bit key size)
//  Returns 0 if successful, or -1 if invalid KeySize provided
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
int
    AesCbcInitialiseWithKey
    (
        AesCbcContext*      Context,                // [out]
        uint8_t const*      Key,                    // [in]
        uint32_t            KeySize,                // [in]
        uint8_t const       IV [AES_CBC_IV_SIZE]    // [in]
    );

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  AesCbcEncrypt
//
//  Encrypts a buffer of data using an AES CBC context. The data buffer must be a multiple of 16 bytes (128 bits)
//  in size. The "position" of the context will be advanced by the buffer amount. A buffer can be encrypted in one
//  go or in smaller chunks at a time. The result will be the same as long as data is fed into the function in the
//  same order.
//  InBuffer and OutBuffer can point to the same location for in-place encrypting.
//  Returns 0 if successful, or -1 if Size is not a multiple of 16 bytes.
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
int
    AesCbcEncrypt
    (
        AesCbcContext*      Context,                // [in out]
        void const*         InBuffer,               // [in]
        void*               OutBuffer,              // [out]
        uint32_t            Size                    // [in]
    );

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  AesCbcDecrypt
//
//  Decrypts a buffer of data using an AES CBC context. The data buffer must be a multiple of 16 bytes (128 bits)
//  in size. The "position" of the context will be advanced by the buffer amount.
//  InBuffer and OutBuffer can point to the same location for in-place decrypting.
//  Returns 0 if successful, or -1 if Size is not a multiple of 16 bytes.
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
int
    AesCbcDecrypt
    (
        AesCbcContext*      Context,                // [in out]
        void const*         InBuffer,               // [in]
        void*               OutBuffer,              // [out]
        uint32_t            Size                    // [in]
    );

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  AesCbcEncryptWithKey
//
//  This function combines AesCbcInitialiseWithKey and AesCbcEncrypt. This is suitable when encrypting data in one go
//  with a key that is not going to be reused.
//  InBuffer and OutBuffer can point to the same location for inplace encrypting.
//  Returns 0 if successful, or -1 if invalid KeySize provided or BufferSize not a multiple of 16 bytes.
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
int
    AesCbcEncryptWithKey
    (
        uint8_t const*      Key,                    // [in]
        uint32_t            KeySize,                // [in]
        uint8_t const       IV [AES_CBC_IV_SIZE],   // [in]
        void const*         InBuffer,               // [in]
        void*               OutBuffer,              // [out]
        uint32_t            BufferSize              // [in]
    );

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  AesCbcDecryptWithKey
//
//  This function combines AesCbcInitialiseWithKey and AesCbcDecrypt. This is suitable when decrypting data in one go
//  with a key that is not going to be reused.
//  InBuffer and OutBuffer can point to the same location for inplace decrypting.
//  Returns 0 if successful, or -1 if invalid KeySize provided or BufferSize not a multiple of 16 bytes.
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
int
    AesCbcDecryptWithKey
    (
        uint8_t const*      Key,                    // [in]
        uint32_t            KeySize,                // [in]
        uint8_t const       IV [AES_CBC_IV_SIZE],   // [in]
        void const*         InBuffer,               // [in]
        void*               OutBuffer,              // [out]
        uint32_t            BufferSize              // [in]
    );
