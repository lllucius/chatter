"""Centralized configuration for SDK generation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class SDKConfig:
    """Base configuration for SDK generation."""
    project_root: Path
    output_dir: Path
    package_name: str
    package_version: str
    package_description: str
    package_url: str
    package_author: str
    author_email: str


@dataclass
class PythonSDKConfig(SDKConfig):
    """Configuration for Python SDK generation."""
    project_name: str = ""
    package_company: str = ""
    use_asyncio: bool = True
    
    def __post_init__(self):
        if not self.project_name:
            self.project_name = self.package_name.replace("_", "-")


@dataclass
class TypeScriptSDKConfig(SDKConfig):
    """Configuration for TypeScript SDK generation."""
    npm_name: str = ""
    npm_repository: str = ""
    base_path: str = "http://localhost:8000"
    api_package: str = "api"
    with_interfaces: bool = True
    use_single_request_parameter: bool = True
    supports_es6: bool = True
    with_separate_models_and_api: bool = False
    
    def __post_init__(self):
        if not self.npm_name:
            self.npm_name = self.package_name.replace("_", "-")
        if not self.npm_repository:
            self.npm_repository = self.package_url


def get_default_python_config(project_root: Path) -> PythonSDKConfig:
    """Get default configuration for Python SDK generation."""
    return PythonSDKConfig(
        project_root=project_root,
        output_dir=project_root / "sdk" / "python",
        package_name="chatter_sdk",
        project_name="chatter-sdk",
        package_version="0.1.0",
        package_description="Python SDK for Chatter AI Chatbot API",
        package_url="https://github.com/lllucius/chatter",
        package_author="Chatter Team",
        author_email="support@chatter.ai",
        package_company="Chatter Team",
        use_asyncio=True,
    )


def get_default_typescript_config(project_root: Path) -> TypeScriptSDKConfig:
    """Get default configuration for TypeScript SDK generation."""
    return TypeScriptSDKConfig(
        project_root=project_root,
        output_dir=project_root / "frontend" / "src" / "sdk",
        package_name="chatter_sdk",
        npm_name="chatter-sdk",
        package_version="0.1.0",
        package_description="TypeScript SDK for Chatter AI Chatbot API",
        package_url="https://github.com/lllucius/chatter",
        npm_repository="https://github.com/lllucius/chatter",
        package_author="Chatter Team",
        author_email="support@chatter.ai",
        base_path="http://localhost:8000",
    )


def get_openapi_generator_config(config: Any) -> Dict[str, Any]:
    """Convert SDK config to OpenAPI Generator configuration format."""
    if isinstance(config, PythonSDKConfig):
        return {
            "packageName": config.package_name,
            "projectName": config.project_name,
            "packageVersion": config.package_version,
            "packageUrl": config.package_url,
            "packageCompany": config.package_company,
            "packageAuthor": config.package_author,
            "packageDescription": config.package_description,
            "infoEmail": config.author_email,
            "library": "asyncio" if config.use_asyncio else "urllib3",
            "useAsyncio": config.use_asyncio,
        }
    
    elif isinstance(config, TypeScriptSDKConfig):
        return {
            "basePath": config.base_path,
            "npmName": config.npm_name,
            "npmVersion": config.package_version,
            "npmRepository": config.npm_repository,
            "npmDescription": config.package_description,
            "apiPackage": config.api_package,
            "withInterfaces": config.with_interfaces,
            "useSingleRequestParameter": config.use_single_request_parameter,
            "supportsES6": config.supports_es6,
            "withSeparateModelsAndApi": config.with_separate_models_and_api,
            "enumNameSuffix": "",
            "enumPropertyNaming": "original",
        }
    
    else:
        raise ValueError(f"Unsupported config type: {type(config)}")