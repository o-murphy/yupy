# File: test_number_schema.py
import pytest

from yupy.icomparable_schema import ComparableSchema, EqualityComparableSchema
from yupy.locale import locale
from yupy.number_schema import NumberSchema
from yupy.schema import Schema
from yupy.validation_error import ValidationError


# Fixture to ensure isolation of tests that might modify the global 'locale'
@pytest.fixture(autouse=True)
def reset_locale_for_number_schema_tests():
    original_locale = locale.copy()
    yield
    locale.clear()
    locale.update(original_locale)


def test_number_schema_inheritance():
    """Test that NumberSchema inherits correctly."""
    schema = NumberSchema()
    assert isinstance(schema, ComparableSchema)
    assert isinstance(schema, EqualityComparableSchema)
    assert isinstance(schema, Schema)
    assert schema._type == (float, int)


def test_number_schema_default_type_check_success():
    """Test that NumberSchema correctly validates default numeric types."""
    schema = NumberSchema()
    assert schema.validate(10) == 10
    assert schema.validate(10.5) == 10.5


def test_number_schema_default_type_check_failure():
    """Test that NumberSchema correctly fails for non-numeric types."""
    schema = NumberSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate("abc")
    assert excinfo.value.constraint.type == "type"
    assert excinfo.value.invalid_value == "abc"
    expected_message = locale["type"](((float, int), type("abc")))
    assert excinfo.value.constraint.format_message == expected_message


def test_positive_success():
    """Test positive() method for successful validation."""
    schema = NumberSchema().positive()
    assert schema.validate(1) == 1
    assert schema.validate(0.001) == 0.001
    assert schema.validate(100) == 100


def test_positive_failure():
    """Test positive() method for failed validation."""
    schema = NumberSchema().positive()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(0)
    assert excinfo.value.constraint.type == "gt"
    assert excinfo.value.path == "~"
    assert excinfo.value.invalid_value == 0
    # Corrected expectation: positive() uses its own locale message
    expected_message = locale["positive"]
    assert excinfo.value.constraint.format_message == expected_message

    with pytest.raises(ValidationError) as excinfo:
        schema.validate(-5)
    assert excinfo.value.constraint.type == "gt"
    assert excinfo.value.invalid_value == -5
    # Corrected expectation for negative value as well
    assert excinfo.value.constraint.format_message == expected_message


