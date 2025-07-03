from typing import Any  # Import Any here

import pytest

from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ValidationError, Constraint


# Fixture to ensure isolation of tests that might modify the global 'locale'
# Although Schema doesn't modify it, other tests (like locale tests) might.
@pytest.fixture(autouse=True)
def reset_locale_for_schema_tests():
    original_locale = locale.copy()
    yield
    locale.clear()
    locale.update(original_locale)


def test_schema_initialization_default():
    """Test Schema initialization with default values."""
    schema = Schema()
    assert schema._type is object
    assert schema._transforms == []
    assert schema._validators == []
    assert schema._nullability is False
    assert schema._not_nullable == locale["not_nullable"]


def test_schema_initialization_with_type():
    """Test Schema initialization with a specified type."""
    schema = Schema(_type=str)
    assert schema._type is str


def test_nullable_property_and_method():
    """Test nullability property and nullable() method."""
    schema = Schema()
    assert schema.nullability is False

    schema.nullable()
    assert schema.nullability is True
    assert schema._nullability is True


def test_not_nullable_method():
    """Test not_nullable() method and custom message."""
    schema = Schema().nullable()  # Start as nullable
    assert schema.nullability is True

    schema.not_nullable()
    assert schema.nullability is False
    assert schema._nullability is False
    assert schema._not_nullable == locale["not_nullable"]

    custom_message = "Custom nullability error!"
    schema.not_nullable(message=custom_message)
    assert schema._not_nullable == custom_message


def test_nullable_check_value_not_none_not_nullable():
    """Test _nullable_check when value is not None and schema is not nullable."""
    schema = Schema()  # Default not nullable
    try:
        schema._nullable_check("some_value")
    except ValidationError:
        pytest.fail("_nullable_check raised ValidationError unexpectedly")


def test_nullable_check_value_none_nullable():
    """Test _nullable_check when value is None and schema is nullable."""
    schema = Schema().nullable()
    try:
        schema._nullable_check(None)
    except ValidationError:
        pytest.fail("_nullable_check raised ValidationError unexpectedly")


def test_nullable_check_value_none_not_nullable_raises_error():
    """Test _nullable_check raises ValidationError when value is None and schema is not nullable."""
    schema = Schema()  # Default not nullable
    with pytest.raises(ValidationError) as excinfo:
        schema._nullable_check(None)

    error = excinfo.value
    assert error.constraint.type == "nullable"
    assert error.constraint.message == locale["not_nullable"]
    assert error.path == ""  # Path is not set by _nullable_check itself
    assert error.invalid_value is None


def test_type_check_any_type():
    """Test _type_check with Any type, should not raise."""
    schema = Schema(_type=Any)
    try:
        schema._type_check(123)
        schema._type_check("abc")
        schema._type_check(None)
    except ValidationError:
        pytest.fail("_type_check raised ValidationError unexpectedly for Any type")


def test_type_check_matching_type():
    """Test _type_check with a matching type."""
    schema = Schema(_type=int)
    try:
        schema._type_check(123)
    except ValidationError:
        pytest.fail("_type_check raised ValidationError unexpectedly for matching type")


def test_type_check_non_matching_type_raises_error():
    """Test _type_check raises ValidationError for non-matching type."""
    schema = Schema(_type=str)
    with pytest.raises(ValidationError) as excinfo:
        schema._type_check(123)

    error = excinfo.value
    assert error.constraint.type == "type"
    # The message is a callable in locale, so we get the result of the callable
    expected_message = locale["type"]((str, int))  # Simulate the args that would be passed
    assert error.constraint.format_message == expected_message
    assert error.path == ""
    assert error.invalid_value == 123


def test_transform_method_adds_transform_func():
    """Test transform() method adds a function to _transforms."""
    schema = Schema()
    assert len(schema._transforms) == 0

    def upper_transform(value):
        return value.upper()

    schema.transform(upper_transform)
    assert len(schema._transforms) == 1
    assert schema._transforms[0] == upper_transform


