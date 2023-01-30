import os
import subprocess
from setuptools import setup
import setuptools.command.build_py


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class iverilog(setuptools.command.build_py.build_py):
    """Install iverilog"""

    def run(self):
        sp = subprocess.Popen(
            ["sudo", "apt", "install", "iverilog"], shell=True, stdin=subprocess.PIPE)


setup(
    cmdclass={
        'iverilog': iverilog
    },
    name="interfacer",
    version="0.0.1",
    packages=['interfacer'],
    package_data={'interfacer': [
        'protocols/protocol.json',
        'templates/*',
    ]},

    author="Alex Bucknall",
    author_email="alex.bucknall@gmail.com",
    description=(
        "Interfacer is a library for interfacing RTL with SoC designs, primarily for FPGA Partial Reconfiguration development"),
    license="MIT",
    keywords=["verilog", "EDA", "hdl", "rtl", "synthesis",
              "FPGA", "Xilinx", "Partial Reconfiguration"],
    url="https://github.com/accl-kaust/interfacer",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU GPLv3 License",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: Utilities",
    ],
    install_requires=[
        'wheel',
        'pyverilog==1.2.1',
        'colorlog',
        'ast2json==0.2.1',
        'edalize',
        'pytest',
        'lxml',
        'markdown-wavedrom',
        'mkdocs>=1.1',
        'mkdocs-wavedrom-plugin==0.1.1',
        'mkdocs-bibtex==0.2.3',
        'mkdocstrings',
        'mkdocs-material',
        'pymdown-extensions',
        'pytest>=3.3.0',
        'Jinja2 >=2.8, !=2.11.0, !=2.11.1',
    ],
    tests_require=[
        'vunit_hdl>=4.0.8'
    ],
    # Supported Python versions: 3.5+
    python_requires=">=3.5, <4",
)
