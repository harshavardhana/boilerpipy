from setuptools import setup, find_packages

with open('README.md') as file:
    long_description = file.read()

version = '0.2.3'

setup(
    name='boilerpipy',
    version=version,
    description='Readability/Boilerpipe extractor in Python',
    author='Harshavardhana',
    author_email='harsha@harshavardhana.net',
    url='https://github.com/harshavardhana/boilerpipy.git',
    license='Apache',
    platforms=['any'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    scripts=['bin/readability', 'bin/query'],
    install_requires=['lxml', 'beautifulsoup4', 'urlparse2'],
    long_description=long_description,
)
