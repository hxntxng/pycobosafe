from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pycobosafe",
    description="A Python SDK for interactions with Cobo Safe contracts.",
    url="https://github.com/coboglobal/pycobosafe",
    author="Cobo Global",
    version="0.0.1",
    packages=find_packages(),
    package_data={"pycobosafe": ["abi/*.json"]},
    python_requires=">=3.8",
    install_requires=[
        "eth_abi==2.2.0",
        "eth_account==0.5.9",
        "eth_utils==1.10.0",
        "pytest==6.2.5",
        "python-dotenv==1.0.0",
        "eth_account==0.5.9",
    ],
    license="LGPL-3.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["pycobosafe = pycobosafe.main:main"]},
)
