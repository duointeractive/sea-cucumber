from setuptools import setup

DESCRIPTION = "A Django email backend for Amazon Simple Email Service, backed by celery."

LONG_DESCRIPTION = open('README.rst').read()

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Framework :: Django',
]

setup(
    name='seacucumber',
    version='1.5.1',
    packages=[
        'seacucumber',
        'seacucumber.management',
        'seacucumber.management.commands',
    ],
    author='Gregory Taylor',
    author_email='gtaylor@duointeractive.com',
    url='https://github.com/duointeractive/sea-cucumber/',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=CLASSIFIERS,
    install_requires=['boto>=2.8.0', 'celery'],
)
