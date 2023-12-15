'''Parallel Hasher
'''
import re
from multiprocessing import Condition, Event, Lock, Queue, cpu_count
from pathlib import Path
from queue import Empty
from threading import Thread
from typing import Callable, Iterable

from tqdm import tqdm

from pyfilehash.hasher import compute_sha256


def _hasher(condition: Condition,
            job_queue: Queue,
            terminate: Event,
            result_queue: Queue,
            result_condition: Condition,
            hash_fn: Callable[[Path], str]) -> None:
    # pylint: disable=too-many-arguments
    # This is a general hasher
    while True:
        with condition:
            if job_queue.empty() and not terminate.is_set():
                condition.wait(timeout=1)
            if terminate.is_set() and job_queue.empty():
                return
        try:
            job: Path = job_queue.get(block=False)
        except Empty:
            continue
        digest = hash_fn(job)
        result_queue.put((job, digest))
        with result_condition:
            result_condition.notify()


class ParallelHasher:
    """Parallel Hashing Class
    """
    # pylint: disable=too-few-public-methods
    # This is meant to be a single method class

    def __init__(self,
                 process_fn: Callable[[Path, str], None],
                 ignore_pattern: re.Pattern,
                 *,
                 hash_fn: Callable[[Path], str] = compute_sha256):
        """Initializes the Parallel Hashing Class

        Args:
            process_fn (Callable[[Path, str], None]): Processing Function to retrieve the results
            ignore_pattern (re.Pattern): Regex pattern to use for ignore
        """
        self._process_fn = process_fn
        self._ignore_pattern = ignore_pattern
        self._pb = None
        self._pb_lock = Lock()
        self._hash_fn = hash_fn

    def run(self, paths: Iterable[Path], n_iter: int):
        """Runs the parallel hasher

        Args:
            paths (Iterable[Path]): Iterable of paths to hash
            n_iter (int): Number of iterations expected
        """
        processor_terminate = Event()
        result_condition = Condition()
        job_terminate = Event()
        job_condition = Condition()
        job_queue = Queue()
        result_queue = Queue()
        self._pb = tqdm(total=n_iter)
        job_terminate.clear()
        processor_terminate.clear()
        accumulator = Thread(target=self._result_accumulator, kwargs={
            'result_condition': result_condition,
            'result_queue': result_queue,
            'processor_terminate': processor_terminate
        })
        accumulator.start()
        processes = [Thread(target=_hasher, kwargs={
            'condition': job_condition,
            'job_queue': job_queue,
            'terminate': job_terminate,
            'result_queue': result_queue,
            'result_condition': result_condition,
            'hash_fn': self._hash_fn
        })
            for _ in range(cpu_count())]
        for process in processes:
            process.start()
        for path in paths:
            if self._ignore_pattern and self._ignore_pattern.search(path.as_posix()):
                with self._pb_lock:
                    self._pb.update(n=1)
                continue
            if not path.is_file():
                with self._pb_lock:
                    self._pb.update(n=1)
                continue
            with self._pb_lock:
                self._pb.update(n=0.5)
            with job_condition:
                job_queue.put(path)
                job_condition.notify()
        job_terminate.set()
        with job_condition:
            job_condition.notify_all()
        for process in processes:
            process.join()
        processor_terminate.set()

        with result_condition:
            result_condition.notify_all()
        accumulator.join()
        job_queue.close()
        result_queue.close()
        self._pb.close()

    def _result_accumulator(self,
                            result_condition: Condition,
                            result_queue: Queue,
                            processor_terminate: Event) -> None:
        while True:
            with result_condition:
                if result_queue.empty() and not processor_terminate.is_set():
                    result_condition.wait(timeout=1)
                if processor_terminate.is_set() and result_queue.empty():
                    return
            try:
                pair = result_queue.get()
            except Empty:
                continue
            path, digest = pair
            with self._pb_lock:
                self._pb.update(n=0.5)
            self._process_fn(path, digest)
