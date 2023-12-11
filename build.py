from pathlib import Path

from pybind11.setup_helpers import (ParallelCompile, Pybind11Extension,
                                    build_ext, naive_recompile)


def build(setup_kwargs):
    ParallelCompile("NPY_NUM_BUILD_JOBS", needs_recompile=naive_recompile).install()
    src_dir = Path('file_hasher/src/')
    src_files = list(src_dir.rglob('*.c*'))
    ext_modules = [
        Pybind11Extension('file_hasher',
                          [str(src) for src in src_files if src.name != 'digest.cpp' and src.parent.name != 'tests'],
                          extra_compile_args=['-O3'],
                          language='c++',
                          cxx_std=11)
    ]
    setup_kwargs.update({
        'ext_modules': ext_modules,
        'cmd_class': {'build_ext': build_ext},
        'zip_safe': False
    })
