from setuptools import setup, find_packages

setup(
    name="minipdb",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click",
        "numpy",
        "pandas",
        "duckdb",
    ],
    entry_points={
        "console_scripts": [
            "minipdb = minipdb.minipdb:cli",
        ],
    },
)
