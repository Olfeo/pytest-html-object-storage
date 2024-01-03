#!/usr/bin/env python
import glob

from setuptools import setup, find_packages

from pytest_html_object_storage import __version__

data_files = []
directories = glob.glob("pytest_html_object_storage/")
for directory in directories:
    files = glob.glob(directory + "*/*")
    data_files.append((directory, files))


setup(
    name="pytest-html-object-storage",
    version=__version__,
    url="https://github.com/treussart/pytest-html-object-storage",
    license="BSD",
    description="Pytest report plugin for send HTML report on object-storage",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="py.test pytest zulip report",
    author="mtreussart",
    author_email="matthieu@treussart.com",
    packages=find_packages(
        include=["pytest_html_object_storage"],
    ),
    data_files=data_files,
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "pytest-html",
        "minio",
        "python-keystoneclient",
        "python-swiftclient",
    ],
    entry_points={
        "pytest11": ["html_object_storage = pytest_html_object_storage.plugin"]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
