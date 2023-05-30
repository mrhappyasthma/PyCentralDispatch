import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycentraldispatch",
    version="1.0.12",
    author="MrHappyAsthma",
    author_email="mrhappyasthma@gmail.com",
    description="A simple Grand Central Dispatch (GCD) inspired API for python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrhappyasthma/PyCentralDispatch",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
