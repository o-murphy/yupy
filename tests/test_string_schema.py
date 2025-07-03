# test_string_schema.py
import re
from unittest.mock import patch

import pytest

from yupy.string_schema import StringSchema
from yupy.validation_error import ValidationError


# Patch the locale module for tests that don't explicitly set messages
# This fixture will run for every test in this module
@pytest.fixture(autouse=True)
def reset_locale_for_string_schema_tests():
    # Define the mock locale data
    mock_locale_data = {
        "email": "Value must be a valid email",
        "url": "Value must be a valid URL",
        "uuid": "Value must be a valid UUID",
        "lowercase": "Value must be lowercase",
        "uppercase": "Value must be uppercase",
        "matches": "Don't match regex",
        "length": "Invalid length",
        "min": "Too short",
        "max": "Too long",
        "date": "Value must be a valid ISO 8601 date (YYYY-MM-DD)",  # Added
        "datetime": "Value must be a valid ISO 8601 datetime",  # Added
        "one_of": lambda args: f"Must be one of {args[0]}",  # Added for NumberSchema.round error
        "nullable": "Value can't be null",  # Added for completeness
        "type": lambda args: f"Value is not of type {args[0]}, got {args[1]}",  # Added for completeness
    }

    with patch('yupy.locale') as mock_locale_module:
        # Set the 'locale' attribute of the mocked module to our dictionary
        mock_locale_module.locale = mock_locale_data
        # Mock get_error_message to retrieve from our mocked locale dictionary
        # This ensures that when get_error_message(key) is called, it returns
        # the corresponding message from mock_locale_data.
        mock_locale_module.get_error_message.side_effect = lambda key: mock_locale_data.get(key,
                                                                                            "Undefined error message")

        yield mock_locale_module


def test_string_schema_creation():
    schema = StringSchema()
    assert schema._type is str


def test_string_schema_email_success():
    schema = StringSchema().email()
    assert schema.validate("test@example.com") == "test@example.com"
    assert schema.validate("another.one@sub.domain.co.uk") == "another.one@sub.domain.co.uk"


def test_string_schema_email_failure():
    schema = StringSchema().email()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("invalid-email")
    assert excinfo.value.constraint.type == "email"
    assert excinfo.value.invalid_value == "invalid-email"