def test_positive_with_custom_message():
    """Test positive() method with a custom error message."""
    custom_message = "Value must be strictly greater than zero!"
    schema = NumberSchema().positive(message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(-10)
    assert excinfo.value.constraint.message == custom_message


def test_negative_success():
    """Test negative() method for successful validation."""
    schema = NumberSchema().negative()
    assert schema.validate(-1) == -1
    assert schema.validate(-0.001) == -0.001
    assert schema.validate(-100) == -100


def test_negative_failure():
    """Test negative() method for failed validation."""
    schema = NumberSchema().negative()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(0)
    assert excinfo.value.constraint.type == "lt"
    assert excinfo.value.invalid_value == 0
    expected_message = locale["negative"]
    assert excinfo.value.constraint.format_message == expected_message

    with pytest.raises(ValidationError) as excinfo:
        schema.validate(5)
    assert excinfo.value.constraint.type == "lt"
    assert excinfo.value.invalid_value == 5
    assert excinfo.value.constraint.format_message == expected_message


def test_negative_with_custom_message():
    """Test negative() method with a custom error message."""
    custom_message = "Value must be strictly less than zero!"
    schema = NumberSchema().negative(message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(10)
    assert excinfo.value.constraint.message == custom_message


def test_integer_success():
    """Test integer() method for successful validation."""
    schema = NumberSchema().integer()
    assert schema.validate(5) == 5
    assert schema.validate(0) == 0
    assert schema.validate(-10) == -10


def test_integer_failure():
    """Test integer() method for failed validation."""
    schema = NumberSchema().integer()
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(5.5)
    assert excinfo.value.constraint.type == "integer"
    assert excinfo.value.path == "~"
    assert excinfo.value.invalid_value == 5.5
    expected_message = locale["integer"]
    assert excinfo.value.constraint.format_message == expected_message

    with pytest.raises(ValidationError) as excinfo:
        schema.validate(-1.23)
    assert excinfo.value.constraint.type == "integer"
    assert excinfo.value.invalid_value == -1.23
    assert excinfo.value.constraint.format_message == expected_message


def test_integer_with_custom_message():
    """Test integer() method with a custom error message."""
    custom_message = "Number must be a whole number!"
    schema = NumberSchema().integer(message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(99.9)
    assert excinfo.value.constraint.message == custom_message


def test_multiple_of_success():
    """Test multiple_of() method for successful validation."""
    schema = NumberSchema().multiple_of(5)
    assert schema.validate(10) == 10
    assert schema.validate(0) == 0
    assert schema.validate(-15) == -15

    schema_float_multiplier = NumberSchema().multiple_of(0.5)
    assert schema_float_multiplier.validate(2.0) == 2.0
    assert schema_float_multiplier.validate(2.5) == 2.5


def test_multiple_of_failure():
    """Test multiple_of() method for failed validation."""
    schema = NumberSchema().multiple_of(3)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(7)
    assert excinfo.value.constraint.type == "multiple_of"
    assert excinfo.value.path == "~"
    assert excinfo.value.invalid_value == 7
    expected_message = locale["multiple_of"]((3,))
    assert excinfo.value.constraint.format_message == expected_message

    with pytest.raises(ValidationError) as excinfo:
        schema.validate(10)
    assert excinfo.value.constraint.type == "multiple_of"
    assert excinfo.value.invalid_value == 10
    assert excinfo.value.constraint.format_message == expected_message

    schema_float_multiplier = NumberSchema().multiple_of(0.3)
    with pytest.raises(ValidationError) as excinfo:
        schema_float_multiplier.validate(1.0)  # 1.0 is not a multiple of 0.3
    assert excinfo.value.constraint.type == "multiple_of"
    assert excinfo.value.invalid_value == 1.0
    expected_message_float = locale["multiple_of"]((0.3,))
    assert excinfo.value.constraint.format_message == expected_message_float


def test_multiple_of_with_custom_message():
    """Test multiple_of() method with a custom error message."""
    custom_message = "Value is not a multiple of 7!"
    schema = NumberSchema().multiple_of(7, message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(10)
    assert excinfo.value.constraint.message == custom_message


def test_number_schema_nullable_behavior():
    """Test nullable behavior with NumberSchema methods."""
    # Test positive() with nullable and None
    schema_positive_nullable = NumberSchema().nullable().positive()
    assert schema_positive_nullable.validate(None) is None
    assert schema_positive_nullable.validate(10) == 10
    with pytest.raises(ValidationError):
        schema_positive_nullable.validate(-5)

    # Test integer() with nullable and None
    schema_integer_nullable = NumberSchema().nullable().integer()
    assert schema_integer_nullable.validate(None) is None
    assert schema_integer_nullable.validate(5) == 5
    with pytest.raises(ValidationError):
        schema_integer_nullable.validate(5.5)

    # Test multiple_of() with nullable and None
    schema_multiple_of_nullable = NumberSchema().nullable().multiple_of(2)
    assert schema_multiple_of_nullable.validate(None) is None
    assert schema_multiple_of_nullable.validate(4) == 4
    with pytest.raises(ValidationError):
        schema_multiple_of_nullable.validate(3)

    # Test non-nullable behavior (default)
    schema_positive_not_nullable = NumberSchema().positive()
    with pytest.raises(ValidationError) as excinfo:
        schema_positive_not_nullable.validate(None)
    assert excinfo.value.constraint.type == "nullable"

    schema_integer_not_nullable = NumberSchema().integer()
    with pytest.raises(ValidationError) as excinfo:
        schema_integer_not_nullable.validate(None)
    assert excinfo.value.constraint.type == "nullable"


# region Rounding and Truncation tests
def test_truncate_success():
    """Test truncate() method for successful transformation."""
    schema = NumberSchema().truncate()
    assert schema.validate(5.7) == 5
    assert schema.validate(-5.7) == -5
    assert schema.validate(5) == 5
    assert schema.validate(-5) == -5
    assert schema.validate(0.999) == 0
    assert schema.validate(-0.999) == 0


def test_round_default_success():
    """Test round() method with default 'round' behavior."""
    schema = NumberSchema().round()
    assert schema.validate(5.7) == 6
    assert schema.validate(5.3) == 5
    assert schema.validate(-5.7) == -6
    assert schema.validate(-5.3) == -5
    assert schema.validate(2.5) == 2  # Standard round ties to nearest even
    assert schema.validate(3.5) == 4  # Standard round ties to nearest even


def test_round_ceil_success():
    """Test round() method with 'ceil' behavior."""
    schema = NumberSchema().round(method='ceil')
    assert schema.validate(5.1) == 6
    assert schema.validate(5.0) == 5
    assert schema.validate(-5.1) == -5  # ceil(-5.1) is -5
    assert schema.validate(-5.0) == -5


def test_round_floor_success():
    """Test round() method with 'floor' behavior."""
    schema = NumberSchema().round(method='floor')
    assert schema.validate(5.9) == 5
    assert schema.validate(5.0) == 5
    assert schema.validate(-5.9) == -6  # floor(-5.9) is -6
    assert schema.validate(-5.0) == -5


def test_round_trunc_success():
    """Test round() method with 'trunc' behavior."""
    schema = NumberSchema().round(method='trunc')
    assert schema.validate(5.7) == 5
    assert schema.validate(-5.7) == -5
    assert schema.validate(5.0) == 5
    assert schema.validate(-5.0) == -5
    assert schema.validate(0.999) == 0
    assert schema.validate(-0.999) == 0


def test_round_invalid_method_failure():
    """Test round() method with an invalid method string."""
    schema = NumberSchema()
    with pytest.raises(ValueError):
        schema.round(method='invalid_method')


def test_round_and_validate_chaining():
    """Test chaining round() with other validation methods."""
    schema = NumberSchema().round('ceil').positive().integer()
    assert schema.validate(5.1) == 6  # ceil(5.1) -> 6, positive, integer
    assert schema.validate(0.1) == 1  # ceil(0.1) -> 1, positive, integer

    # This test case is expected to raise a ValidationError
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(-0.1)  # ceil(-0.1) -> 0, fails positive()
    assert excinfo.value.constraint.type == "gt"
    assert excinfo.value.invalid_value == -0.1  # The invalid_value should be the original input to validate()

    # Test an actual failure case for chaining:
    schema_chained_negative_fail = NumberSchema().round('floor').positive()
    with pytest.raises(ValidationError) as excinfo:
        schema_chained_negative_fail.validate(-0.9)  # floor(-0.9) is -1, fails positive()
    assert excinfo.value.constraint.type == "gt"
    assert excinfo.value.invalid_value == -0.9  # The invalid_value should be the original input to validate()


def test_truncate_and_validate_chaining():
    """Test chaining truncate() with other validation methods."""
    schema = NumberSchema().truncate().positive().integer()
    assert schema.validate(5.7) == 5  # trunc(5.7) -> 5, positive, integer

    # This test case is expected to raise a ValidationError
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(0.1)  # trunc(0.1) -> 0, fails positive()
    assert excinfo.value.constraint.type == "gt"
    assert excinfo.value.invalid_value == 0.1  # The invalid_value should be the original input to validate()

    # This test case is expected to raise a ValidationError
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(-5.7)  # trunc(-5.7) -> -5, fails positive()
    assert excinfo.value.constraint.type == "gt"
    assert excinfo.value.invalid_value == -5.7  # The invalid_value should be the original input to validate()

# endregion
