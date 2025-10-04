"""Tests for input validation and security."""
import pytest
from bazel_mcp.validation import (
    validate_bazel_target,
    validate_bazel_targets,
    validate_bazel_flag,
    validate_bazel_flags,
    validate_query_expression,
    validate_runtime_args,
    ValidationError,
)


class TestBazelTargetValidation:
    """Tests for Bazel target validation."""
    
    def test_valid_absolute_target(self):
        """Test validation of absolute target labels."""
        assert validate_bazel_target("//src:app") == "//src:app"
        assert validate_bazel_target("//src/main:app") == "//src/main:app"
        assert validate_bazel_target("//src/main/foo:bar_test") == "//src/main/foo:bar_test"
    
    def test_valid_external_target(self):
        """Test validation of external repository targets."""
        assert validate_bazel_target("@repo//src:app") == "@repo//src:app"
        assert validate_bazel_target("@my-repo//path:target") == "@my-repo//path:target"
    
    def test_valid_relative_target(self):
        """Test validation of relative target labels."""
        assert validate_bazel_target(":app") == ":app"
        assert validate_bazel_target(":test_target") == ":test_target"
    
    def test_valid_wildcard(self):
        """Test validation of wildcard target."""
        assert validate_bazel_target("//...") == "//..."
    
    def test_command_injection_semicolon(self):
        """Test rejection of command injection with semicolon."""
        with pytest.raises(ValidationError, match="forbidden character"):
            validate_bazel_target("//src:app; rm -rf /")
    
    def test_command_injection_pipe(self):
        """Test rejection of command injection with pipe."""
        with pytest.raises(ValidationError, match="forbidden character"):
            validate_bazel_target("//src:app | cat /etc/passwd")
    
    def test_command_injection_ampersand(self):
        """Test rejection of command injection with ampersand."""
        with pytest.raises(ValidationError, match="forbidden character"):
            validate_bazel_target("//src:app && malicious")
    
    def test_command_injection_backticks(self):
        """Test rejection of command injection with backticks."""
        with pytest.raises(ValidationError, match="forbidden character"):
            validate_bazel_target("//src:`whoami`")
    
    def test_command_injection_dollar(self):
        """Test rejection of command injection with dollar signs."""
        with pytest.raises(ValidationError, match="forbidden character"):
            validate_bazel_target("//src:$MALICIOUS")
    
    def test_command_injection_redirect(self):
        """Test rejection of output redirection."""
        with pytest.raises(ValidationError, match="forbidden character"):
            validate_bazel_target("//src:app > /tmp/evil")
    
    def test_empty_target(self):
        """Test rejection of empty target."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_bazel_target("")
    
    def test_invalid_format(self):
        """Test rejection of invalid target format."""
        with pytest.raises(ValidationError, match="Invalid Bazel target label"):
            validate_bazel_target("not-a-valid-target")
    
    def test_too_long_target(self):
        """Test rejection of excessively long target."""
        long_target = "//src:" + "a" * 600
        with pytest.raises(ValidationError, match="too long"):
            validate_bazel_target(long_target)


class TestBazelTargetsValidation:
    """Tests for validating lists of targets."""
    
    def test_valid_targets_list(self):
        """Test validation of valid target list."""
        targets = ["//src:app", "//lib:common", "//test:unit_test"]
        result = validate_bazel_targets(targets)
        assert result == targets
    
    def test_empty_targets_list(self):
        """Test rejection of empty target list."""
        with pytest.raises(ValidationError, match="At least one target"):
            validate_bazel_targets([])
    
    def test_too_many_targets(self):
        """Test rejection of too many targets."""
        targets = [f"//src:target{i}" for i in range(101)]
        with pytest.raises(ValidationError, match="Too many targets"):
            validate_bazel_targets(targets)
    
    def test_invalid_target_in_list(self):
        """Test rejection when one target in list is invalid."""
        targets = ["//src:app", "//src:app; rm -rf /", "//test:foo"]
        with pytest.raises(ValidationError):
            validate_bazel_targets(targets)


class TestBazelFlagValidation:
    """Tests for Bazel flag validation."""
    
    def test_valid_flags(self):
        """Test validation of valid flags."""
        assert validate_bazel_flag("--config=debug") == "--config=debug"
        assert validate_bazel_flag("--test_filter=MyTest.*") == "--test_filter=MyTest.*"
        assert validate_bazel_flag("--verbose_failures") == "--verbose_failures"
        assert validate_bazel_flag("-c") == "-c"
    
    def test_flag_with_path(self):
        """Test validation of flags with paths."""
        assert validate_bazel_flag("--output_base=/tmp/bazel") == "--output_base=/tmp/bazel"
    
    def test_command_injection_in_flag(self):
        """Test rejection of command injection in flag."""
        with pytest.raises(ValidationError, match="forbidden character"):
            validate_bazel_flag("--config=debug; rm -rf /")
    
    def test_invalid_flag_format(self):
        """Test rejection of invalid flag format."""
        with pytest.raises(ValidationError, match="Invalid Bazel flag format"):
            validate_bazel_flag("not-a-flag")
    
    def test_too_long_flag(self):
        """Test rejection of excessively long flag."""
        long_flag = "--flag=" + "a" * 600
        with pytest.raises(ValidationError, match="too long"):
            validate_bazel_flag(long_flag)


class TestBazelFlagsValidation:
    """Tests for validating lists of flags."""
    
    def test_valid_flags_list(self):
        """Test validation of valid flags list."""
        flags = ["--config=debug", "--verbose_failures", "--test_output=all"]
        result = validate_bazel_flags(flags)
        assert result == flags
    
    def test_none_flags(self):
        """Test that None returns empty list."""
        assert validate_bazel_flags(None) == []
    
    def test_empty_flags_list(self):
        """Test that empty list is valid."""
        assert validate_bazel_flags([]) == []
    
    def test_too_many_flags(self):
        """Test rejection of too many flags."""
        flags = [f"--flag{i}=value" for i in range(51)]
        with pytest.raises(ValidationError, match="Too many flags"):
            validate_bazel_flags(flags)


class TestQueryExpressionValidation:
    """Tests for Bazel query expression validation."""
    
    def test_valid_query_expressions(self):
        """Test validation of valid query expressions."""
        assert validate_query_expression("//...") == "//..."
        assert validate_query_expression("deps(//src:app)") == "deps(//src:app)"
        assert validate_query_expression("rdeps(//..., //lib:common)") == "rdeps(//..., //lib:common)"
        assert validate_query_expression("kind('cc_test', //...)") == "kind('cc_test', //...)"
    
    def test_command_injection_in_query(self):
        """Test rejection of command injection in query."""
        with pytest.raises(ValidationError, match="forbidden character"):
            validate_query_expression("deps(//src:app); rm -rf /")
    
    def test_query_with_pipe(self):
        """Test rejection of pipe in query."""
        with pytest.raises(ValidationError, match="forbidden character"):
            validate_query_expression("deps(//src:app) | evil")
    
    def test_empty_query(self):
        """Test rejection of empty query."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_query_expression("")
    
    def test_invalid_query_format(self):
        """Test rejection of query without valid indicators."""
        with pytest.raises(ValidationError, match="does not appear to be a valid"):
            validate_query_expression("random text")
    
    def test_too_long_query(self):
        """Test rejection of excessively long query."""
        long_query = "deps(" + "a" * 2100 + ")"
        with pytest.raises(ValidationError, match="too long"):
            validate_query_expression(long_query)


