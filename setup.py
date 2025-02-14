from setuptools import setup, find_packages

setup(
    name="InputParameterMiner",
    version="1.0",
    description="A tool to analyze websites for input fields, network requests, hidden parameters, and reflected values.",
    author="MrColonel",
    author_email="mrcolonelhunter@gmail.com",
    url="https://github.com/hrgeek/InputParameterMiner.git",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "selenium",
        "selenium-wire",
        "beautifulsoup4",
        "aiohttp",
        "requests",
        "argparse"
    ],
    entry_points={
        "console_scripts": [
            "parameterminer=InputParameterMiner.main:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Testing"
    ],
    python_requires=">=3.7",
)
