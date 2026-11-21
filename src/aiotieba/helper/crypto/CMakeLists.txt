set(TBC_INCLUDE_DIRS ./csrc)
file(GLOB_RECURSE TBC_SOURCES *.c)

Python3_add_library(crypto MODULE WITH_SOABI ${TBC_SOURCES})
target_include_directories(crypto PUBLIC ${TBC_INCLUDE_DIRS})

if (MSVC)
    target_compile_options(crypto PRIVATE /utf-8)
endif ()

install(TARGETS crypto DESTINATION ${SKBUILD_PROJECT_NAME}/helper/crypto)