class TestRuntimeArgsValidation:
    """Tests for runtime arguments validation."""
    
    def test_valid_runtime_args(self):
        """Test validation of valid runtime arguments."""
        args = ["--port=8080", "--host=localhost", "input.txt"]
        result = validate_runtime_args(args)
        assert result == args
    
    def test_none_runtime_args(self):
        """Test that None returns empty list."""
        assert validate_runtime_args(None) == []
    
    def test_empty_args_list(self):
        """Test that empty list is valid."""
        assert validate_runtime_args([]) == []
    
    def test_command_injection_in_args(self):
        """Test rejection of command injection in arguments."""
        with pytest.raises(ValidationError, match="dangerous character"):
            validate_runtime_args(["arg1", "arg2; rm -rf /"])
    
    def test_too_many_args(self):
        """Test rejection of too many arguments."""
        args = [f"arg{i}" for i in range(101)]
        with pytest.raises(ValidationError, match="Too many runtime arguments"):
            validate_runtime_args(args)
    
    def test_too_long_arg(self):
        """Test rejection of excessively long argument."""
        long_arg = "a" * 1100
        with pytest.raises(ValidationError, match="too long"):
            validate_runtime_args([long_arg])


class TestEdgeCases:
    """Tests for edge cases and combined scenarios."""
    
    def test_unicode_in_target(self):
        """Test that unicode characters are rejected."""
        with pytest.raises(ValidationError):
            validate_bazel_target("//src:app™")
    
    def test_newline_in_flag(self):
        """Test that newlines are rejected."""
        with pytest.raises(ValidationError, match="forbidden character"):
            validate_bazel_flag("--flag=value\nmalicious")
    
    def test_multiple_injections_in_target(self):
        """Test that multiple injection attempts are caught."""
        with pytest.raises(ValidationError, match="forbidden character"):
            validate_bazel_target("//src:app; echo `whoami` & evil")
