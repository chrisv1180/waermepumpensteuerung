# -*- coding: utf-8 -*-
import setuptools
import re

requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()

version = ''
with open('waermepumpensteuerung/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

long_description = ""
with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="waermepumpensteuerung",
    version=version,
    author="Christian V.",
    author_email="chrisv1180-waermepumpensteuerung@yahoo.com",
    description="Controller for SG-Ready controlled heatpump with production and comsumption data in InfluxDB ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chrisv1180/waermepumpensteuerung",
    packages=["waermepumpensteuerung"],
    license="MIT",
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)