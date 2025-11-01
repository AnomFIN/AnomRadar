"""
Tests for configuration system.

Tests layered configuration loading and validation.
"""

import os
import tempfile
from pathlib import Path

import toml

from anomradar.core.config import (
    Config,
    AppConfig,
    CacheConfig,
    ScannerConfig,
    get_config
)


def test_app_config_defaults():
    """Test AppConfig with default values."""
    config = AppConfig()
    
    assert config.name == "AnomRadar"
    assert config.version == "2.0.0"
    assert config.debug is False


def test_cache_config_defaults():
    """Test CacheConfig with default values."""
    config = CacheConfig()
    
    assert config.enabled is True
    assert config.ttl == 3600
    assert config.directory == "~/.anomradar/cache"


def test_scanner_config_defaults():
    """Test ScannerConfig with default values."""
    config = ScannerConfig()
    
    assert config.timeout == 30
    assert config.max_retries == 2


def test_config_initialization():
    """Test Config initialization without TOML."""
    config = Config()
    
    assert config.app is not None
    assert config.cache is not None
    assert config.scanners is not None
    assert config.http_scanner is not None
    assert config.dns_scanner is not None
    assert config.ssl_scanner is not None
    assert config.reports is not None
    assert config.logging is not None


def test_config_toml_override():
    """Test Config with TOML overrides."""
    # Create temporary TOML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        toml_data = {
            "app": {
                "name": "TestRadar",
                "debug": True
            },
            "cache": {
                "enabled": False,
                "ttl": 7200
            },
            "scanners": {
                "timeout": 60,
                "http": {
                    "timeout": 30
                }
            }
        }
        toml.dump(toml_data, f)
        toml_path = f.name
    
    try:
        # Load config with TOML
        config = Config(toml_path=toml_path)
        
        # Check overrides
        assert config.app.name == "TestRadar"
        assert config.app.debug is True
        assert config.cache.enabled is False
        assert config.cache.ttl == 7200
        assert config.scanners.timeout == 60
        assert config.http_scanner.timeout == 30
    
    finally:
        # Clean up
        os.unlink(toml_path)


def test_config_get_cache_dir():
    """Test cache directory path expansion."""
    config = Config()
    cache_dir = config.get_cache_dir()
    
    assert isinstance(cache_dir, Path)
    assert "~" not in str(cache_dir)  # Should be expanded


def test_config_get_report_dir():
    """Test report directory path expansion."""
    config = Config()
    report_dir = config.get_report_dir()
    
    assert isinstance(report_dir, Path)
    assert "~" not in str(report_dir)  # Should be expanded


def test_config_get_log_file():
    """Test log file path expansion."""
    config = Config()
    log_file = config.get_log_file()
    
    assert isinstance(log_file, Path)
    assert "~" not in str(log_file)  # Should be expanded


def test_config_ensure_directories():
    """Test directory creation."""
    config = Config()
    
    # This should not raise an exception
    config.ensure_directories()
    
    # Verify directories exist
    assert config.get_cache_dir().exists()
    assert config.get_report_dir().exists()
    assert config.get_log_file().parent.exists()


def test_dns_scanner_config_nameservers_list():
    """Test DNS scanner nameservers list parsing."""
    from anomradar.core.config import DnsScannerConfig
    
    config = DnsScannerConfig()
    nameservers = config.nameservers_list
    
    assert isinstance(nameservers, list)
    assert len(nameservers) >= 1
    assert all(isinstance(ns, str) for ns in nameservers)


def test_config_invalid_toml():
    """Test Config with invalid TOML file."""
    # Non-existent file should not crash
    config = Config(toml_path="/nonexistent/path/to/config.toml")
    
    # Should still have default values
    assert config.app.name == "AnomRadar"
    assert config.cache.enabled is True


def test_get_config_singleton():
    """Test get_config returns singleton instance."""
    config1 = get_config()
    config2 = get_config()
    
    # Should be the same instance
    assert config1 is config2


def test_get_config_force_reload():
    """Test get_config with force reload."""
    config1 = get_config()
    config2 = get_config(force_reload=True)
    
    # Should be different instances
    assert config1 is not config2
