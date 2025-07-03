# test_array_schema.py
from unittest.mock import patch, MagicMock

import pytest

from yupy.array_schema import ArraySchema
from yupy.number_schema import NumberSchema
from yupy.schema import Schema
from yupy.string_schema import StringSchema
from yupy.validation_error import ValidationError


# Patch the locale module for tests that don't explicitly set messages
@pytest.fixture(autouse=True)
def reset_locale_for_array_schema_tests():
    with patch('yupy.locale') as mock_locale_module:
        mock_locale_module.get_error_message = MagicMock(return_value="Default error message")
        mock_locale_module.locale = {
            "type": lambda args: "Value is not of type %r, got %r" % args,
            "array": "invalid array",
            "min": lambda args: "Min length must be %r" % args[0],
            "max": lambda args: "Max length must be %r" % args[0],
            "length": lambda args: "Length must be %r" % args[0],
            "nullable": "Value can't be null",  # Added for nullability check
        }
        yield mock_locale_module


def test_array_schema_creation():
    schema = ArraySchema()
    assert schema._type == (list, tuple)
    # Default should be a None
    if schema._of_schema_type is not None:
        assert isinstance(schema._of_schema_type, Schema)
        assert schema._of_schema_type.nullability is True  # It should be nullable by default for 'of'
    assert schema._fields == []


def test_array_schema_of_success_with_string_schema():
    string_schema = StringSchema()
    schema = ArraySchema().of(string_schema)
    assert schema._of_schema_type is string_schema


def test_array_schema_of_success_with_number_schema():
    number_schema = NumberSchema()
    schema = ArraySchema().of(number_schema)
    assert schema._of_schema_type is number_schema


def test_array_schema_of_invalid_schema_type():
    schema = ArraySchema()
    with pytest.raises(TypeError):
        schema.of("not a schema object")


def test_array_schema_validate_success_no_of():
    # If .of() is not called, it defaults to a generic nullable Schema, accepting any type
    schema = ArraySchema()
    assert schema.validate([1, "hello", True, None]) == [1, "hello", True, None]
    assert schema.validate((1, "hello", True, None)) == (1, "hello", True, None)


def test_array_schema_validate_success_with_of_string():
    schema = ArraySchema().of(StringSchema())
    assert schema.validate(["hello", "world"]) == ["hello", "world"]
    assert schema.validate(("foo", "bar")) == ("foo", "bar")  # Ensure tuple output for tuple input


def test_array_schema_validate_success_with_of_number():
    schema = ArraySchema().of(NumberSchema())
    assert schema.validate([1, 2, 3]) == [1, 2, 3]
    assert schema.validate((1.0, 2.5)) == (1.0, 2.5)  # Ensure tuple output for tuple input


def test_array_schema_validate_empty_list():
    schema = ArraySchema().of(StringSchema())
    assert schema.validate([]) == []
    assert schema.validate(()) == ()


def test_array_schema_validate_type_mismatch_top_level():
    schema = ArraySchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("not a list")
    assert excinfo.value.constraint.type == "type"
    assert excinfo.value.invalid_value == "not a list"
    assert excinfo.value.constraint.format_message == "Value is not of type (<class 'list'>, <class 'tuple'>), got <class 'str'>"


def test_array_schema_validate_failure_single_error_abort_early_true():
    schema = ArraySchema().of(StringSchema())
    data = ["valid", 123, "another_valid"]  # 123 is invalid
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(data, abort_early=True)
    assert excinfo.value.path == "~/[1]"  # Adjusted to '~.1' as per common path standard
    assert excinfo.value.invalid_value == 123
    assert excinfo.value.constraint.type == "type"
    assert excinfo.value.constraint.format_message == "Value is not of type <class 'str'>, got <class 'int'>"
    assert not excinfo.value._errors  # No nested errors when abort_early is True


