"""Input validation and sanitization for Bazel MCP server.

This module provides security-focused validation to prevent command injection
and ensure safe execution of Bazel commands.
"""
from __future__ import annotations
import re
from typing import Sequence


# Bazel target label pattern: //path/to:target or @repo//path:target
# Also supports relative labels like :target or //...
BAZEL_TARGET_PATTERN = re.compile(
    r'^(@[\w\-\.]+)?//[\w\-\./]*(:[\w\-\.\+]+)?$|'  # Absolute: //foo/bar:baz or @repo//foo:bar
    r'^:[\w\-\.\+]+$|'  # Relative: :target
    r'^//\.\.\.$'  # Wildcard: //...
)

# Safe Bazel flag pattern - must start with -- or -
# Allows alphanumeric, underscore, hyphen, equals, and common safe characters
# Includes asterisk and plus for test filters and glob patterns
BAZEL_FLAG_PATTERN = re.compile(r'^-{1,2}[\w\-]+(=[\w\-\./,:@\[\]\*\+]*)?$')

# Dangerous characters that should never appear in user inputs
DANGEROUS_CHARS = [';', '|', '&', '$', '`', '\n', '\r', '>', '<', '(', ')', '{', '}']


class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass


def validate_bazel_target(target: str) -> str:
    """
    Validate a Bazel target label.
    
    Args:
        target: Bazel target label to validate
        
    Returns:
        The validated target string (unchanged if valid)
        
    Raises:
        ValidationError: If the target is invalid or potentially malicious
        
    Examples:
        >>> validate_bazel_target("//src:app")
        '//src:app'
        >>> validate_bazel_target("//src:app; rm -rf /")
        Traceback (most recent call last):
        ...
        ValidationError: Invalid Bazel target label
    """
    if not target or not isinstance(target, str):
        raise ValidationError("Target must be a non-empty string")
    
    # Check for dangerous characters
    for char in DANGEROUS_CHARS:
        if char in target:
            raise ValidationError(
                f"Target contains forbidden character: {repr(char)}"
            )
    
    # Check length to prevent DoS
    if len(target) > 500:
        raise ValidationError("Target label too long (max 500 characters)")
    
    # Validate against pattern
    if not BAZEL_TARGET_PATTERN.match(target):
        raise ValidationError(
            f"Invalid Bazel target label: {target!r}. "
            "Expected format: //path/to:target, @repo//path:target, or :target"
        )
    
    return target


def validate_bazel_targets(targets: Sequence[str]) -> list[str]:
    """
    Validate a list of Bazel target labels.
    
    Args:
        targets: List of Bazel target labels to validate
        
    Returns:
        List of validated target strings
        
    Raises:
        ValidationError: If any target is invalid
    """
    if not targets:
        raise ValidationError("At least one target must be specified")
    
    if not isinstance(targets, (list, tuple)):
        raise ValidationError("Targets must be a list or tuple")
    
    if len(targets) > 100:
        raise ValidationError("Too many targets (max 100)")
    
    validated = []
    for target in targets:
        validated.append(validate_bazel_target(target))
    
    return validated


def validate_bazel_flag(flag: str) -> str:
    """
    Validate a Bazel command-line flag.
    
    Args:
        flag: Bazel flag to validate
        
    Returns:
        The validated flag string (unchanged if valid)
        
    Raises:
        ValidationError: If the flag is invalid or potentially malicious
        
    Examples:
        >>> validate_bazel_flag("--config=debug")
        '--config=debug'
        >>> validate_bazel_flag("--flag; rm -rf /")
        Traceback (most recent call last):
        ...
        ValidationError: Flag contains forbidden character
    """
    if not flag or not isinstance(flag, str):
        raise ValidationError("Flag must be a non-empty string")
    
    # Check for dangerous characters
    for char in DANGEROUS_CHARS:
        if char in flag:
            raise ValidationError(
                f"Flag contains forbidden character: {repr(char)}"
            )
    
    # Check length
    if len(flag) > 500:
        raise ValidationError("Flag too long (max 500 characters)")
    
    # Validate against pattern
    if not BAZEL_FLAG_PATTERN.match(flag):
        raise ValidationError(
            f"Invalid Bazel flag format: {flag!r}. "
            "Flags must start with - or -- and contain only safe characters"
        )
    
    return flag


