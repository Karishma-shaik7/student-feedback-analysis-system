"""
Unit tests for configuration loading and validation.
"""

import pytest
from config import get_config, DevelopmentConfig, TestingConfig, ProductionConfig


def test_development_config():
    """Verify development defaults."""
    cfg = get_config("development")
    assert cfg.DEBUG is True
    assert cfg.MYSQL_PORT == 3306
    safe = cfg.get_safe_info()
    assert "mysql_password" not in safe
    assert "mysql_password_configured" in safe


def test_testing_config():
    """Verify testing configuration defaults."""
    cfg = get_config("testing")
    assert cfg.TESTING is True
    assert cfg.SECRET_KEY == "test-secret-key-for-automated-tests"


def test_production_config_validation():
    """Verify production requires non-default secret key."""
    # With default key, validate() should raise ValueError
    ProductionConfig.SECRET_KEY = ProductionConfig._DEFAULT_DEV_SECRET
    with pytest.raises(ValueError, match="CRITICAL: FLASK_SECRET_KEY must be set"):
        ProductionConfig.validate()

    # With proper key, validate() passes
    ProductionConfig.SECRET_KEY = "super-secret-production-token-1234567890"
    ProductionConfig.validate()
