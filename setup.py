from distutils.core import setup

version = '0.1'

setup(
    name='extractor',
    version=version,
    description=('Readability extractor in Python'),
    author='Harshavardhana',
    author_email='harsha@harshavardhana.net',
    url='https://github.com/harshavardhana/extractor.git',
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
    scripts=['bin/relevance_extractor'],
    requires=['lxml', 'beautifulsoup4', 'urlparse2'],
)
