'''Utility to sort a file line by line
'''
import math
from heapq import merge as heap_merge
from multiprocessing import Condition, Event, Process, Queue, cpu_count
from pathlib import Path
from queue import Empty
from shutil import copy
from tempfile import TemporaryDirectory
from typing import Iterable


class PoolMerger:
    """Parallel Process Merger

    """
    # pylint: disable=too-few-public-methods
    # Runner

    def __init__(self):
        self.final_size = 0
        self.final_path = None

    def run(self, partitions: Iterable[Path], final_size: int) -> Path:
        """Runs the pool merger over the specified partitions

        Args:
            partitions (Iterable[Path]): Specified partitions
            final_size (int): Final size of merged file

        Returns:
            Path: Path of final file
        """
        self.final_size = final_size
        merger_terminate = Event()
        merger_condition = Condition()
        merge_queue = Queue()
        result_queue = Queue()

        merger_terminate.clear()
        workers = [Process(target=self._merger, kwargs={
            'condition': merger_condition,
            'queue': merge_queue,
            'terminate': merger_terminate,
            'result_queue': result_queue
        }, name=f'merge_worker_{thread_idx:03d}') for thread_idx in range(cpu_count())]
        for worker in workers:
            worker.start()
        with merger_condition:
            for partition in partitions:
                merge_queue.put(partition)
            merger_condition.notify_all()
        for worker in workers:
            worker.join()
        return result_queue.get()

    def _merger(self, condition: Condition, queue: Queue, terminate: Event, result_queue: Queue):
        while True:
            with condition:
                if queue.empty() and not terminate.is_set():
                    condition.wait(timeout=1)
                if terminate.is_set() and queue.empty():
                    return
                try:
                    part1: Path = queue.get(block=False)
                except Empty:
                    continue
                if part1.stat().st_size == self.final_size:
                    terminate.set()
                    condition.notify_all()
                    result_queue.put(part1)
                    return
                if queue.empty():
                    queue.put(part1)
                    condition.wait(timeout=5)
                    continue
                part2: Path = queue.get(block=False)
            output_path = part1.parent.joinpath(f'{part1.stem}_{part2.stem}')
            with open(part1, 'r', encoding='utf-8') as handle1, \
                open(part2, 'r', encoding='utf-8') as handle2, \
                    open(output_path, 'w', encoding='utf-8') as output_handle:
                output_handle.writelines(heap_merge(handle1, handle2))
            part1.unlink()
            part2.unlink()
            with condition:
                queue.put(output_path)
                condition.notify()


def sort_file(src_path: Path, sorted_path: Path) -> None:
    """Sorts the file line by line

    Args:
        src_path (Path): Source Path
        sorted_path (Path): Final Path

    """
    file_size = src_path.stat().st_size
    partition_size = min(math.ceil(file_size / cpu_count()), 1024*1024*1024)
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        partitions = []
        with open(src_path, 'r', encoding='utf-8') as src_handle:
            partition_idx = 0
            while lines := src_handle.readlines(partition_size):
                partition_path = temp_dir.joinpath(f'{partition_idx}')
                with open(partition_path, 'w', encoding='utf-8') as partition_handle:
                    partition_handle.writelines(sorted(lines))
                partition_idx += 1
                partitions.append(partition_path)
        pool = PoolMerger()
        sorted_file = pool.run(partitions, file_size)
        copy(sorted_file, sorted_path)
