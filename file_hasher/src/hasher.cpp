#include <cstdint>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <thread>
#include <queue>
#include <utility>
#include <functional>
#include <filesystem>

#if USE_PYBIND11
#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/pytypes.h>
#include <pybind11/embed.h>
#include <Python.h>
#endif

#include "hash-library/sha256.h"
#include "hash-library/sha1.h"
#include "hash-library/sha3.h"
#include "hash-library/md5.h"
#include "hash-library/crc32.h"

#if USE_PYBIND11
namespace py = pybind11;
#endif

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
#if USE_PYBIND11
    py::gil_scoped_release release;
#endif
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
#if USE_PYBIND11
    py::gil_scoped_release release;
#endif
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
#if USE_PYBIND11
    py::gil_scoped_release release;
#endif
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
#if USE_PYBIND11
    py::gil_scoped_release release;
#endif
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
#if USE_PYBIND11
    py::gil_scoped_release release;
#endif
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

class ParallelHasher
{
private:
    Hash_t hash_type;
    std::function<void(std::string, std::string)> process_fn;
    int n_cpus;

    bool should_terminate = false;
    std::mutex job_queue_mutex;
    std::condition_variable job_mutex_condition;
    std::mutex result_queue_mutex;
    std::condition_variable result_mutex_condition;
    std::vector<std::thread> hash_workers;
    std::thread accumulator;
    std::queue<std::string> jobs;
    std::queue<std::pair<std::string, std::string>> results;

    void result_accumulator(void)
    {

        while (true)
        {
            std::pair<std::string, std::string> result;
            {
                std::unique_lock<std::mutex> lock(result_queue_mutex);
                result_mutex_condition.wait(lock, [this]
                                            { return !results.empty() || should_terminate; });
                if (should_terminate)
                {
                    std::cout << "Accumulator returning" << std::endl;
                    return;
                }
                result = results.front();
                results.pop();
            }
            {

                std::cout << "process_fn" << std::endl;
                py::gil_scoped_acquire acquire{};
                process_fn(result.first, result.second);
                std::cout << "process_fn done" << std::endl;
            }
        }
    };
    void worker_loop(void)
    {
        while (true)
        {
            std::string path_to_hash;
            {
                std::unique_lock<std::mutex> lock(job_queue_mutex);
                job_mutex_condition.wait(lock, [this]
                                         { return !jobs.empty() || should_terminate; });
                if (should_terminate)
                {
                    std::cout << "Worker  returning" << std::endl;
                    return;
                }
                path_to_hash = jobs.front();
                jobs.pop();
            }
            std::string digest = compute_digest(hash_type, path_to_hash);
            {
                std::unique_lock<std::mutex> lock(result_queue_mutex);
                results.push(std::pair<std::string, std::string>(path_to_hash, digest));
            }
            result_mutex_condition.notify_one();
        }
    };

public:
    ParallelHasher(const std::function<void(std::string, std::string)> process_fn,
                   Hash_t hash_type,
                   int n_cpus) : hash_type(hash_type), n_cpus(n_cpus), process_fn(process_fn){};
    void run(int n_iter)
    {
        int n_workers = n_cpus - 1;
        if (n_workers < 1)
        {
            n_workers = 1;
        }
        for (uint32_t idx = 0; idx < n_workers; ++idx)
        {
            hash_workers.emplace_back(std::thread(&ParallelHasher::worker_loop, this));
        }
        accumulator = std::thread(&ParallelHasher::result_accumulator, this);
    };
    void put(std::string path)
    {
        {
            std::unique_lock<std::mutex> lock(job_queue_mutex);
            jobs.push(path);
        }
        job_mutex_condition.notify_one();
    };
    void join(void)
    {
        {
            std::unique_lock<std::mutex> lock(job_queue_mutex);
            std::unique_lock<std::mutex> rlock(result_queue_mutex);
            should_terminate = true;
            std::cout << jobs.size() << std::endl;
        }
        job_mutex_condition.notify_all();
        result_mutex_condition.notify_all();
        for (std::thread &active_thread : hash_workers)
        {
            active_thread.join();
        }
        accumulator.join();
        hash_workers.clear();
    };
};

#if USE_PYBIND11
PYBIND11_MODULE(file_hasher, m)
{
    py::enum_<Hash_t>(m, "HashType")
        .value("CRC32", HASH_CRC32)
        .value("MD5", HASH_MD5)
        .value("SHA1", HASH_SHA1)
        .value("SHA256", HASH_SHA256)
        .export_values();
    m.def("compute_digest", &compute_digest);

    py::class_<ParallelHasher>(m, "ParallelHasher")
        .def(py::init<const std::function<void(std::string, std::string)>,
                      Hash_t,
                      int>())
        .def("run", &ParallelHasher::run, py::call_guard<py::gil_scoped_release>())
        .def("put", &ParallelHasher::put, py::call_guard<py::gil_scoped_release>())
        .def("join", &ParallelHasher::join, py::call_guard<py::gil_scoped_release>());
}
#else

void test_process_fn(std::string path, std::string digest)
{
    std::cout << "File: " << path << " -> " << digest << std::endl;
}

int main(void)
{
    ParallelHasher hasher(std::function<void(std::string, std::string)>(test_process_fn), HashType::HASH_SHA256, 16);
    std::size_t n_files = 0;
    for (const auto &dir_entry : std::filesystem::recursive_directory_iterator("D:\\workspace\\e4e\\e4e_tools\\e4e-deduplication"))
    {
        n_files++;
    }
    std::cout << "Processing " << n_files << " files" << std::endl;
    hasher.run(n_files);
    for (const auto &dir_entry : std::filesystem::recursive_directory_iterator("D:\\workspace\\e4e\\e4e_tools\\e4e-deduplication"))
    {
        if (!dir_entry.is_regular_file())
        {
            continue;
        }
        // std::cout << "Queueing " << dir_entry << std::endl;
        hasher.put(dir_entry.path().string());
    }
    hasher.join();
}
#endif