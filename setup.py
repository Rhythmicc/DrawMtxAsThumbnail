from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy

with open("README.md", "r") as fh:
    long_description = fh.read()
VERSION = "0.0.37"

module = Extension(
    "MtxDrawer.MtxReader",
    sources=["MatGen/MatGen.pyx", "MatGen/_MatGen.c"],
    extra_compile_args=["-ffast-math"],
    include_dirs=[numpy.get_include()],
    language="c"
)

setup(
    name='MtxDrawer',
    version=VERSION,
    description='Draw Mtx As Thumbnail',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    author='RhythmLian',
    author_email='RhythmLian@outlook.com',
    url="https://github.com/Rhythmicc/DrawMtxAsThumbnail",
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    ext_modules=cythonize(module),
    install_requires=['numpy', 'matplotlib', 'Qpro', 'cython'],
    entry_points={
        'console_scripts': [
            'mtx-drawer = MtxDrawer.main:main'
        ]
    },
)
