#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import sys

import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as BuildExtCommand
from setuptools.command.test import test as TestCommand

from distutils.sysconfig import get_config_var, get_python_inc

import versioneer


class NumPyBuildExt(BuildExtCommand):
    def finalize_options(self):
        BuildExtCommand.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())


class PyTest(TestCommand):
    description = "Run test suite with pytest"

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


#version = versioneer.get_version()
version = '0.3.1'

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

setup_requirements = [
    "cython>=0.25.2",
    "numpy>=1.11.3",
]

install_requirements = [
    "numpy>=1.11.3",
    # TODO: put package install requirements here
]

test_requirements = [
    "pytest",
]

cmdclasses = dict()
#cmdclasses.update(versioneer.get_cmdclass())
cmdclasses["build_ext"] = NumPyBuildExt
cmdclasses["test"] = PyTest

if not (({"develop", "test"} & set(sys.argv)) or
    any([v.startswith("build") for v in sys.argv]) or
    any([v.startswith("bdist") for v in sys.argv]) or
    any([v.startswith("install") for v in sys.argv])):
    setup_requirements = []
else:
    with open("sparse_dot_topn/version.pxi", "w") as f:
        f.writelines([
            "__version__ = " + "\"" + str(version) + "\""
        ])


try:
    i = sys.argv.index("test")
    sys.argv = sys.argv[:i] + ["build_ext", "--inplace"] + sys.argv[i:]
except ValueError:
    pass


include_dirs = [
    os.path.dirname(get_python_inc()),
    get_python_inc()
]
library_dirs = list(filter(
    lambda v: v is not None,
    [get_config_var("LIBDIR")]
))

headers = []
# sources = glob.glob("src/*.pxd") + glob.glob("src/*.pyx")
libraries = []
define_macros = []
if os.name == 'nt':
    extra_compile_args = ["-Ox"]
else:
    extra_compile_args = ['-std=c++0x', '-pthread', '-O3']
cython_directives = {}
cython_line_directives = {}


if "test" in sys.argv:
    cython_directives["binding"] = True
    cython_directives["embedsignature"] = True
    cython_directives["profile"] = True
    cython_directives["linetrace"] = True
    define_macros += [
        ("CYTHON_PROFILE", 1),
        ("CYTHON_TRACE", 1),
        ("CYTHON_TRACE_NOGIL", 1),
    ]


ext_modules = [
    Extension(
        "sparse_dot_topn.sparse_dot_topn_nonthreaded",
        sources=['sparse_dot_topn/sparse_dot_topn_nonthreaded.pyx',
                 'sparse_dot_topn/sparse_dot_topn_nonthreaded.pxd',  # To check
                 'sparse_dot_topn/sparse_dot_topn_source.cpp'],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
        language="c++"
    ),
    Extension(
        "sparse_dot_topn.sparse_dot_topn_threaded",
        sources=['sparse_dot_topn/sparse_dot_topn_threaded.pyx',
                 'sparse_dot_topn/sparse_dot_topn_threaded.pxd',  # To check
                 'sparse_dot_topn/sparse_dot_topn_source.cpp',
                 'sparse_dot_topn/sparse_dot_topn_parallel.cpp'],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
        language="c++"
    )
]
for em in ext_modules:
    em.cython_directives = dict(cython_directives)
    em.cython_line_directives = dict(cython_line_directives)


setup(
    name="sparse_dot_topn",
    version=version,
    description="This package boosts a sparse matrix multiplication followed by selecting the top-n multiplication",
    long_description=readme + "\n\n" + history,
    author="Zhe Sun",
    author_email="ymwdalex@gmail.com",
    url="https://github.com/ing-bank/sparse_dot_topn",
    cmdclass=cmdclasses,
    packages=setuptools.find_packages(exclude=["tests*"]),
    include_package_data=True,
    setup_requires=setup_requirements,
    install_requires=install_requirements,
    headers=headers,
    ext_modules=ext_modules,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="sparse_dot_topn",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    tests_require=test_requirements
)