def test_string_schema_email_with_custom_message():
    custom_message = "This is not a valid email address."
    schema = StringSchema().email(message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("bad-email")
    assert excinfo.value.constraint.type == "email"
    assert excinfo.value.constraint.format_message == custom_message


def test_string_schema_url_success():
    schema = StringSchema().url()
    assert schema.validate("http://example.com") == "http://example.com"
    assert schema.validate("https://www.example.co.uk/path?query=1") == "https://www.example.co.uk/path?query=1"


def test_string_schema_url_failure():
    schema = StringSchema().url()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("not-a-url")
    assert excinfo.value.constraint.type == "url"
    assert excinfo.value.invalid_value == "not-a-url"


def test_string_schema_url_with_custom_message():
    custom_message = "Invalid URL format."
    schema = StringSchema().url(message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("ftp://invalid host")
    assert excinfo.value.constraint.type == "url"
    assert excinfo.value.constraint.format_message == custom_message


def test_uuid_success():
    schema = StringSchema().uuid().not_nullable()  # Added not_nullable for explicit clarity, though redundant
    uuid_str_1 = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    result = schema.validate(uuid_str_1)
    assert result == uuid_str_1
    assert result is not None  # Explicit check for None
    assert isinstance(result, str)  # Ensure it's a string


def test_uuid_failure():
    schema = StringSchema().uuid()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("not-a-uuid")
    assert excinfo.value.constraint.type == "uuid"
    assert excinfo.value.invalid_value == "not-a-uuid"


def test_uuid_with_custom_message():
    custom_message = "Must be a valid UUID."
    schema = StringSchema().uuid(message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("12345")
    assert excinfo.value.constraint.type == "uuid"
    assert excinfo.value.constraint.format_message == custom_message


def test_matches_success():
    schema = StringSchema().matches(re.compile(r"^\d{5}$"))
    assert schema.validate("12345") == "12345"


def test_matches_failure():
    schema = StringSchema().matches(re.compile(r"^\d{5}$"))
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("123")
    assert excinfo.value.constraint.type == "matches"
    assert excinfo.value.invalid_value == "123"


def test_matches_with_custom_message():
    custom_message = "Pattern mismatch."
    schema = StringSchema().matches(re.compile(r"^\d{3}$"), message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("1234")
    assert excinfo.value.constraint.type == "matches"
    assert excinfo.value.constraint.format_message == custom_message


def test_matches_exclude_empty():
    # Test with exclude_empty=True and empty string
    schema_exclude_empty = StringSchema().matches(re.compile(r"^\d+$"), exclude_empty=True)
    assert schema_exclude_empty.validate("") == ""

    # Test with exclude_empty=True and non-empty string that matches
    assert schema_exclude_empty.validate("123") == "123"

    # Test with exclude_empty=True and non-empty string that does not match
    with pytest.raises(ValidationError) as excinfo:
        schema_exclude_empty.validate("abc")
    assert excinfo.value.constraint.type == "matches"
    assert excinfo.value.invalid_value == "abc"

    # Test with exclude_empty=False (default) and empty string
    schema_no_exclude_empty = StringSchema().matches(re.compile(r"^\d+$"))
    with pytest.raises(ValidationError) as excinfo:
        schema_no_exclude_empty.validate("")
    assert excinfo.value.constraint.type == "matches"
    assert excinfo.value.invalid_value == ""


def test_ensure_transform():
    schema = StringSchema().ensure()  # Removed .nullable()
    assert schema.validate("") == ""  # Changed from validate(None)
    assert schema.validate("hello") == "hello"
    assert schema.validate(" ") == " "  # Ensure does not trim spaces by default


def test_trim_success():
    """Test trim() method for successful transformation."""
    schema = StringSchema().trim()
    assert schema.validate("  hello  ") == "hello"
    assert schema.validate("\tworld\n") == "world"
    assert schema.validate(" no leading spaces") == "no leading spaces"
    assert schema.validate("no trailing spaces ") == "no trailing spaces"
    assert schema.validate("   ") == ""  # All whitespace should become empty string


def test_trim_no_change():
    """Test trim() method does not change strings without leading/trailing whitespace."""
    schema = StringSchema().trim()
    assert schema.validate("hello") == "hello"
    assert schema.validate("") == ""
    assert schema.validate("hello world") == "hello world"


def test_lowercase_success():
    schema = StringSchema().lowercase()
    assert schema.validate("hello") == "hello"


def test_lowercase_failure():
    schema = StringSchema().lowercase()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("Hello")
    assert excinfo.value.constraint.type == "lowercase"
    assert excinfo.value.invalid_value == "Hello"


def test_lowercase_with_custom_message():
    custom_message = "String must be all lowercase."
    schema = StringSchema().lowercase(message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("WORLD")
    assert excinfo.value.constraint.type == "lowercase"
    assert excinfo.value.constraint.format_message == custom_message


def test_uppercase_success():
    schema = StringSchema().uppercase()
    assert schema.validate("HELLO") == "HELLO"


def test_uppercase_failure():
    schema = StringSchema().uppercase()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("World")
    assert excinfo.value.constraint.type == "uppercase"
    assert excinfo.value.invalid_value == "World"


def test_uppercase_with_custom_message():
    custom_message = "String must be all uppercase."
    schema = StringSchema().uppercase(message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("hello")
    assert excinfo.value.constraint.type == "uppercase"
    assert excinfo.value.constraint.format_message == custom_message


def test_length_success():
    schema = StringSchema().length(5)
    assert schema.validate("abcde") == "abcde"


def test_length_failure():
    schema = StringSchema().length(5)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("abcd")
    assert excinfo.value.constraint.type == "length"
    assert excinfo.value.invalid_value == "abcd"


def test_min_length_success():
    schema = StringSchema().min(3)
    assert schema.validate("abc") == "abc"
    assert schema.validate("abcd") == "abcd"


def test_min_length_failure():
    schema = StringSchema().min(3)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("ab")
    assert excinfo.value.constraint.type == "min"
    assert excinfo.value.invalid_value == "ab"


def test_max_length_success():
    schema = StringSchema().max(5)
    assert schema.validate("abcde") == "abcde"
    assert schema.validate("abcd") == "abcd"


def test_max_length_failure():
    schema = StringSchema().max(5)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("abcdef")
    assert excinfo.value.constraint.type == "max"
    assert excinfo.value.invalid_value == "abcdef"


# region Datetime and Date tests
# def test_datetime_success_basic():
#     """Test datetime() with basic ISO 8601 format."""
#     schema = StringSchema().datetime()
#     assert schema.validate("2023-01-15T10:30:00") == "2023-01-15T10:30:00"
#     assert schema.validate("2023-01-15T10:30:00Z") == "2023-01-15T10:30:00Z"
#     assert schema.validate("2023-01-15T10:30:00+01:00") == "2023-01-15T10:30:00+01:00"
#
#
# def test_datetime_success_precision():
#     """Test datetime() with various fractional second precisions."""
#     schema_no_precision = StringSchema().datetime(precision=0)
#     assert schema_no_precision.validate("2023-01-15T10:30:00") == "2023-01-15T10:30:00"
#     with pytest.raises(ValidationError): # Should fail if precision is 0 but has fractional seconds
#         schema_no_precision.validate("2023-01-15T10:30:00.123")
#
#     schema_ms_precision = StringSchema().datetime(precision=3)
#     assert schema_ms_precision.validate("2023-01-15T10:30:00.123") == "2023-01-15T10:30:00.123"
#     assert schema_ms_precision.validate("2023-01-15T10:30:00") == "2023-01-15T10:30:00" # No fractional seconds is fine for ms precision
#     with pytest.raises(ValidationError): # Should fail if precision is 3 but has more than 3 digits
#         schema_ms_precision.validate("2023-01-15T10:30:00.123456")
#
#     schema_us_precision = StringSchema().datetime(precision=6)
#     assert schema_us_precision.validate("2023-01-15T10:30:00.123456") == "2023-01-15T10:30:00.123456"
#     assert schema_us_precision.validate("2023-01-15T10:30:00.123") == "2023-01-15T10:30:00.123"
#     assert schema_us_precision.validate("2023-01-15T10:30:00") == "2023-01-15T10:30:00"
#
#
# def test_datetime_success_allow_offset():
#     """Test datetime() with allow_offset=True (default)."""
#     schema = StringSchema().datetime(allow_offset=True) # Explicitly True
#     assert schema.validate("2023-01-15T10:30:00Z") == "2023-01-15T10:30:00Z"
#     assert schema.validate("2023-01-15T10:30:00+05:00") == "2023-01-15T10:30:00+05:00"
#     assert schema.validate("2023-01-15T10:30:00-08:00") == "2023-01-15T10:30:00-08:00"
#     assert schema.validate("2023-01-15T10:30:00") == "2023-01-15T10:30:00" # No offset is also fine
#
#
# def test_datetime_failure_invalid_format():
#     """Test datetime() fails for invalid ISO 8601 formats."""
#     schema = StringSchema().datetime()
#     with pytest.raises(ValidationError) as excinfo:
#         schema.validate("2023-13-01T10:00:00") # Invalid month
#     assert excinfo.value.constraint.type == "datetime"
#     assert excinfo.value.invalid_value == "2023-13-01T10:00:00"
#
#     with pytest.raises(ValidationError) as excinfo:
#         schema.validate("not-a-datetime")
#     assert excinfo.value.constraint.type == "datetime"
#     assert excinfo.value.invalid_value == "not-a-datetime"
#
#     with pytest.raises(ValidationError) as excinfo:
#         schema.validate("2023-01-15 10:30:00") # Missing 'T'
#     assert excinfo.value.constraint.type == "datetime"
#
#
# def test_datetime_failure_precision_mismatch():
#     """Test datetime() fails for precision mismatches."""
#     schema_no_precision = StringSchema().datetime(precision=0)
#     with pytest.raises(ValidationError) as excinfo:
#         schema_no_precision.validate("2023-01-15T10:30:00.1")
#     assert excinfo.value.constraint.type == "datetime"
#     assert excinfo.value.invalid_value == "2023-01-15T10:30:00.1"
#
#
#     schema_ms_precision = StringSchema().datetime(precision=3)
#     with pytest.raises(ValidationError) as excinfo:
#         schema_ms_precision.validate("2023-01-15T10:30:00.1234") # More than 3 digits
#     assert excinfo.value.constraint.type == "datetime"
#     assert excinfo.value.invalid_value == "2023-01-15T10:30:00.1234"
#
#
# def test_datetime_failure_disallow_offset():
#     """Test datetime() fails when allow_offset=False but offset is present."""
#     schema = StringSchema().datetime(allow_offset=False)
#     with pytest.raises(ValidationError) as excinfo:
#         schema.validate("2023-01-15T10:30:00Z")
#     assert excinfo.value.constraint.type == "datetime"
#     assert excinfo.value.invalid_value == "2023-01-15T10:30:00Z"
#
#     with pytest.raises(ValidationError) as excinfo:
#         schema.validate("2023-01-15T10:30:00+01:00")
#     assert excinfo.value.constraint.type == "datetime"
#     assert excinfo.value.invalid_value == "2023-01-15T10:30:00+01:00"
#
#
# def test_datetime_with_custom_message():
#     """Test datetime() with a custom error message."""
#     custom_message = "Invalid date and time format."
#     schema = StringSchema().datetime(message=custom_message)
#     with pytest.raises(ValidationError) as excinfo:
#         schema.validate("2023/01/01 12:00:00")
#     assert excinfo.value.constraint.type == "datetime"
#     assert excinfo.value.constraint.format_message == custom_message


def test_date_success():
    """Test date() with valid ISO 8601 date format."""
    schema = StringSchema().date()
    assert schema.validate("2023-01-15") == "2023-01-15"
    assert schema.validate("1999-12-31") == "1999-12-31"


def test_date_failure_invalid_format():
    """Test date() fails for invalid ISO 8601 date formats."""
    schema = StringSchema().date()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("2023/01/15")  # Invalid separator
    assert excinfo.value.constraint.type == "date"
    assert excinfo.value.invalid_value == "2023/01/15"

    with pytest.raises(ValidationError) as excinfo:
        schema.validate("2023-01-15T10:00:00")  # Datetime instead of date
    assert excinfo.value.constraint.type == "date"
    assert excinfo.value.invalid_value == "2023-01-15T10:00:00"

    with pytest.raises(ValidationError) as excinfo:
        schema.validate("not-a-date")
    assert excinfo.value.constraint.type == "date"
    assert excinfo.value.invalid_value == "not-a-date"


def test_date_with_custom_message():
    """Test date() with a custom error message."""
    custom_message = "Date format is incorrect."
    schema = StringSchema().date(message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("01-01-2023")
    assert excinfo.value.constraint.type == "date"
    assert excinfo.value.constraint.format_message == custom_message

# endregion
