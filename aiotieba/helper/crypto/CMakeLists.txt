set(TBC_INCLUDE_DIRS "include")
file(GLOB_RECURSE TBC_SOURCES "*.c")

Python3_add_library(crypto MODULE ${TBC_SOURCES})
target_include_directories(crypto PUBLIC ${TBC_INCLUDE_DIRS})

install(TARGETS crypto DESTINATION ${SKBUILD_PROJECT_NAME}/helper/crypto)
