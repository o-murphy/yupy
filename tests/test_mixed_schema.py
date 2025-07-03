# File: test_mixed_schema.py
from typing import Any

import pytest

from yupy.icomparable_schema import EqualityComparableSchema
from yupy.locale import locale
from yupy.mixed_schema import MixedSchema
from yupy.schema import Schema
from yupy.validation_error import ValidationError


# Fixture to ensure isolation of tests that might modify the global 'locale'
@pytest.fixture(autouse=True)
def reset_locale_for_mixed_schema_tests():
    original_locale = locale.copy()
    yield
    locale.clear()
    locale.update(original_locale)


def test_mixed_schema_inheritance():
    """Test that MixedSchema inherits from EqualityComparableSchema."""
    schema = MixedSchema()
    assert isinstance(schema, EqualityComparableSchema)
    assert isinstance(schema, Schema)  # Also check grand-parent


def test_of_success_matching_type():
    """Test of() method for successful validation with matching type."""
    schema = MixedSchema().of(int)
    result = schema.validate(123)
    assert result == 123

    schema_str = MixedSchema().of(str)
    result_str = schema_str.validate("hello")
    assert result_str == "hello"


def test_of_success_any_type():
    """Test of() method for successful validation when type is Any."""
    schema = MixedSchema().of(Any)
    result_int = schema.validate(123)
    assert result_int == 123
    result_str = schema.validate("hello")
    assert result_str == "hello"
    # This should now pass because the schema is not nullable by default,
    # and the test does not make it nullable, so None should fail at _nullable_check
    with pytest.raises(ValidationError) as excinfo:
        MixedSchema().of(Any).validate(None)
    assert excinfo.value.constraint.type == "nullable"

    # When the schema is explicitly made nullable, it should pass for None
    schema_nullable = MixedSchema().nullable().of(Any)
    result_none = schema_nullable.validate(None)
    assert result_none is None


def test_of_failure_non_matching_type():
    """Test of() method for failed validation with non-matching type."""
    schema = MixedSchema().of(int)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("not_an_int")

    error = excinfo.value
    assert error.constraint.type == "type"
    assert error.path == "~"  # Default path from Schema.validate
    assert error.invalid_value == "not_an_int"
    # The locale's 'type' message is a callable, so we simulate its call
    expected_message = locale["type"]((int, type("not_an_int")))  # Expected type and actual type
    assert error.constraint.format_message == expected_message


def test_of_failure_with_custom_message():
    """Test of() method for failed validation with a custom message."""
    custom_message = "Value must be a number!"
    schema = MixedSchema().of(int, message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("abc")

    error = excinfo.value
    assert error.constraint.type == "type"
    assert error.constraint.message == custom_message
    assert error.invalid_value == "abc"


def test_one_of_success():
    """Test one_of() method for successful validation."""
    schema = MixedSchema().one_of(["apple", "banana", "cherry"])
    result = schema.validate("banana")
    assert result == "banana"

    schema_int = MixedSchema().one_of([1, 2, 3])
    result_int = schema_int.validate(2)
    assert result_int == 2


def test_one_of_failure():
    """Test one_of() method for failed validation."""
    schema = MixedSchema().one_of(["apple", "banana", "cherry"])
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("grape")

    error = excinfo.value
    assert error.constraint.type == "one_of"
    assert error.path == "~"
    assert error.invalid_value == "grape"
    expected_message = locale["one_of"]((["apple", "banana", "cherry"],))  # Items passed to one_of
    assert error.constraint.format_message == expected_message


def test_one_of_failure_with_custom_message():
    """Test one_of() method for failed validation with a custom message."""
    custom_message = "Choose from the allowed list!"
    schema = MixedSchema().one_of(["red", "green", "blue"], message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("yellow")

    error = excinfo.value
    assert error.constraint.type == "one_of"
    assert error.constraint.message == custom_message
    assert error.invalid_value == "yellow"


def test_mixed_schema_combined_constraints():
    """Test MixedSchema with a combination of constraints (e.g., eq and of)."""
    # Schema: value must be an integer and equal to 10
    schema = MixedSchema().of(int).eq(10)
    result = schema.validate(10)
    assert result == 10

    with pytest.raises(ValidationError):
        schema.validate("10")  # Fails 'of(int)'

    with pytest.raises(ValidationError):
        schema.validate(5)  # Fails 'eq(10)'

    # Schema: value must be a string and one of "cat", "dog"
    schema_animal = MixedSchema().of(str).one_of(["cat", "dog"])
    result_animal = schema_animal.validate("cat")
    assert result_animal == "cat"

    with pytest.raises(ValidationError):
        schema_animal.validate(123)  # Fails 'of(str)'

    with pytest.raises(ValidationError):
        schema_animal.validate("bird")  # Fails 'one_of'


def test_mixed_schema_nullable_behavior():
    """Test nullable behavior with MixedSchema methods."""
    # This test case should now pass due to the change in Schema.validate
    schema_nullable_of = MixedSchema().nullable().of(int)
    result = schema_nullable_of.validate(None)
    assert result is None

    # This still correctly fails as schema is not nullable by default
    schema_not_nullable_of = MixedSchema().of(int)
    with pytest.raises(ValidationError):
        schema_not_nullable_of.validate(None)

    # This test case should now pass due to the change in Schema.validate
    schema_nullable_one_of = MixedSchema().nullable().one_of([1, 2, 3])
    result = schema_nullable_one_of.validate(None)
    assert result is None

    # This still correctly fails as schema is not nullable by default
    schema_not_nullable_one_of = MixedSchema().one_of([1, 2, 3])
    with pytest.raises(ValidationError):
        schema_not_nullable_one_of.validate(None)
