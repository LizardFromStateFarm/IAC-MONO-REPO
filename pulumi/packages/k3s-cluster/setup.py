from setuptools import setup, find_packages

setup(
    name="k3s-cluster",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pulumi>=3.0.0",
        "pulumi-kubernetes>=4.0.0",
        "pulumi-command>=0.9.0",
        "pyyaml>=6.0",
    ],
    python_requires=">=3.8",
)
