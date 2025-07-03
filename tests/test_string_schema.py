# test_string_schema.py
import pytest
from unittest.mock import patch, MagicMock
from yupy.validation_error import ValidationError, Constraint, _EMPTY_MESSAGE_
from yupy.string_schema import StringSchema
from typing import List, Any
import re

# Patch the locale module for tests that don't explicitly set messages
# This fixture will run for every test in this module
@pytest.fixture(autouse=True)
def reset_locale_for_string_schema_tests():
    with patch('yupy.locale') as mock_locale_module:
        mock_locale_module.get_error_message = MagicMock(return_value="Default error message")
        # Ensure 'locale' dictionary is also mocked if it's accessed directly
        mock_locale_module.locale = {
            "email": "Value must be a valid email",
            "url": "Value must be a valid URL",
            "uuid": "Value must be a valid UUID",
            "lowercase": "Value must be lowercase",
            "uppercase": "Value must be uppercase",
            "matches": "Don't match regex",
            "length": "Invalid length",
            "min": "Too short",
            "max": "Too long",
        }
        yield mock_locale_module

def test_string_schema_creation():
    schema = StringSchema()
    assert schema._type == str

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
    schema = StringSchema().uuid().not_nullable() # Added not_nullable for explicit clarity, though redundant
    uuid_str_1 = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    result = schema.validate(uuid_str_1)
    assert result == uuid_str_1
    assert result is not None  # Explicit check for None
    assert isinstance(result, str) # Ensure it's a string

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
    schema = StringSchema().ensure() # Removed .nullable()
    assert schema.validate("") == "" # Changed from validate(None)
    assert schema.validate("hello") == "hello"
    assert schema.validate(" ") == " " # Ensure does not trim spaces by default

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