def test_transform_method_applies_single_transform():
    """Test _transform method applies a single transformation."""
    schema = Schema(_type=str)
    schema.transform(lambda x: x + " World")
    transformed_value = schema._transform("Hello")
    assert transformed_value == "Hello World"


def test_transform_method_applies_multiple_transforms_in_order():
    """Test _transform method applies multiple transformations in order."""
    schema = Schema(_type=str)
    schema.transform(lambda x: x.upper())
    schema.transform(lambda x: x + "!!!")
    transformed_value = schema._transform("hello")
    assert transformed_value == "HELLO!!!"


def test_test_method_adds_validator_func():
    """Test test() method adds a function to _validators."""
    schema = Schema()
    assert len(schema._validators) == 0

    def is_positive(value):
        if value <= 0:
            raise ValueError("Value must be positive")

    schema.test(is_positive)
    assert len(schema._validators) == 1
    assert schema._validators[0] == is_positive


def test_validate_success_no_transforms_no_validators():
    """Test validate() success with no transforms or validators."""
    schema = Schema(_type=int)
    result = schema.validate(123)
    assert result == 123


def test_validate_success_with_transforms_and_validators():
    """Test validate() success with transforms and validators."""
    schema = Schema(_type=str) \
        .transform(lambda x: x.strip()) \
        .test(lambda x: x if len(x) > 5 else pytest.fail("Length too short"))

    result = schema.validate("  long_string  ")
    assert result == "long_string"


def test_validate_nullable_check_failure():
    """Test validate() fails due to nullability check."""
    schema = Schema(_type=int)  # Not nullable by default
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(None, path="field.subfield")

    error = excinfo.value
    assert error.constraint.type == "nullable"
    assert error.path == "field.subfield"
    assert error.invalid_value is None


def test_validate_type_check_failure():
    """Test validate() fails due to type check."""
    schema = Schema(_type=str)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(123, path="user.name")

    error = excinfo.value
    assert error.constraint.type == "type"
    assert error.path == "user.name"
    assert error.invalid_value == 123


def test_validate_custom_validator_failure():
    """Test validate() fails due to a custom validator."""

    def always_fail_validator(value):
        raise ValidationError(Constraint("custom_fail", "This value is always invalid"))

    schema = Schema(_type=int).test(always_fail_validator)

    with pytest.raises(ValidationError) as excinfo:
        schema.validate(10, path="item.id")

    error = excinfo.value
    assert error.constraint.type == "custom_fail"
    assert error.constraint.message == "This value is always invalid"
    assert error.path == "item.id"
    assert error.invalid_value == 10


def test_validate_path_propagation():
    """Test that the path is correctly propagated to ValidationError."""
    schema = Schema(_type=int)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("not_an_int", path="root.data.value")

    assert excinfo.value.path == "root.data.value"


def test_validate_const_success():
    """Test const() method for successful validation."""
    schema = Schema(_type=int).const(10)
    result = schema.validate(10)
    assert result == 10


def test_validate_const_failure():
    """Test const() method for failed validation."""
    schema = Schema(_type=int).const(10)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(5)

    error = excinfo.value
    assert error.constraint.type == "const"
    # The default path for validate() is "~"
    assert error.path == "~"
    assert error.invalid_value == 5
    # The locale's 'const' message is a callable, so we simulate its call
    expected_message = locale["const"]((10,))  # Value expected to be 10
    assert error.constraint.format_message == expected_message


def test_validate_const_failure_with_custom_message():
    """Test const() method for failed validation with a custom message."""
    custom_const_message = "Value must be exactly ten!"
    schema = Schema(_type=int).const(10, message=custom_const_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(5)

    error = excinfo.value
    assert error.constraint.type == "const"
    assert error.constraint.message == custom_const_message
    assert error.invalid_value == 5
