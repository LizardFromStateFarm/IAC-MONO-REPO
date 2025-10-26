from setuptools import setup, find_packages

setup(
    name="pulumi-metrics-server-helm",
    version="1.0.0",
    description="Pulumi package for deploying Kubernetes metrics server using Helm",
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
    keywords=["pulumi", "metrics-server", "helm", "kubernetes"],
    author="",
    license="MIT",
)
