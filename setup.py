import os
from setuptools import setup, find_packages


def read(file_name: str) -> str:
    __file = os.path.join(os.path.dirname(__file__), file_name)
    if os.path.exists(__file):
        with open(__file) as f:
            return f.read()
    else:
        return ""


def get_version() -> str:
    main_ns = {}
    ver_path = os.path.join(os.path.dirname(__file__), 'version.py')
    with open(ver_path) as ver_file:
        exec(ver_file.read(), main_ns)
    return main_ns['__version__']


setup(
    name="AgendaMD",
    version="0.4.dev0",
    author="Ricardo Állan",
    author_email="ricardoallancosta@hotmail.com",
    description="A Calendar App developed in Python, with Kivy framework and google Material Design.",
    license="Apache 2.0",
    url="https://github.com/RicardoDazzling/agendamd",
    packages=find_packages(),
    long_description=read('README'),
    classifiers=[
        "Development Status :: 2 - Pré-alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: Portuguese (Brazilian)",
        "Programming Language :: Python :: 3.9",
    ],
)
