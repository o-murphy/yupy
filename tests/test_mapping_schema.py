# test_mapping_schema.py
from unittest.mock import patch, MagicMock

import pytest

from yupy.adapters import SchemaRequiredAdapter, _REQUIRED_UNDEFINED_
from yupy.locale import locale as yupy_actual_locale, get_error_message as yupy_actual_get_error_message
from yupy.mapping_schema import MappingSchema
from yupy.number_schema import NumberSchema
from yupy.string_schema import StringSchema
from yupy.validation_error import ValidationError


# Patch the locale module for tests that don't explicitly set messages
@pytest.fixture(autouse=True)
def mock_yupy_locale():
    mock_locale_data = yupy_actual_locale.copy()

    # Patch the yupy.locale module itself, and set its attributes
    with patch('yupy.locale',
               new=MagicMock(locale=mock_locale_data, get_error_message=yupy_actual_get_error_message)):
        yield


def test_mapping_schema_creation():
    schema = MappingSchema()
    assert schema._type is dict
    assert schema._fields == {}


def test_mapping_schema_shape_success():
    name_schema = StringSchema()
    age_schema = NumberSchema().integer()
    user_schema = MappingSchema().shape({
        "name": name_schema,
        "age": age_schema
    })
    assert user_schema._fields["name"] == name_schema
    assert user_schema._fields["age"] == age_schema


def test_mapping_schema_shape_invalid_input():
    schema = MappingSchema()
    with pytest.raises(TypeError):
        schema.shape("not a dict")


def test_mapping_schema_shape_invalid_field_type():
    schema = MappingSchema()
    with pytest.raises(TypeError):
        schema.shape({"name": "not a schema"})


# region Strict tests
def test_mapping_schema_strict_true_unknown_keys_fails():
    schema = MappingSchema().shape({"name": StringSchema()}).strict(True)  # Explicitly set strict to True
    with pytest.raises(ValidationError) as excinfo:
        schema.validate({"name": "Alice", "extra": 123})
    assert excinfo.value.constraint.type == "strict"
    assert excinfo.value.path == "~"  # Strictness is a check on the object itself
    assert excinfo.value.constraint.format_message == "Object contains unknown keys: ['extra']"


def test_mapping_schema_strict_false_unknown_keys_succeeds():
    schema = MappingSchema().shape({"name": StringSchema()}).strict(False)  # Explicitly set strict to False
    value = schema.validate({"name": "Alice", "extra": 123})
    assert value == {"name": "Alice", "extra": 123}


def test_mapping_schema_default_not_strict_unknown_keys_succeeds():
    schema = MappingSchema().shape({"name": StringSchema()})  # strict is False by default
    value = schema.validate({"name": "Alice", "extra": 123})
    assert value == {"name": "Alice", "extra": 123}


def test_mapping_schema_strict_true_no_unknown_keys_succeeds():
    schema = MappingSchema().shape({"name": StringSchema()}).strict(True)
    value = schema.validate({"name": "Alice"})
    assert value == {"name": "Alice"}


# endregion

# region Validation success tests
def test_mapping_schema_validate_empty_shape_empty_value_success():
    schema = MappingSchema().shape({})
    assert schema.validate({}) == {}


def test_mapping_schema_validate_simple_success():
    schema = MappingSchema().shape({
        "name": StringSchema(),
        "age": NumberSchema().integer()
    })
    data = {"name": "Bob", "age": 30}
    assert schema.validate(data) == data


def test_mapping_schema_validate_nested_success():
    address_schema = MappingSchema().shape({
        "street": StringSchema(),
        "zip": StringSchema().length(5)
    })
    user_schema = MappingSchema().shape({
        "name": StringSchema(),
        "address": address_schema
    })
    data = {"name": "Charlie", "address": {"street": "Main St", "zip": "12345"}}
    assert user_schema.validate(data) == data


def test_mapping_schema_validate_with_nullable_field_present():
    schema = MappingSchema().shape({
        "name": StringSchema(),
        "email": StringSchema().nullable()
    })
    data = {"name": "Diana", "email": "diana@example.com"}
    assert schema.validate(data) == data


def test_mapping_schema_validate_with_nullable_field_missing():
    schema = MappingSchema().shape({
        "name": StringSchema(),
        "email": StringSchema().nullable()
    })
    data = {"name": "Diana"}  # email is missing, but nullable, so should pass
    assert schema.validate(data) == data


def test_mapping_schema_validate_with_nullable_field_none():
    schema = MappingSchema().shape({
        "name": StringSchema(),
        "email": StringSchema().nullable()
    })
    data = {"name": "Eve", "email": None}
    assert schema.validate(data) == data


def test_mapping_schema_validate_none_input_with_nullable_schema():
    schema = MappingSchema().nullable()
    assert schema.validate(None) is None


# endregion

# region Validation failure (abort_early=True) tests
def test_mapping_schema_validate_missing_required_field_abort_early():
    schema = MappingSchema().shape({
        "name": StringSchema(),
        "age": SchemaRequiredAdapter(NumberSchema().integer())
    })  # age is required by default
    with pytest.raises(ValidationError) as excinfo:
        schema.validate({"name": "Frank"})
    assert excinfo.value.constraint.type == "required"
    assert excinfo.value.path == "~/age"
    assert excinfo.value.invalid_value is _REQUIRED_UNDEFINED_  # The invalid value for a missing required field is None
    assert excinfo.value.constraint.format_message == "Value is required"


