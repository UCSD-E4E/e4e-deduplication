#include <cstdint>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>

#include <pybind11/pybind11.h>
#include "hash-library/sha256.h"
#include "hash-library/sha1.h"
#include "hash-library/sha3.h"
#include "hash-library/md5.h"
#include "hash-library/crc32.h"

typedef enum HashType
{
    HASH_CRC32 = 0,
    HASH_MD5,
    HASH_SHA1,
    HASH_SHA256,
    HASH_SHA3
} Hash_t;

std::string compute_SHA256(std::ifstream &handle, uint8_t *buffer, const std::size_t buffer_size)
{
    SHA256 hasher;
    do
    {
        handle.read(reinterpret_cast<char *>(buffer), buffer_size);
        hasher.add(buffer, handle.gcount());
    } while (handle.good());
    return hasher.getHash();
}
std::string compute_MD5(std::ifstream &handle, uint8_t *buffer, const std::size_t buffer_size)
{
    MD5 hasher;
    do
    {
        handle.read(reinterpret_cast<char *>(buffer), buffer_size);
        hasher.add(buffer, handle.gcount());
    } while (handle.good());
    return hasher.getHash();
}
std::string compute_SHA1(std::ifstream &handle, uint8_t *buffer, const std::size_t buffer_size)
{
    SHA1 hasher;
    do
    {
        handle.read(reinterpret_cast<char *>(buffer), buffer_size);
        hasher.add(buffer, handle.gcount());
    } while (handle.good());
    return hasher.getHash();
}
std::string compute_CRC32(std::ifstream &handle, uint8_t *buffer, const std::size_t buffer_size)
{
    CRC32 hasher;
    do
    {
        handle.read(reinterpret_cast<char *>(buffer), buffer_size);
        hasher.add(buffer, handle.gcount());
    } while (handle.good());
    return hasher.getHash();
}
std::string compute_SHA3(std::ifstream &handle, uint8_t *buffer, const std::size_t buffer_size)
{
    SHA3 hasher;
    do
    {
        handle.read(reinterpret_cast<char *>(buffer), buffer_size);
        hasher.add(buffer, handle.gcount());
    } while (handle.good());
    return hasher.getHash();
}

std::string (*compute_fn[])(std::ifstream &, uint8_t *, const std::size_t) = {
    compute_CRC32,
    compute_MD5,
    compute_SHA1,
    compute_SHA256,
    compute_SHA3};

namespace py = pybind11;
std::string compute_digest(Hash_t hash_type, std::string path)
{
    const std::size_t BUFFER_SIZE = 2 * 1024 * 1024;
    // const std::size_t BUFFER_SIZE = 1;
    std::size_t n_bytes = 0;
    std::ifstream handle(path, std::ios::binary);
    uint8_t *buffer = new uint8_t[BUFFER_SIZE];
    if (!handle.is_open())
    {
        throw std::exception();
    }
    std::string digest = compute_fn[hash_type](handle, buffer, BUFFER_SIZE);
    handle.close();
    delete[] buffer;
    return digest;
}

PYBIND11_MODULE(file_hasher, m)
{
    py::enum_<HashType>(m, "HashType")
        .value("CRC32", HASH_CRC32)
        .value("MD5", HASH_MD5)
        .value("SHA1", HASH_SHA1)
        .value("SHA256", HASH_SHA256)
        .export_values();
    m.def("compute_digest", &compute_digest);
}