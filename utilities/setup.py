from setuptools import setup, find_packages

setup(
    name="pulumi-utilities",
    version="1.0.0",
    description="Common utilities and configurations for Pulumi monorepo",
    packages=find_packages(),
    install_requires=[
        "pulumi>=3.0.0",
        "pulumi-kubernetes>=4.0.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords=["pulumi", "utilities", "kubernetes"],
    author="",
    license="MIT",
)