def test_mapping_schema_validate_invalid_field_type_abort_early():
    schema = MappingSchema().shape({
        "name": StringSchema(),
        "age": NumberSchema().integer()
    })
    with pytest.raises(ValidationError) as excinfo:
        schema.validate({"name": "Grace", "age": "thirty"})
    assert excinfo.value.constraint.type == "type"
    assert excinfo.value.path == "~/age"
    assert excinfo.value.invalid_value == "thirty"  # The invalid value should be 'thirty', not the whole dict
    assert "Value is not of type " in excinfo.value.constraint.format_message  # Order of int, float might vary


def test_mapping_schema_validate_nested_error_abort_early():
    address_schema = MappingSchema().shape({
        "street": StringSchema(),
        "zip": StringSchema().length(5)
    })
    user_schema = MappingSchema().shape({
        "name": StringSchema(),
        "address": address_schema
    })
    # zip is too short
    data = {"name": "Heidi", "address": {"street": "Elm St", "zip": "123"}}
    with pytest.raises(ValidationError) as excinfo:
        user_schema.validate(data, abort_early=True)
    assert excinfo.value.constraint.type == "length"
    assert excinfo.value.path == "~/address/zip"  # Path should be the specific failing field
    assert excinfo.value.invalid_value == "123"
    assert "Length must be" in excinfo.value.constraint.format_message


# endregion

# region Validation failure (abort_early=False) tests
def test_mapping_schema_validate_multiple_errors_collect_all():
    schema = MappingSchema().shape({
        "name": StringSchema(),
        "age": SchemaRequiredAdapter(NumberSchema().integer()),
        "email": StringSchema(),
        "occupation": StringSchema().nullable()
    })
    data = {
        "name": 123,  # Type error
        # age is missing (required)
        "email": 456,  # Type error
        "occupation": None
    }
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(data, abort_early=False)

    all_errors = list(excinfo.value.errors)
    # Expect 3 errors: main object error, name error, age error, email error
    assert len(all_errors) == 4  # Main error + 3 field errors

    # Check the main error
    assert all_errors[0].path == "~"
    assert all_errors[0].constraint.type == "mapping"
    assert all_errors[0].constraint.format_message == "Invalid mapping"  # Consistent with locale

    # Check sub-errors (order might vary based on dictionary iteration, but content should be there)
    # Paths should be fully qualified in the collected errors
    error_paths = sorted([e.path for e in all_errors[1:]])
    assert error_paths == ["~/age", "~/email", "~/name"]  # Paths should be fully qualified

    name_error = next(e for e in all_errors if e.path == "~/name")
    assert name_error.constraint.type == "type"
    assert name_error.invalid_value == 123

    age_error = next(e for e in all_errors if e.path == "~/age")
    assert age_error.constraint.type == "required"
    assert age_error.invalid_value is _REQUIRED_UNDEFINED_

    email_error = next(e for e in all_errors if e.path == "~/email")
    assert email_error.constraint.type == "type"
    assert email_error.invalid_value == 456


def test_mapping_schema_validate_nested_and_multiple_errors_collect_all():
    address_schema = MappingSchema().shape({
        "street": StringSchema(),
        "city": SchemaRequiredAdapter(StringSchema()),
        "zip": StringSchema().length(5)
    })
    user_schema = MappingSchema().shape({
        "name": StringSchema(),
        "age": NumberSchema().integer(),
        "address": address_schema
    })
    data = {
        "name": "Ivan",
        "age": "twenty",  # Type error
        "address": {
            "street": 123,  # Type error
            # city is missing (required)
            "zip": "123"  # Length error
        }
    }

    with pytest.raises(ValidationError) as excinfo:
        user_schema.validate(data, abort_early=False)

    all_errors = list(excinfo.value.errors)
    # Expected errors:
    # 0: Main user object error (~)
    # 1: age error (~/age)
    # 2: address object error (~/address)
    # 3: street error (~/address/street)
    # 4: city error (~/address/city)
    # 5: zip error (~/address/zip)
    # assert len(all_errors) == 6

    # Check main error
    assert all_errors[0].path == "~"
    assert all_errors[0].constraint.type == "mapping"

    # Check age error
    age_error = next(e for e in all_errors if e.path == "~/age")  # Fully qualified path
    assert age_error.constraint.type == "type"
    assert age_error.invalid_value == "twenty"

    # Check address object error
    address_object_error = next(e for e in all_errors if e.path == "~/address")  # Fully qualified path
    assert address_object_error.constraint.type == "mapping"

    # Check nested errors within address (order by path for consistency)
    # Paths should be fully qualified in the collected errors
    nested_address_errors = sorted([e for e in all_errors if e.path.startswith("~/address")], key=lambda x: x.path)

    street_error = next(e for e in nested_address_errors if e.path == "~/address/street")
    assert street_error.constraint.type == "type"
    assert street_error.invalid_value == 123

    city_error = next(e for e in nested_address_errors if e.path == "~/address/city")
    assert city_error.constraint.type == "required"
    assert city_error.invalid_value is _REQUIRED_UNDEFINED_

    zip_error = next(e for e in nested_address_errors if e.path == "~/address/zip")
    assert zip_error.constraint.type == "length"
    assert zip_error.invalid_value == "123"


# endregion

# region __getitem__ tests
def test_mapping_schema_getitem():
    name_schema = StringSchema()
    age_schema = NumberSchema()
    user_schema = MappingSchema().shape({
        "name": name_schema,
        "age": age_schema
    })
    assert user_schema["name"] == name_schema
    assert user_schema["age"] == age_schema


def test_mapping_schema_getitem_key_not_found():
    schema = MappingSchema().shape({"name": StringSchema()})
    with pytest.raises(KeyError):
        _ = schema["non_existent_key"]
# endregion
