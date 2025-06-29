from setuptools import setup, find_packages


def long_description():
    with open("README.md") as readme:
        return readme.read()


setup(
    name="chatwoot-gemini-bot",
    version="1.0.0",
    author="Jordan Price",
    author_email="jordan@dragonbyte.solutions",
    description="Chatwoot agent bot powered by Google Gemini AI",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    packages=["woothook"],
    license="MIT",
    project_urls={
        "Bug Tracker": "https://github.com/xrhythmic/chatwoot-gemini-bot/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.27.1",
        "woot @ git+https://github.com/dearkafka/woot#egg=woot",
        "typer",
        "fastapi",
        "uvicorn",
        "google-generativeai>=0.8.0",
        "python-dotenv",
    ],
    entry_points={  # Optional
        "console_scripts": [
            "woothook=woothook.service:app",
        ],
    },
)
