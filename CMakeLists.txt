cmake_minimum_required(VERSION 3.25)
project(file_hasher)
add_executable(file_hasher_test
    file_hasher/src/hasher.cpp
    file_hasher/src/hash-library/sha256.cpp
    file_hasher/src/hash-library/sha1.cpp
    file_hasher/src/hash-library/sha3.cpp
    file_hasher/src/hash-library/md5.cpp
    file_hasher/src/hash-library/crc32.cpp
)
set_property(TARGET file_hasher_test PROPERTY CXX_STANDARD 17)
target_compile_definitions(file_hasher_test
    PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO}
    USE_PYBIND11=0
)