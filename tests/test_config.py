"""Tests for configuration module"""

from pathlib import Path
import tempfile

from anomradar.core.config import Config, LoggingConfig, CacheConfig, ScannerConfig


def test_config_defaults():
    """Test default configuration values"""
    config = Config()
    
    assert config.env == "production"
    assert config.log_level == "INFO"
    assert config.timeout == 30
    assert config.max_retries == 3
    assert config.cache_ttl == 3600
    assert config.cache_enabled is True


def test_config_path_expansion():
    """Test that paths are expanded correctly"""
    config = Config(
        cache_dir="~/.anomradar/cache",
        data_dir="~/test/data"
    )
    
    # Paths should be expanded
    assert config.cache_dir.startswith(str(Path.home()))
    assert config.data_dir.startswith(str(Path.home()))


def test_config_load_with_env_file():
    """Test loading config from .env file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_file.write_text("""
ANOMRADAR_ENV=testing
ANOMRADAR_LOG_LEVEL=DEBUG
ANOMRADAR_TIMEOUT=60
ANOMRADAR_CACHE_TTL=7200
""")
        
        config = Config.load(env_file=env_file)
        
        assert config.env == "testing"
        assert config.log_level == "DEBUG"
        assert config.timeout == 60
        assert config.cache_ttl == 7200


def test_config_load_with_toml_file():
    """Test loading config from TOML file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        toml_file = Path(tmpdir) / "anomradar.toml"
        toml_file.write_text("""
[application]
name = "AnomRadar"
environment = "testing"

[logging]
level = "DEBUG"
format = "json"
output = "~/.anomradar/logs/test.log"

[cache]
enabled = true
ttl = 1800
directory = "~/.anomradar/cache"
max_size_mb = 50

[scanners]
timeout = 45
max_retries = 5
user_agent = "TestAgent/1.0"
""")
        
        config = Config.load(toml_file=toml_file)
        
        assert config.env == "testing"
        assert config.logging is not None
        assert config.logging.level == "DEBUG"
        assert config.logging.format == "json"
        assert config.cache is not None
        assert config.cache.ttl == 1800
        assert config.scanners is not None
        assert config.scanners.timeout == 45


def test_config_ensure_directories():
    """Test directory creation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use environment variables to avoid path expansion in validator
        test_cache_dir = f"{tmpdir}/cache"
        test_data_dir = f"{tmpdir}/data"
        
        config = Config(
            cache_dir=test_cache_dir,
            data_dir=test_data_dir
        )
        
        # Directories may not exist yet (depending on if path was already expanded)
        # Create directories
        config.ensure_directories()
        
        # Now they should definitely exist
        assert Path(config.cache_dir).exists()
        assert Path(config.data_dir).exists()


def test_nested_configs():
    """Test nested configuration objects"""
    logging_config = LoggingConfig(level="ERROR", format="text")
    cache_config = CacheConfig(enabled=False, ttl=600)
    scanner_config = ScannerConfig(timeout=120, max_retries=1)
    
    config = Config(
        logging=logging_config,
        cache=cache_config,
        scanners=scanner_config
    )
    
    assert config.logging.level == "ERROR"
    assert config.cache.enabled is False
    assert config.scanners.timeout == 120
