from setuptools import setup, find_packages
import shutil


setup(
    name="bkang",
    version="0.1.0",
    author="Anguelos Nicolaou",
    author_email="anguelos.nicolaou@gmail.com",
    description="A pruner for backup snapshots.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/anguelos/bkang",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=["fargv>=0.1.0", "toml"],
    entry_points={
        "console_scripts": [
            "bkang-prune=bkang.datename:list_prune_main",
            "bkang-sync=bkang.datename:sync_current_main",
            "bkang-snapshot=bkang.datename:take_snapshot_main",
            "bkang-config=bkang.config:config_main",
            "bkang-setup=bkang.config:setup_main",
        ],
    },
)