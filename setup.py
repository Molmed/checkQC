from setuptools import setup, find_packages
from checkQC import __version__

setup(
    name='checkQC',
    version=__version__,
    description="A simple program to parse Illumina NGS data and check it for quality criteria.",
    long_description="A simple program to parse Illumina NGS data and check it for quality criteria.",
    keywords=['bioinformatics', 'ngs', 'quality control'],
    author='Johan Dahlberg, SNP&SEQ Technology Platform, Uppsala University',
    author_email='johan.dahlberg@medsci.uu.se',
    url="https://www.github.com/Molmed/checkQC",
    download_url='https://github.com/Molmed/checkQC/archive/{}.tar.gz'.format(__version__),
    python_requires='>3.10, <3.11',
    install_requires=[
        "click",
        "PyYAML>=6.0",
        "interop>=1.2.4",
        "xmltodict",
        "tornado",
        "sample_sheet"],
    packages=find_packages(exclude=["tests*"]),
    test_suite="tests",
    package_data={'checkQC': ['default_config/config.yaml', 'default_config/logger.yaml']},
    include_package_data=True,
    license='GPLv3',
    entry_points={
        'console_scripts': ['checkqc = checkQC.app:start',
                            'checkqc-ws = checkQC.web_app:start']
    },
)
