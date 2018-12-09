from setuptools import setup, find_packages

setup(
    name='majlib',
    version='0.1',
    packages=find_packages(),
    url='',
    license='GPL',
    author='Ledenel',
    author_email='ledenelintelli@gmail.com',
    description='',
    setup_requires=[
        "pytest-runner"
    ],
    tests_require=[
        "pytest"
    ],
)
