"""Tests for scanner modules using example.com"""

import pytest
from anomradar.core.config import Config
from anomradar.scanners.http import scan_http
from anomradar.scanners.dns import scan_dns
from anomradar.scanners.ssl import scan_ssl
from anomradar.scanners import run_scan, get_available_scanners


# Test domain - example.com is designed for testing
TEST_DOMAIN = "example.com"


@pytest.fixture
def config():
    """Create test configuration"""
    return Config(timeout=30, max_retries=1)


def test_get_available_scanners():
    """Test getting list of available scanners"""
    scanners = get_available_scanners()
    
    assert isinstance(scanners, list)
    assert "http" in scanners
    assert "dns" in scanners
    assert "ssl" in scanners


def test_http_scanner_success(config):
    """Test HTTP scanner with example.com"""
    result = scan_http(TEST_DOMAIN, config)
    
    assert isinstance(result, dict)
    assert "success" in result
    assert "message" in result
    assert "timestamp" in result
    assert "target" in result
    
    # Should succeed for example.com
    if result["success"]:
        assert "data" in result
        assert "status_code" in result["data"]
        assert result["data"]["status_code"] == 200


def test_http_scanner_with_https(config):
    """Test HTTP scanner with HTTPS URL"""
    result = scan_http(f"https://{TEST_DOMAIN}", config)
    
    assert isinstance(result, dict)
    assert "target" in result
    assert result["target"].startswith("https://")


def test_http_scanner_invalid_domain(config):
    """Test HTTP scanner with invalid domain"""
    result = scan_http("invalid-domain-that-does-not-exist.xyz", config)
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "error" in result


def test_dns_scanner_success(config):
    """Test DNS scanner with example.com"""
    result = scan_dns(TEST_DOMAIN, config)
    
    assert isinstance(result, dict)
    assert "success" in result
    assert "message" in result
    assert "timestamp" in result
    assert "target" in result
    
    # Should find at least A records for example.com
    if result["success"]:
        assert "data" in result
        # example.com should have A records
        if "A" in result["data"]:
            assert len(result["data"]["A"]) > 0


def test_dns_scanner_with_protocol(config):
    """Test DNS scanner strips protocol"""
    result = scan_dns(f"https://{TEST_DOMAIN}/path", config)
    
    assert isinstance(result, dict)
    assert result["target"] == TEST_DOMAIN


def test_dns_scanner_invalid_domain(config):
    """Test DNS scanner with invalid domain"""
    result = scan_dns("invalid-domain-xyz.invalid", config)
    
    assert isinstance(result, dict)
    # May fail with nxdomain or no records


def test_ssl_scanner_success(config):
    """Test SSL scanner with example.com"""
    result = scan_ssl(TEST_DOMAIN, config)
    
    assert isinstance(result, dict)
    assert "success" in result
    assert "message" in result
    assert "timestamp" in result
    assert "target" in result
    
    # Should succeed for example.com
    if result["success"]:
        assert "data" in result
        # Check for SSL/TLS info
        assert "version" in result["data"]
        assert "cipher" in result["data"]


def test_ssl_scanner_strips_protocol(config):
    """Test SSL scanner strips protocol"""
    result = scan_ssl(f"https://{TEST_DOMAIN}/path", config)
    
    assert isinstance(result, dict)
    assert result["target"] == TEST_DOMAIN


def test_ssl_scanner_invalid_domain(config):
    """Test SSL scanner with invalid domain"""
    result = scan_ssl("invalid-domain-that-does-not-exist.xyz", config)
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "error" in result


def test_run_scan_all_scanners(config):
    """Test running all scanners together"""
    results = run_scan(TEST_DOMAIN, config=config, use_cache=False)
    
    assert isinstance(results, dict)
    assert "http" in results
    assert "dns" in results
    assert "ssl" in results
    
    # Each scanner should return a result dict
    for scanner_name, result in results.items():
        assert isinstance(result, dict)
        assert "success" in result
        assert "message" in result


def test_run_scan_specific_scanner(config):
    """Test running specific scanner"""
    results = run_scan(TEST_DOMAIN, scanner_names=["http"], config=config, use_cache=False)
    
    assert isinstance(results, dict)
    assert "http" in results
    assert "dns" not in results
    assert "ssl" not in results


def test_run_scan_multiple_scanners(config):
    """Test running multiple specific scanners"""
    results = run_scan(
        TEST_DOMAIN, 
        scanner_names=["http", "dns"], 
        config=config, 
        use_cache=False
    )
    
    assert isinstance(results, dict)
    assert "http" in results
    assert "dns" in results
    assert "ssl" not in results


def test_run_scan_with_cache(config):
    """Test scan with caching enabled"""
    # First run (no cache)
    results1 = run_scan(TEST_DOMAIN, config=config, use_cache=True)
    
    # Second run (should use cache if first succeeded)
    results2 = run_scan(TEST_DOMAIN, config=config, use_cache=True)
    
    assert isinstance(results1, dict)
    assert isinstance(results2, dict)
    
    # Results should be consistent
    assert set(results1.keys()) == set(results2.keys())


def test_scanner_error_handling():
    """Test scanner handles missing config gracefully"""
    # Create minimal config
    config = Config()
    
    # Should not crash even with default config
    result = scan_http(TEST_DOMAIN, config)
    assert isinstance(result, dict)
