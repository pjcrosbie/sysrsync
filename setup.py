import setuptools

from sysrsync import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sysrsync",
    version=__version__,
    author="Gabriel Chamon, pjc minor fork changes ",
    author_email="gchamon@live.com",
    description="Python module that wraps system calls to rsync",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pjcrosbie/sysrsync",
    py_modules=["sysrsync"],
    platforms='any',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>3.5'
)
