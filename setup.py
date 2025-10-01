from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Define the Cython extension
module = Extension(
    "MtxDrawer.MtxReader",
    sources=["MatGen/MatGen.pyx", "MatGen/_MatGen.c"],
    extra_compile_args=["-ffast-math"],
    include_dirs=[numpy.get_include()],
    language="c"
)

# Setup with minimal configuration (most config is now in pyproject.toml)
setup(
    ext_modules=cythonize(module, compiler_directives={'language_level': "3"}),
    zip_safe=False,
)
