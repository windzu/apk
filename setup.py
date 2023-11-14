"""
Author: wind windzu1@gmail.com
Date: 2023-11-07 17:15:41
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-11-07 17:17:17
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
"""
Author: windzu windzu1@gmail.com
Date: 2023-11-06 23:34:28
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-11-07 00:31:44
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
import sys

from setuptools import find_packages, setup

# 获取当前Python版本
current_python_version = sys.version_info


def parse_requirements(fname_list=[]):
    """Parse the package dependencies listed in a requirements list file."""
    filename = "requirements/requirements.txt"
    requirements = []
    if current_python_version < (3, 7):
        filename = "requirements/py36_requirements.txt"

    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
    # remove duplicates
    requirements = list(set(requirements))
    return requirements


# basic
setup(
    # 描述信息
    name="apk",
    version="0.0.4",
    description="awesome perception kit",
    author="windzu",
    author_email="windzu1@gmail.com",
    url="",
    license="MIT license",
    keywords="adas deeplearning",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    # 主要设置
    python_requires=">=3.6",
    packages=find_packages(exclude=("docs")),
    install_requires=parse_requirements(),
    entry_points={"console_scripts": ["apk=apk.main:main"]},
    # 次要设置
    include_package_data=True,
    zip_safe=False,
)
