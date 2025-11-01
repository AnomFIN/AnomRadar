"""Configuration management for AnomRadar v2

Merges settings from .env files and anomradar.toml configuration files
using Pydantic for validation and type safety.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
try:
    import tomllib
except ImportError:
    import tomli as tomllib

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "json"
    output: str = "~/.anomradar/logs/anomradar.log"


class CacheConfig(BaseModel):
    """Cache configuration"""
    enabled: bool = True
    ttl: int = 3600
    directory: str = "~/.anomradar/cache"
    max_size_mb: int = 100


class ScannerConfig(BaseModel):
    """Scanner configuration"""
    timeout: int = 30
    max_retries: int = 3
    user_agent: str = "AnomRadar/2.0 Security Scanner"


class Config(BaseSettings):
    """Main configuration class with .env and TOML merging"""
    
    model_config = SettingsConfigDict(
        env_prefix='ANOMRADAR_',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    # Application settings
    env: str = Field(default="production", alias="ANOMRADAR_ENV")
    log_level: str = Field(default="INFO", alias="ANOMRADAR_LOG_LEVEL")
    cache_dir: str = Field(default="~/.anomradar/cache", alias="ANOMRADAR_CACHE_DIR")
    data_dir: str = Field(default="~/.anomradar/data", alias="ANOMRADAR_DATA_DIR")
    
    # Scanner settings
    timeout: int = Field(default=30, alias="ANOMRADAR_TIMEOUT")
    max_retries: int = Field(default=3, alias="ANOMRADAR_MAX_RETRIES")
    user_agent: str = Field(default="AnomRadar/2.0 Security Scanner", alias="ANOMRADAR_USER_AGENT")
    
    # Cache settings
    cache_ttl: int = Field(default=3600, alias="ANOMRADAR_CACHE_TTL")
    cache_enabled: bool = Field(default=True, alias="ANOMRADAR_CACHE_ENABLED")
    
    # Additional nested configs (loaded from TOML if available)
    logging: Optional[LoggingConfig] = None
    cache: Optional[CacheConfig] = None
    scanners: Optional[ScannerConfig] = None
    
    @field_validator('cache_dir', 'data_dir')
    @classmethod
    def expand_path(cls, v: str) -> str:
        """Expand ~ and environment variables in paths"""
        return os.path.expanduser(os.path.expandvars(v))
    
    @classmethod
    def load(cls, 
             env_file: Optional[Path] = None, 
             toml_file: Optional[Path] = None) -> "Config":
        """Load configuration from .env and anomradar.toml files
        
        Priority (highest to lowest):
        1. Environment variables
        2. TOML file settings
        3. .env file settings
        4. Default values
        
        Args:
            env_file: Path to .env file (default: .env in current dir)
            toml_file: Path to anomradar.toml file (default: anomradar.toml in current dir)
            
        Returns:
            Configured Config instance
        """
        # Load .env file
        if env_file is None:
            env_file = Path.cwd() / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        # Start with base config from environment/defaults
        config_dict: Dict[str, Any] = {}
        
        # Load TOML configuration if available
        if toml_file is None:
            toml_file = Path.cwd() / "anomradar.toml"
        
        if toml_file.exists():
            with open(toml_file, "rb") as f:
                toml_data = tomllib.load(f)
                
                # Merge application settings
                if "application" in toml_data:
                    app = toml_data["application"]
                    if "environment" in app:
                        config_dict["env"] = app["environment"]
                
                # Store nested configs
                if "logging" in toml_data:
                    config_dict["logging"] = LoggingConfig(**toml_data["logging"])
                if "cache" in toml_data:
                    config_dict["cache"] = CacheConfig(**toml_data["cache"])
                if "scanners" in toml_data:
                    config_dict["scanners"] = ScannerConfig(**toml_data["scanners"])
        
        # Create config instance (environment variables take precedence)
        return cls(**config_dict)
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # Create log directory if logging config exists
        if self.logging:
            log_path = Path(self.logging.output).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)
