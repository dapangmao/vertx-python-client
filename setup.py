import os
from setuptools import setup, find_packages

pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'README.md')) as f:
    readme = f.read()

setup(
    name='vertx-python-client',
    py_modules=['vertx'],
    version='0.4.0',
    description='An asynchronous TCP eventbus Python client',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='dapangmao',
    author_email='hchao8@gmail.com',
    url='https://github.com/dapangmao/vertx-python-client',
    install_requires=[
    ],
    tests_require=[
        'pytest>=5.0.1',
    ],
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
    packages=find_packages(exclude=['tests', 'docs', 'script', 'build', 'dist'])
)
