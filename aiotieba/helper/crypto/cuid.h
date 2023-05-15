#pragma once

#include <stdint.h>

/**
 * @brief impl of TiebaLite tieba/post/utils/helios
 *
 * @param src alloc and free by user
 * @param srcSize size of src. must >= 1
 * @param dst 5 bytes. alloc and free by user
 *
 * @note 12.x loc: com.baidu.tieba.l40.a / com.baidu.tieba.pz.a
 */
void tbc_heliosHash(const unsigned char* src, size_t srcSize, unsigned char* dst);

/**
 * @brief generate `cuid_galaxy2`
 *
 * @param androidID 16 bytes. alloc and free by user
 * @param dst 42 bytes. alloc and free by user
 *
 * @note 12.x loc: com.baidu.tieba.oz.m
 */
void tbc_cuid_galaxy2(const unsigned char* androidID, unsigned char* dst);

/**
 * @brief generate `c3_aid`
 *
 * @param androidID 16 bytes. alloc and free by user
 * @param uuid 36 bytes. alloc and free by user
 * @param dst 45 bytes. alloc and free by user
 *
 * @note 12.x loc: com.baidu.tieba.r50.f
 */
void tbc_c3_aid(const unsigned char* androidID, const unsigned char* uuid, unsigned char* dst);
