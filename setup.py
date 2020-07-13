import setuptools
from pip._internal.req import parse_requirements

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_reqs = parse_requirements("requirements.txt", session="hack")
try:
    reqs = [str(ir.req) for ir in install_reqs]
except AttributeError:
    reqs = [str(ir.requirement) for ir in install_reqs]

setuptools.setup(
    name="pedia-cloud",
    version="0.0.9",
    author="SheiUn",
    author_email="develop@sheiun.me",
    description="A third-party Python API for Pedia Cloud Dictionary",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sheiun/pedia-cloud",
    packages=setuptools.find_packages(),
    install_requires=reqs,
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
