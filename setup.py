from setuptools import setup

version = '0.2.1beta'

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
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=['boilerpipy'],
    scripts=['bin/readability', 'bin/query'],
    install_requires=['lxml', 'beautifulsoup4', 'urlparse2'],
)
