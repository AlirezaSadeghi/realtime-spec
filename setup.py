#!/usr/bin/env python

from pathlib import Path
from setuptools import find_packages, setup

project_name = 'realtime'
readme = Path('README.rst')

classes = """
    Development Status :: 1 - Beta
    Intended Audience :: Guys @ Tapad
    
    Programming Language :: Python :: 3.6 :: Only
    
    Operating System :: POSIX :: Linux
    Operating System :: MacOS :: MacOS X
    
    Topic :: Framework :: Django
    Topic :: Software Development :: Offline Test
"""
classifiers = [s.strip() for s in classes.split('\n') if s]

base_dir = Path(__file__).parent.absolute()


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def _pip_requirement(req):
    if req.startswith('-r '):
        _, path = req.split()
        return requirements(*path.split('/'))
    return [req]


def requirements(*f):
    path = (Path.cwd() / 'requirements').joinpath(*f)
    with path.open() as fh:
        _requirements = [strip_comments(l) for l in fh.readlines()]
        return [
            req for sub_requirements in [
                _pip_requirement(r) for r in _requirements if r
            ] for req in sub_requirements
        ]


setup(
    name=project_name,
    version='1.0.0',
    description='TapAd offline test',
    author='Alireza Sadeghi',
    author_email='alireza@pushe.co',
    url='http://alirezasadeghi.com',
    platforms=['any'],
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    include_package_data=True,
    python_requires='>=3.6.0',
    keywords=[],
    zip_safe=False,
    install_requires=requirements('base.txt'),
    tests_require=requirements('test.txt'),
    classifiers=classifiers,
    long_description=readme.read_text(encoding='utf-8'),
    entry_points={
        'console_scripts': [
            'tapad = realtime.__main__:main',
            'consumer = realtime.consumer.app:main',
        ],
    },
)
