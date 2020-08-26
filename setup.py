from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pedia-cloud",
    version="0.10.0",
    author="SheiUn",
    author_email="develop@sheiun.me",
    description="A third-party Python API for Pedia Cloud Dictionary",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sheiun/pedia-cloud",
    packages=find_packages(),
    install_requires=["requests"],
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