def validate_bazel_flags(flags: Sequence[str] | None) -> list[str]:
    """
    Validate a list of Bazel flags.
    
    Args:
        flags: List of Bazel flags to validate, or None
        
    Returns:
        List of validated flags (empty list if None)
        
    Raises:
        ValidationError: If any flag is invalid
    """
    if flags is None:
        return []
    
    if not isinstance(flags, (list, tuple)):
        raise ValidationError("Flags must be a list or tuple")
    
    if len(flags) > 50:
        raise ValidationError("Too many flags (max 50)")
    
    validated = []
    for flag in flags:
        validated.append(validate_bazel_flag(flag))
    
    return validated


def validate_query_expression(expr: str) -> str:
    """
    Validate a Bazel query expression.
    
    Args:
        expr: Bazel query expression to validate
        
    Returns:
        The validated expression string (unchanged if valid)
        
    Raises:
        ValidationError: If the expression is invalid or potentially malicious
    """
    if not expr or not isinstance(expr, str):
        raise ValidationError("Query expression must be a non-empty string")
    
    # Check for dangerous characters
    for char in [';', '|', '&', '$', '`', '\n', '\r']:
        if char in expr:
            raise ValidationError(
                f"Query expression contains forbidden character: {repr(char)}"
            )
    
    # Check length to prevent DoS
    if len(expr) > 2000:
        raise ValidationError("Query expression too long (max 2000 characters)")
    
    # Basic sanity check - should contain at least one of: //, :, or common functions
    # This prevents completely arbitrary strings while allowing valid queries
    query_indicators = ['//', ':', 'deps(', 'rdeps(', 'kind(', 'attr(', 'filter(']
    if not any(indicator in expr for indicator in query_indicators):
        raise ValidationError(
            "Query expression does not appear to be a valid Bazel query. "
            f"Expected patterns like '//', ':', or query functions"
        )
    
    return expr


def validate_runtime_args(args: Sequence[str] | None) -> list[str]:
    """
    Validate runtime arguments passed to a binary.
    
    These are less restrictive than Bazel flags since they're passed after --
    to the actual binary, but we still check for shell injection attempts.
    
    Args:
        args: List of runtime arguments to validate, or None
        
    Returns:
        List of validated arguments (empty list if None)
        
    Raises:
        ValidationError: If any argument appears malicious
    """
    if args is None:
        return []
    
    if not isinstance(args, (list, tuple)):
        raise ValidationError("Runtime arguments must be a list or tuple")
    
    if len(args) > 100:
        raise ValidationError("Too many runtime arguments (max 100)")
    
    validated = []
    for arg in args:
        if not isinstance(arg, str):
            raise ValidationError("Runtime arguments must be strings")
        
        # Check for obvious shell injection attempts
        dangerous_patterns = [';', '|', '&', '$', '`', '\n', '\r']
        for pattern in dangerous_patterns:
            if pattern in arg:
                raise ValidationError(
                    f"Runtime argument contains potentially dangerous character: {repr(pattern)}"
                )
        
        if len(arg) > 1000:
            raise ValidationError("Runtime argument too long (max 1000 characters)")
        
        validated.append(arg)
    
    return validated


def sanitize_for_display(text: str, max_length: int = 1000) -> str:
    """
    Sanitize text for safe display in logs/output.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length to return
        
    Returns:
        Sanitized text safe for display
    """
    if not text:
        return ""
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "... (truncated)"
    
    # Remove control characters except newlines and tabs
    sanitized = ''.join(
        char for char in text 
        if char in '\n\t' or not char.isspace() or char == ' '
    )
    
    return sanitized
