from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mcp-universal-framework",
    version="1.0.0",
    author="MCP Framework Team", 
    author_email="team@mcp-framework.org",
    description="A comprehensive framework for accelerating MCP server development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/mcp-universal-framework",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0", 
            "black>=23.0.0",
            "mypy>=1.5.0",
        ],
        "cli": [
            "click>=8.0.0",
            "jinja2>=3.1.0",
            "rich>=13.0.0",
        ],
        "all": [
            "mcp>=0.1.0",
            "fastmcp>=0.1.0",
            "httpx>=0.25.0",
            "requests>=2.31.0",
            "pydantic>=2.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "mcp-framework=mcp_framework.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mcp_framework": [
            "templates/**/*",
            "examples/**/*",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-org/mcp-universal-framework/issues",
        "Source": "https://github.com/your-org/mcp-universal-framework",
        "Documentation": "https://mcp-framework.readthedocs.io/",
    },
)
