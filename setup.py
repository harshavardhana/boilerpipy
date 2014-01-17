from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

version = '0.2.1'

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
        "Development Status :: 5 - Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=['boilerpipy'],
    scripts=['bin/readability', 'bin/query'],
    install_requires=['lxml', 'beautifulsoup4', 'urlparse2'],
    long_description=long_description,
)
