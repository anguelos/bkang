from setuptools import setup, find_packages
import shutil
import sys



data_files = [
    ("share/applications", ["bkang/resources/bkang-browse.desktop"]),
]

# Add each icon size to the correct hicolor path
for size in [16, 24, 32, 48, 64, 128, 256, 512]:
    icon_path = f"bkang/resources/icons/{size}x{size}/bkang-browse.png"
    install_path = f"share/icons/hicolor/{size}x{size}/apps"
    data_files.append((install_path, [icon_path]))

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
    install_requires=["fargv", "toml", "PySide6", "python-crontab"],
    entry_points={
        "console_scripts": [
            "bkang-prune=bkang.datename:list_prune_main",
            "bkang-sync=bkang.datename:sync_current_main",
            "bkang-snapshot=bkang.datename:take_snapshot_main",
            "bkang-config=bkang.config:config_main",
            "bkang-setup=bkang.config:setup_main",
        ],
        "gui_scripts": [
            "bkang-browse=bkang.gui_browser:main_browse_gui",
        ],
    },
    data_files=data_files,
    include_package_data=True,
    package_data={
        "bkang": [
            "resources/icons/*.png",
            "resources/bkang-browse.desktop",
            "resources/default_config.toml",
        ]
    },
)