def test_array_schema_validate_failure_multiple_errors_abort_early_false():
    schema = ArraySchema().of(StringSchema())
    data = ["valid", 123, True, "another_valid"]  # 123 and True are invalid
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(data, abort_early=False)

    assert excinfo.value.constraint.type == "array"
    assert excinfo.value.path == "~"
    assert len(list(excinfo.value.errors)) == 3  # Main error + 2 nested errors

    # Check specific nested errors
    error_list = list(excinfo.value.errors)
    # The first error is the main array error
    assert error_list[0].constraint.type == "array"
    assert error_list[0].path == "~"

    # The second error is for index 1
    assert error_list[1].path == "~/[1]"  # Adjusted to '~.1'
    assert error_list[1].invalid_value == 123
    assert error_list[1].constraint.type == "type"
    assert error_list[1].constraint.format_message == "Value is not of type <class 'str'>, got <class 'int'>"

    # The third error is for index 2
    assert error_list[2].path == "~/[2]"  # Adjusted to '~.2'
    assert error_list[2].invalid_value is True
    assert error_list[2].constraint.type == "type"
    assert error_list[2].constraint.format_message == "Value is not of type <class 'str'>, got <class 'bool'>"


def test_array_schema_validate_complex_nested_schema():
    # Test a schema for an array of numbers that must be positive
    number_schema_positive = NumberSchema().positive()
    array_of_positive_numbers_schema = ArraySchema().of(number_schema_positive)

    # Success case
    assert array_of_positive_numbers_schema.validate([1, 5, 100]) == [1, 5, 100]
    assert array_of_positive_numbers_schema.validate((1, 5, 100)) == (1, 5, 100)  # Test tuple input/output

    # Failure case with negative number, abort_early=True
    with pytest.raises(ValidationError) as excinfo:
        array_of_positive_numbers_schema.validate([1, -5, 100])
    assert excinfo.value.path == "~/[1]"  # Adjusted to '~.1'
    assert excinfo.value.invalid_value == -5
    assert excinfo.value.constraint.type == "gt"  # 'gt' for greater than 0 from .positive()

    # Failure case with mixed types and negative, abort_early=False
    with pytest.raises(ValidationError) as excinfo:
        array_of_positive_numbers_schema.validate([1, -5, "abc", 10], abort_early=False)
    assert excinfo.value.constraint.type == "array"
    assert len(list(excinfo.value.errors)) == 3  # Main error + 2 nested errors

    error_list = list(excinfo.value.errors)
    assert error_list[1].path == "~/[1]"  # Adjusted to '~.1' # Error for -5
    assert error_list[1].invalid_value == -5
    assert error_list[1].constraint.type == "gt"

    assert error_list[2].path == "~/[2]"  # Adjusted to '~.2' # Error for "abc" (type mismatch)
    assert error_list[2].invalid_value == "abc"
    assert error_list[2].constraint.type == "type"


# --- Tests for inherited SizedSchema methods in ArraySchema ---

def test_array_schema_inherited_length_success():
    schema = ArraySchema().length(3)
    assert schema.validate([1, 2, 3]) == [1, 2, 3]


def test_array_schema_inherited_length_failure():
    schema = ArraySchema().length(3)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate([1, 2])
    assert excinfo.value.constraint.type == "length"
    assert excinfo.value.invalid_value == [1, 2]
    assert excinfo.value.constraint.format_message == "Length must be 3"


def test_array_schema_inherited_min_success():
    schema = ArraySchema().min(2)
    assert schema.validate([1, 2]) == [1, 2]
    assert schema.validate([1, 2, 3]) == [1, 2, 3]


def test_array_schema_inherited_min_failure():
    schema = ArraySchema().min(2)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate([1])
    assert excinfo.value.constraint.type == "min"
    assert excinfo.value.invalid_value == [1]
    assert excinfo.value.constraint.format_message == "Min length must be 2"


def test_array_schema_inherited_max_success():
    schema = ArraySchema().max(3)
    assert schema.validate([1, 2]) == [1, 2]
    assert schema.validate([1, 2, 3]) == [1, 2, 3]


def test_array_schema_inherited_max_failure():
    schema = ArraySchema().max(3)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate([1, 2, 3, 4])
    assert excinfo.value.constraint.type == "max"
    assert excinfo.value.invalid_value == [1, 2, 3, 4]
    assert excinfo.value.constraint.format_message == "Max length must be 3"
