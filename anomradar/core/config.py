"""
Configuration management for AnomRadar v2.

Implements layered configuration using:
1. Environment variables (.env file)
2. TOML configuration file (anomradar.toml)
3. Sensible defaults

Uses pydantic for validation and BaseSettings for env integration.
"""

from pathlib import Path
from typing import List, Optional

import toml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application-level configuration."""
    
    name: str = Field(default="AnomRadar", alias="APP_NAME")
    version: str = Field(default="2.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class CacheConfig(BaseSettings):
    """Cache configuration."""
    
    enabled: bool = Field(default=True, alias="CACHE_ENABLED")
    ttl: int = Field(default=3600, alias="CACHE_TTL")
    directory: str = Field(default="~/.anomradar/cache", alias="CACHE_DIR")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class ScannerConfig(BaseSettings):
    """Scanner configuration."""
    
    timeout: int = Field(default=30, alias="SCANNER_TIMEOUT")
    max_retries: int = Field(default=2, alias="SCANNER_MAX_RETRIES")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class HttpScannerConfig(BaseSettings):
    """HTTP scanner specific configuration."""
    
    user_agent: str = Field(
        default="AnomRadar/2.0 (Security Scanner)",
        alias="HTTP_USER_AGENT"
    )
    follow_redirects: bool = Field(default=True, alias="HTTP_FOLLOW_REDIRECTS")
    timeout: int = Field(default=15, alias="HTTP_TIMEOUT")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class DnsScannerConfig(BaseSettings):
    """DNS scanner specific configuration."""
    
    nameservers: str = Field(default="8.8.8.8,1.1.1.1", alias="DNS_NAMESERVERS")
    timeout: int = Field(default=10, alias="DNS_TIMEOUT")
    
    @property
    def nameservers_list(self) -> List[str]:
        """Parse nameservers string into list."""
        return [ns.strip() for ns in self.nameservers.split(",")]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class SslScannerConfig(BaseSettings):
    """SSL scanner specific configuration."""
    
    verify_expiration: bool = Field(default=True, alias="SSL_VERIFY_EXPIRATION")
    check_weak_ciphers: bool = Field(default=True, alias="SSL_CHECK_WEAK_CIPHERS")
    timeout: int = Field(default=20, alias="SSL_TIMEOUT")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class ReportConfig(BaseSettings):
    """Report generation configuration."""
    
    output_directory: str = Field(
        default="~/.anomradar/reports",
        alias="REPORT_OUTPUT_DIR"
    )
    template: str = Field(default="default", alias="REPORT_TEMPLATE")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    
    level: str = Field(default="INFO", alias="LOG_LEVEL")
    file: str = Field(default="~/.anomradar/logs/anomradar.log", alias="LOG_FILE")
    console: bool = Field(default=True, alias="LOG_CONSOLE")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class Config:
    """
    Main configuration class with layered settings support.
    
    Configuration priority (highest to lowest):
    1. TOML file (anomradar.toml)
    2. Environment variables (.env)
    3. Defaults
    """
    
    def __init__(self, toml_path: Optional[str] = None):
        """
        Initialize configuration with optional TOML overlay.
        
        Args:
            toml_path: Path to TOML configuration file
        """
        # Load base settings from environment
        self.app = AppConfig()
        self.cache = CacheConfig()
        self.scanners = ScannerConfig()
        self.http_scanner = HttpScannerConfig()
        self.dns_scanner = DnsScannerConfig()
        self.ssl_scanner = SslScannerConfig()
        self.reports = ReportConfig()
        self.logging = LoggingConfig()
        
        # Apply TOML overrides if provided
        if toml_path:
            self._load_toml_overrides(toml_path)
    
    def _load_toml_overrides(self, toml_path: str) -> None:
        """
        Load and apply TOML configuration overrides.
        
        Args:
            toml_path: Path to TOML configuration file
        """
        path = Path(toml_path).expanduser()
        if not path.exists():
            return
        
        try:
            data = toml.load(path)
            
            # Apply app settings
            if "app" in data:
                for key, value in data["app"].items():
                    if hasattr(self.app, key):
                        setattr(self.app, key, value)
            
            # Apply cache settings
            if "cache" in data:
                for key, value in data["cache"].items():
                    if hasattr(self.cache, key):
                        setattr(self.cache, key, value)
            
            # Apply scanner settings
            if "scanners" in data:
                for key, value in data["scanners"].items():
                    if key == "http" and isinstance(value, dict):
                        for k, v in value.items():
                            if hasattr(self.http_scanner, k):
                                setattr(self.http_scanner, k, v)
                    elif key == "dns" and isinstance(value, dict):
                        for k, v in value.items():
                            if hasattr(self.dns_scanner, k):
                                if k == "nameservers":
                                    setattr(self.dns_scanner, k, ",".join(v))
                                else:
                                    setattr(self.dns_scanner, k, v)
                    elif key == "ssl" and isinstance(value, dict):
                        for k, v in value.items():
                            if hasattr(self.ssl_scanner, k):
                                setattr(self.ssl_scanner, k, v)
                    elif hasattr(self.scanners, key):
                        setattr(self.scanners, key, value)
            
            # Apply report settings
            if "reports" in data:
                for key, value in data["reports"].items():
                    if hasattr(self.reports, key):
                        setattr(self.reports, key, value)
            
            # Apply logging settings
            if "logging" in data:
                for key, value in data["logging"].items():
                    if hasattr(self.logging, key):
                        setattr(self.logging, key, value)
        
        except Exception as e:
            # Don't crash on config errors - use defaults
            import warnings
            warnings.warn(f"Failed to load TOML config from {toml_path}: {e}")
    
    def get_cache_dir(self) -> Path:
        """Get expanded cache directory path."""
        return Path(self.cache.directory).expanduser()
    
    def get_report_dir(self) -> Path:
        """Get expanded report directory path."""
        return Path(self.reports.output_directory).expanduser()
    
    def get_log_file(self) -> Path:
        """Get expanded log file path."""
        return Path(self.logging.file).expanduser()
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        dirs = [
            self.get_cache_dir(),
            self.get_report_dir(),
            self.get_log_file().parent,
            Path("~/.anomradar").expanduser()
        ]
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)


# Global config instance
_config: Optional[Config] = None


def get_config(toml_path: Optional[str] = None, force_reload: bool = False) -> Config:
    """
    Get or create the global configuration instance.
    
    Args:
        toml_path: Optional path to TOML configuration file
        force_reload: Force reload configuration
    
    Returns:
        Global Config instance
    """
    global _config
    
    if _config is None or force_reload:
        # Look for anomradar.toml in current directory or home
        if toml_path is None:
            candidates = [
                Path("anomradar.toml"),
                Path("~/.anomradar/anomradar.toml").expanduser(),
            ]
            for candidate in candidates:
                if candidate.exists():
                    toml_path = str(candidate)
                    break
        
        _config = Config(toml_path=toml_path)
        _config.ensure_directories()
    
    return _config
