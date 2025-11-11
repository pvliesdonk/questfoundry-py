"""Tests for logging configuration."""

import logging

from questfoundry.logging_config import (
    TRACE,
    TraceFormatter,
    get_logger,
    setup_logging,
)


def test_trace_level_defined():
    """Test TRACE level is defined."""
    assert TRACE == 5
    assert logging.getLevelName(TRACE) == "TRACE"


def test_trace_formatter_default_format():
    """Test TraceFormatter with default format."""
    formatter = TraceFormatter()
    assert formatter is not None
    assert isinstance(formatter, logging.Formatter)


def test_trace_formatter_without_module():
    """Test TraceFormatter without module information."""
    formatter = TraceFormatter(include_module=False)
    assert formatter is not None


def test_trace_formatter_custom_format():
    """Test TraceFormatter with custom format."""
    formatter = TraceFormatter(fmt="%(levelname)s - %(message)s")
    assert formatter is not None


def test_trace_formatter_format_record():
    """Test TraceFormatter can format a log record."""
    formatter = TraceFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "Test message" in formatted
    assert "INFO" in formatted


def test_setup_logging_default():
    """Test setup_logging with defaults."""
    setup_logging()
    logger = logging.getLogger("questfoundry")
    assert logger.level == logging.INFO


def test_setup_logging_debug():
    """Test setup_logging with DEBUG level."""
    setup_logging(level="DEBUG")
    logger = logging.getLogger("questfoundry")
    assert logger.level == logging.DEBUG


def test_setup_logging_trace():
    """Test setup_logging with TRACE level."""
    setup_logging(level="TRACE")
    logger = logging.getLogger("questfoundry")
    assert logger.level == TRACE


def test_setup_logging_custom_format():
    """Test setup_logging with custom format."""
    setup_logging(format_string="%(levelname)s - %(message)s")
    # Should not raise error
    assert True


def test_setup_logging_without_module():
    """Test setup_logging without module info."""
    setup_logging(include_module=False)
    # Should not raise error
    assert True


def test_get_logger():
    """Test get_logger returns a logger."""
    logger = get_logger("test.module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.module"


def test_logger_trace_method_exists():
    """Test that logger has trace method."""
    logger = get_logger("test")
    assert hasattr(logger, "trace")
    assert callable(logger.trace)


def test_logger_trace_method_works():
    """Test that trace method can be called."""
    logger = get_logger("test")
    logger.setLevel(TRACE)
    # Should not raise error
    logger.trace("Test trace message")  # type: ignore
