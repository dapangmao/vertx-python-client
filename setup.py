import os
from setuptools import setup, find_packages

pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'README.md')) as f:
    readme = f.read()

with open(os.path.join(pwd, 'LICENSE')) as f:
    license = f.read()

setup(
    name='vertx-python-client',
    py_modules=['vertx'],
    version='0.3.1',
    description='An asynchronous TCP eventbus Python client',
    long_description=readme,
    author='dapangmao',
    author_email='hchao8@gmail.com',
    url='https://github.com/dapangmao/vertx-python-client',
    install_requires=[
    ],
    tests_require=[
        'pytest>=5.0.1',
    ],
    license=license,
    zip_safe=False,
    packages=find_packages(exclude=['tests', 'docs', 'script', 'build', 'dist'])
)
