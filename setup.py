from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="power_scraper",
    version="0.0.1",
    author="Arin Khare",
    author_email="arinmkhare@gmail.com",
    description="Scrapes powerschool to return grades and info about specific classes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lol-cubes/power-scraper",
    package=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        "selenium"
    ]
)