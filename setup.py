from setuptools import setup, find_packages

setup(
    name="auto_white_reimu",
    version="0.1.3",
    packages=find_packages(),
    url="",
    license="GPL",
    author="Ledenel",
    author_email="ledenelintelli@gmail.com",
    description="",
    package_data={"": ["*.png", "*.html"]},
    install_requires=[
        "bitstruct==8.9.0",
        "certifi==2019.11.28",
        "chardet==3.0.4",
        "colorama==0.4.3; sys_platform == 'win32'",
        "idna==2.8",
        "jinja2==2.11.0",
        "loguru==0.4.1",
        "markupsafe==1.1.1",
        "numpy==1.18.1",
        "pandas==0.25.3",
        "python-dateutil==2.8.1",
        "pytz==2019.3",
        "requests==2.22.0",
        "six==1.14.0",
        "urllib3==1.25.8",
        "win32-setctime==1.0.1; sys_platform == 'win32'",
    ],
    setup_requires=["pytest-runner"],
    # tests_require=test_deps,
    extras_require={
        "dev": ["pipenv-setup",],
        "test": ["pytest", "pandas", "beautifulsoup4"],
    },
    entry_points={
        "console_scripts": [
            "tenhou-check = mahjong.tenhou_record_check:main",
            "mahjong-win-rate = mahjong.win_rate_demo:main",
        ]
    },
)
