from setuptools import setup, find_packages
test_deps = [
    "pytest",
    "pandas"
]
extras = {
    'test': test_deps,
}
setup(
    name='auto_white_reimu',
    version='0.1',
    packages=find_packages(),
    url='',
    license='GPL',
    author='Ledenel',
    author_email='ledenelintelli@gmail.com',
    description='',
    install_requires=[
        'numpy',
        'bitstruct',
        'requests',
        'Jinja2'
    ],
    setup_requires=[
        "pytest-runner"
    ],
    tests_require=test_deps,
    extras_require=extras,
)
