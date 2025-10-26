from setuptools import setup, find_packages

setup(
    name="pulumi-grafana-helm",
    version="1.0.0",
    description="Pulumi package for deploying Grafana using Helm",
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
    keywords=["pulumi", "grafana", "helm", "kubernetes"],
    author="",
    license="MIT",
)
