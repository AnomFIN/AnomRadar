"""
Tests for scanner modules.

Tests HTTP, DNS, and SSL scanners with example.com as target.
"""

import pytest

from anomradar.core.config import Config
from anomradar.core.cache import Cache
from anomradar.scanners.http import HttpScanner
from anomradar.scanners.dns import DnsScanner
from anomradar.scanners.ssl import SslScanner
from anomradar.scanners import ScanStatus


@pytest.fixture
def config():
    """Provide test configuration."""
    return Config()


@pytest.fixture
def cache():
    """Provide test cache (disabled for tests)."""
    return Cache(enabled=False)


@pytest.mark.asyncio
async def test_http_scanner_success(config, cache):
    """Test HTTP scanner with example.com."""
    scanner = HttpScanner(config=config, cache=cache)
    result = await scanner.scan("example.com")
    
    # Check result structure
    assert "status" in result
    assert "signals" in result
    assert "summary" in result
    assert "details" in result
    
    # Status should be success or partial (network issues)
    assert result["status"] in ["success", "partial", "failed"]
    
    # If successful, check details
    if result["status"] == "success":
        assert "status_code" in result["details"]
        assert "headers" in result["details"]
        assert isinstance(result["signals"], list)


@pytest.mark.asyncio
async def test_http_scanner_https(config, cache):
    """Test HTTP scanner with HTTPS URL."""
    scanner = HttpScanner(config=config, cache=cache)
    result = await scanner.scan("https://example.com")
    
    assert "status" in result
    
    if result["status"] == "success":
        assert result["details"]["url"].startswith("https://")


@pytest.mark.asyncio
async def test_http_scanner_invalid_domain(config, cache):
    """Test HTTP scanner with invalid domain."""
    scanner = HttpScanner(config=config, cache=cache)
    result = await scanner.scan("invalid-domain-that-does-not-exist-12345.com")
    
    # Should gracefully degrade
    assert result["status"] in ["partial", "failed"]
    assert "error" in result or result["status"] == "partial"


@pytest.mark.asyncio
async def test_dns_scanner_success(config, cache):
    """Test DNS scanner with example.com."""
    scanner = DnsScanner(config=config, cache=cache)
    result = await scanner.scan("example.com")
    
    # Check result structure
    assert "status" in result
    assert "signals" in result
    assert "summary" in result
    assert "details" in result
    
    # Status should be success or partial
    assert result["status"] in ["success", "partial", "failed"]
    
    # If successful, check for DNS records
    if result["status"] == "success":
        details = result["details"]
        # example.com should have at least A records
        assert "a" in details
        if details.get("a"):
            assert isinstance(details["a"], list)


@pytest.mark.asyncio
async def test_dns_scanner_with_url(config, cache):
    """Test DNS scanner with URL (should extract domain)."""
    scanner = DnsScanner(config=config, cache=cache)
    result = await scanner.scan("https://example.com/path")
    
    assert "status" in result
    # Should extract domain and scan successfully
    if result["status"] == "success":
        assert "a" in result["details"]


@pytest.mark.asyncio
async def test_dns_scanner_invalid_domain(config, cache):
    """Test DNS scanner with invalid domain."""
    scanner = DnsScanner(config=config, cache=cache)
    result = await scanner.scan("invalid-domain-that-does-not-exist-12345.com")
    
    # Should return failed status
    assert result["status"] == "failed"
    assert "error" in result


@pytest.mark.asyncio
async def test_ssl_scanner_success(config, cache):
    """Test SSL scanner with example.com."""
    scanner = SslScanner(config=config, cache=cache)
    result = await scanner.scan("example.com")
    
    # Check result structure
    assert "status" in result
    assert "signals" in result
    assert "summary" in result
    assert "details" in result
    
    # Status should be success or partial
    assert result["status"] in ["success", "partial", "failed"]
    
    # If successful, check certificate details
    if result["status"] == "success":
        details = result["details"]
        assert "hostname" in details
        assert "subject" in details or "issuer" in details


@pytest.mark.asyncio
async def test_ssl_scanner_with_url(config, cache):
    """Test SSL scanner with full URL."""
    scanner = SslScanner(config=config, cache=cache)
    result = await scanner.scan("https://example.com")
    
    assert "status" in result
    # Should extract hostname and scan


@pytest.mark.asyncio
async def test_ssl_scanner_invalid_domain(config, cache):
    """Test SSL scanner with invalid domain."""
    scanner = SslScanner(config=config, cache=cache)
    result = await scanner.scan("invalid-domain-that-does-not-exist-12345.com")
    
    # Should gracefully degrade
    assert result["status"] in ["partial", "failed"]
    assert "error" in result or result["status"] == "partial"


@pytest.mark.asyncio
async def test_scanner_signal_structure(config, cache):
    """Test that scanner signals have correct structure."""
    scanner = HttpScanner(config=config, cache=cache)
    result = await scanner.scan("example.com")
    
    if result["signals"]:
        for signal in result["signals"]:
            assert "severity" in signal
            assert "message" in signal
            assert "details" in signal
            assert signal["severity"] in ["critical", "high", "medium", "low", "info"]


def test_scanner_base_class():
    """Test BaseScanner methods."""
    from anomradar.scanners import BaseScanner, Signal, ScanStatus
    
    # Create a simple test scanner
    class TestScanner(BaseScanner):
        async def scan(self, target: str):
            signals = [Signal("info", "Test signal", {"test": True})]
            return self.create_result(
                ScanStatus.SUCCESS,
                signals,
                "Test summary",
                {"test": "data"}
            )
    
    scanner = TestScanner()
    
    # Test create_result
    result = scanner.create_result(
        ScanStatus.SUCCESS,
        [Signal("info", "Test", {})],
        "Summary",
        {}
    )
    
    assert result["status"] == "success"
    assert len(result["signals"]) == 1
    assert result["summary"] == "Summary"


def test_scanner_degraded_result():
    """Test degraded result creation."""
    from anomradar.scanners import BaseScanner
    
    class TestScanner(BaseScanner):
        async def scan(self, target: str):
            pass
    
    scanner = TestScanner()
    
    error = Exception("Test error")
    result = scanner.create_degraded_result(error, {"partial": "data"})
    
    assert result["status"] == "partial"
    assert "error" in result
    assert result["details"]["partial"] == "data"


def test_scanner_failed_result():
    """Test failed result creation."""
    from anomradar.scanners import BaseScanner
    
    class TestScanner(BaseScanner):
        async def scan(self, target: str):
            pass
    
    scanner = TestScanner()
    
    error = Exception("Test error")
    result = scanner.create_failed_result(error)
    
    assert result["status"] == "failed"
    assert "error" in result
    assert "Test error" in result["error"]
