from setuptools import setup, find_packages

setup(
    name="auto_white_reimu",
    version="0.1.1",
    packages=find_packages(),
    url="",
    license="GPL",
    author="Ledenel",
    author_email="ledenelintelli@gmail.com",
    description="",
    package_data={"": ["*.png", "*.html"]},
    install_requires=["numpy", "bitstruct", "requests", "jinja2", "loguru"],
    setup_requires=["pytest-runner"],
    # tests_require=test_deps,
    extras_require={"dev": ["pipenv-setup",], "test": ["pytest", "pandas", "beautifulsoup4"],},
    entry_points={
        'console_scripts': [
            'tenhou-check = mahjong.tenhou_record_check:main',
            'mahjong-win-rate = mahjong.win_rate_demo:main',
        ]
    }
)
