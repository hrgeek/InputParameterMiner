from setuptools import setup, find_packages

setup(
    name="input-parameter-miner",
    version="1.0.0",
    description="A tool to analyze websites for input fields, network requests, hidden parameters, and reflected values.",
    author="MrColonel",
    author_email="mrcolonelhunter@gmail.com",
    packages=find_packages(),  # Automatically find all packages
    install_requires=[
        "selenium>=4.0.0",
        "selenium-wire>=5.1.0",
        "beautifulsoup4>=4.10.0",
        "requests>=2.26.0",
        "aiohttp>=3.8.1",
        "lxml>=4.6.3",
    ],
    entry_points={
        "console_scripts": [
            "InputParameterMiner=InputParameterMiner.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
