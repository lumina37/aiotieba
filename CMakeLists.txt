cmake_minimum_required(VERSION 3.12 FATAL_ERROR)

project(${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION})

find_package(Python COMPONENTS Interpreter Development REQUIRED)

add_subdirectory(${SKBUILD_PROJECT_NAME}/helper/crypto)