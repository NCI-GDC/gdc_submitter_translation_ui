'''setup'''

from setuptools import setup, find_packages

setup(
    name="GDC_submitter_UI",
    version="1.0",
    install_requires=[
        "Flask==1.0.2",
        "PyYAML==3.12",
        "requests==2.18.4"
    ],
    packages=find_packages(),
)
