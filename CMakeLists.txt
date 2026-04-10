cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

if (NOT SKBUILD_PROJECT_NAME)
    set(SKBUILD_PROJECT_NAME "aiotieba")
endif ()

if (NOT SKBUILD_PROJECT_VERSION)
    set(SKBUILD_PROJECT_VERSION 0)
endif ()

project(${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION})

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)

add_subdirectory(src/${SKBUILD_PROJECT_NAME}/helper/crypto)
