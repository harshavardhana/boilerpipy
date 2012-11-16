from distutils.core import setup

version = '0.2beta'

setup(
    name='extractor',
    version=version,
    description=('Readability extractor in Python'),
    author='Harshavardhana',
    author_email='harsha@harshavardhana.net',
    url='https://github.com/harshavardhana/boilerpipy.git',
    license='Apache',
    platforms=['any'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=['extractor'],
    scripts=['bin/readability'],
    requires=['lxml', 'beautifulsoup4', 'urlparse2'],
)
