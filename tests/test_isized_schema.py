import pytest

from yupy.isized_schema import SizedSchema, ISizedSchema
from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ValidationError


# Fixture to ensure isolation of tests that might modify the global 'locale'
@pytest.fixture(autouse=True)
def reset_locale_for_sized_schema_tests():
    original_locale = locale.copy()
    yield
    locale.clear()
    locale.update(original_locale)


def test_sized_schema_inheritance():
    """Test that SizedSchema inherits from Schema."""
    schema = SizedSchema()
    assert isinstance(schema, Schema)


def test_length_success():
    """Test length() method for successful validation."""
    schema = SizedSchema(_type=str).length(5)
    result = schema.validate("hello")
    assert result == "hello"

    schema_list = SizedSchema(_type=list).length(3)
    result_list = schema_list.validate([1, 2, 3])
    assert result_list == [1, 2, 3]


def test_length_failure():
    """Test length() method for failed validation."""
    schema = SizedSchema(_type=str).length(5)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("hi")

    error = excinfo.value
    assert error.constraint.type == "length"
    assert error.path == "~"  # Default path from Schema.validate
    assert error.invalid_value == "hi"
    expected_message = locale["length"]((5,))  # Expected limit
    assert error.constraint.format_message == expected_message


def test_length_failure_with_custom_message():
    """Test length() method for failed validation with a custom message."""
    custom_message = "String length must be exactly 5 chars!"
    schema = SizedSchema(_type=str).length(5, message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("long_string")

    error = excinfo.value
    assert error.constraint.type == "length"
    assert error.constraint.message == custom_message
    assert error.invalid_value == "long_string"


def test_min_success():
    """Test min() method for successful validation."""
    schema = SizedSchema(_type=str).min(5)
    result_long = schema.validate("long_string")
    assert result_long == "long_string"
    result_exact = schema.validate("hello")
    assert result_exact == "hello"


def test_min_failure():
    """Test min() method for failed validation."""
    schema = SizedSchema(_type=str).min(5)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("hi")

    error = excinfo.value
    assert error.constraint.type == "min"
    assert error.path == "~"
    assert error.invalid_value == "hi"
    expected_message = locale["min"]((5,))  # Expected limit
    assert error.constraint.format_message == expected_message


def test_min_failure_with_custom_message():
    """Test min() method for failed validation with a custom message."""
    custom_message = "Value is too short, needs at least 5!"
    schema = SizedSchema(_type=str).min(5, message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("abc")

    error = excinfo.value
    assert error.constraint.type == "min"
    assert error.constraint.message == custom_message
    assert error.invalid_value == "abc"


def test_max_success():
    """Test max() method for successful validation."""
    schema = SizedSchema(_type=str).max(5)
    result_short = schema.validate("hi")
    assert result_short == "hi"
    result_exact = schema.validate("hello")
    assert result_exact == "hello"


def test_max_failure():
    """Test max() method for failed validation."""
    schema = SizedSchema(_type=str).max(5)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("too_long")

    error = excinfo.value
    assert error.constraint.type == "max"
    assert error.path == "~"
    assert error.invalid_value == "too_long"
    expected_message = locale["max"]((5,))  # Expected limit
    assert error.constraint.format_message == expected_message


def test_max_failure_with_custom_message():
    """Test max() method for failed validation with a custom message."""
    custom_message = "Value is too long, max 5 chars!"
    schema = SizedSchema(_type=str).max(5, message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("abcdefg")

    error = excinfo.value
    assert error.constraint.type == "max"
    assert error.constraint.message == custom_message
    assert error.invalid_value == "abcdefg"


def test_multiple_sized_constraints():
    """Test a schema with multiple sized constraints."""
    schema = SizedSchema(_type=str).min(3).max(7).length(5)
    result = schema.validate("abcde")
    assert result == "abcde"

    with pytest.raises(ValidationError):
        schema.validate("ab")  # Too short

    with pytest.raises(ValidationError):
        schema.validate("abcdefgh")  # Too long

    with pytest.raises(ValidationError):
        schema.validate("abcd")  # Not exact length


def test_isized_schema_protocol_conformance():
    """Test if SizedSchema conforms to ISizedSchema protocol."""
    assert isinstance(SizedSchema(), ISizedSchema)

    class CustomSizedSchema(SizedSchema):
        pass

    assert isinstance(CustomSizedSchema(), ISizedSchema)

    # Test a class that doesn't conform
    class NotSizedSchema(Schema):
        pass

    assert not isinstance(NotSizedSchema(), ISizedSchema)
