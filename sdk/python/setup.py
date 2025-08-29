"""Setup configuration for Chatter Python SDK."""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chatter-sdk",
    version="0.1.0",
    author="Chatter Team",
    author_email="support@chatter.ai",
    description="Python SDK for Chatter AI Chatbot API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lllucius/chatter",
    project_urls={
        "Bug Tracker": "https://github.com/lllucius/chatter/issues",
        "Documentation": "https://github.com/lllucius/chatter#readme",
        "Source Code": "https://github.com/lllucius/chatter",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="api, sdk, chatbot, ai, langchain, openai, anthropic",
    include_package_data=True,
    zip_safe=False,
)
