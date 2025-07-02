# test_union_schema.py
from unittest.mock import patch, MagicMock

import pytest

from yupy.array_schema import ArraySchema
from yupy.locale import locale as yupy_actual_locale, get_error_message as yupy_actual_get_error_message
from yupy.number_schema import NumberSchema
from yupy.schema import Schema
from yupy.string_schema import StringSchema
from yupy.union_schema import UnionSchema
from yupy.validation_error import ValidationError


@pytest.fixture(autouse=True)
def mock_yupy_locale():
    # Create a mock for the 'locale' dictionary itself
    mock_locale_data = {
        # Copy actual lambdas/strings from yupy.locale.locale where appropriate
        "type": yupy_actual_locale["type"],
        "not_nullable": yupy_actual_locale["not_nullable"],
        "undefined": yupy_actual_locale["undefined"],
        "min": yupy_actual_locale["min"],
        "max": yupy_actual_locale["max"],
        "length": yupy_actual_locale["length"],
        "gt": yupy_actual_locale["gt"],
        "ge": yupy_actual_locale["ge"],
        "array_of": yupy_actual_locale["array_of"],
        "array": yupy_actual_locale["array"],
        "one_of": yupy_actual_locale["one_of"],
        "nullable": yupy_actual_locale["nullable"],
    }
    # Patch the yupy.locale module itself, and set its attributes
    with patch('yupy.locale', new=MagicMock(locale=mock_locale_data, get_error_message=yupy_actual_get_error_message)):
        yield


def test_union_schema_creation():
    schema = UnionSchema()
    assert schema._type == object
    assert schema._options == []


def test_union_schema_one_of_success():
    s1 = StringSchema()
    s2 = NumberSchema()
    schema = UnionSchema().one_of([s1, s2])
    assert schema._options == [s1, s2]


def test_union_schema_one_of_invalid_schema_type():
    with pytest.raises(ValidationError) as excinfo:
        UnionSchema().one_of([StringSchema(), "invalid"])
    assert excinfo.value.constraint.type == "one_of"
    assert excinfo.value.invalid_value == "invalid"
    assert "Must be one of " in excinfo.value.constraint.format_message


def test_union_schema_validate_with_string_success():
    schema = UnionSchema().one_of([StringSchema(), NumberSchema()])
    assert schema.validate("hello") == "hello"


def test_union_schema_validate_with_number_success():
    schema = UnionSchema().one_of([StringSchema(), NumberSchema()])
    assert schema.validate(123) == 123


def test_union_schema_validate_with_multiple_matching_schemas_success():
    # Both StringSchema and Schema would match an empty string
    schema = UnionSchema().one_of([StringSchema(), Schema()])
    assert schema.validate("") == ""


def test_union_schema_validate_nullable_success():
    schema = UnionSchema().one_of([StringSchema(), NumberSchema()]).nullable()
    assert schema.validate(None) is None


def test_union_schema_validate_not_nullable_failure():
    schema = UnionSchema().one_of([StringSchema()]).not_nullable()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(None)
    assert excinfo.value.constraint.type == "nullable"
    assert excinfo.value.invalid_value is None
    assert excinfo.value.constraint.format_message == "Value can't be null"


def test_union_schema_one_of_empty_list():
    schema = UnionSchema().one_of([])
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("any_value")
    assert excinfo.value.constraint.type == "one_of"
    assert "Must be one of " in excinfo.value.constraint.format_message
