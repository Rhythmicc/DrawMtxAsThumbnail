from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
VERSION = "0.0.15"

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
    install_requires=['numpy', 'scipy', 'matplotlib', 'Qpro'],
    entry_points={
        'console_scripts': [
            'mtx-drawer = MtxDrawer.main:main'
        ]
    },
)
