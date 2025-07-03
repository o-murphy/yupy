import pytest

from yupy.icomparable_schema import EqualityComparableSchema, ComparableSchema, IEqualityComparableSchema, \
    IComparableSchema
from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ValidationError


# Fixture to ensure isolation of tests that might modify the global 'locale'
@pytest.fixture(autouse=True)
def reset_locale_for_comparable_schema_tests():
    original_locale = locale.copy()
    yield
    locale.clear()
    locale.update(original_locale)


def test_equality_comparable_schema_inheritance():
    """Test that EqualityComparableSchema inherits from Schema."""
    schema = EqualityComparableSchema()
    assert isinstance(schema, Schema)


def test_eq_success():
    """Test eq() method for successful validation."""
    schema = EqualityComparableSchema(_type=int).eq(10)
    result = schema.validate(10)
    assert result == 10

    schema_str = EqualityComparableSchema(_type=str).eq("hello")
    result_str = schema_str.validate("hello")
    assert result_str == "hello"


def test_eq_failure():
    """Test eq() method for failed validation."""
    schema = EqualityComparableSchema(_type=int).eq(10)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(5)

    error = excinfo.value
    assert error.constraint.type == "eq"
    assert error.path == "~"  # Default path from Schema.validate
    assert error.invalid_value == 5
    expected_message = locale["eq"]((10,))  # Expected value passed as args
    assert error.constraint.format_message == expected_message


def test_eq_failure_with_custom_message():
    """Test eq() method for failed validation with a custom message."""
    custom_message = "Value must be exactly 10!"
    schema = EqualityComparableSchema(_type=int).eq(10, message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(15)

    error = excinfo.value
    assert error.constraint.type == "eq"
    assert error.constraint.message == custom_message
    assert error.invalid_value == 15


def test_ne_success():
    """Test ne() method for successful validation."""
    schema = EqualityComparableSchema(_type=int).ne(10)
    result = schema.validate(5)
    assert result == 5


def test_ne_failure():
    """Test ne() method for failed validation."""
    schema = EqualityComparableSchema(_type=int).ne(10)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(10)

    error = excinfo.value
    assert error.constraint.type == "ne"
    assert error.path == "~"
    assert error.invalid_value == 10
    expected_message = locale["ne"]((10,))  # Value to not be equal to
    assert error.constraint.format_message == expected_message


def test_ne_failure_with_custom_message():
    """Test ne() method for failed validation with a custom message."""
    custom_message = "Value must not be 10!"
    schema = EqualityComparableSchema(_type=int).ne(10, message=custom_message)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(10)

    error = excinfo.value
    assert error.constraint.type == "ne"
    assert error.constraint.message == custom_message
    assert error.invalid_value == 10


def test_comparable_schema_inheritance():
    """Test that ComparableSchema inherits from Schema."""
    schema = ComparableSchema()
    assert isinstance(schema, Schema)


def test_le_success():
    """Test le() method for successful validation (less than or equal)."""
    schema = ComparableSchema(_type=int).le(10)
    result_less = schema.validate(5)
    assert result_less == 5
    result_equal = schema.validate(10)
    assert result_equal == 10


def test_le_failure():
    """Test le() method for failed validation (greater than limit)."""
    schema = ComparableSchema(_type=int).le(10)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(15)

    error = excinfo.value
    assert error.constraint.type == "le"
    assert error.path == "~"
    assert error.invalid_value == 15
    expected_message = locale["le"]((10,))  # Limit
    assert error.constraint.format_message == expected_message


def test_ge_success():
    """Test ge() method for successful validation (greater than or equal)."""
    schema = ComparableSchema(_type=int).ge(10)
    result_greater = schema.validate(15)
    assert result_greater == 15
    result_equal = schema.validate(10)
    assert result_equal == 10


def test_ge_failure():
    """Test ge() method for failed validation (less than limit)."""
    schema = ComparableSchema(_type=int).ge(10)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(5)

    error = excinfo.value
    assert error.constraint.type == "ge"
    assert error.path == "~"
    assert error.invalid_value == 5
    expected_message = locale["ge"]((10,))  # Limit
    assert error.constraint.format_message == expected_message


def test_lt_success():
    """Test lt() method for successful validation (strictly less than)."""
    schema = ComparableSchema(_type=int).lt(10)
    result = schema.validate(5)
    assert result == 5


def test_lt_failure():
    """Test lt() method for failed validation (greater than or equal to limit)."""
    schema = ComparableSchema(_type=int).lt(10)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(10)  # Equal to limit

    error = excinfo.value
    assert error.constraint.type == "lt"
    assert error.path == "~"
    assert error.invalid_value == 10
    expected_message = locale["lt"]((10,))  # Limit
    assert error.constraint.format_message == expected_message

    with pytest.raises(ValidationError) as excinfo:
        schema.validate(15)  # Greater than limit

    error = excinfo.value
    assert error.constraint.type == "lt"
    assert error.path == "~"
    assert error.invalid_value == 15


def test_gt_success():
    """Test gt() method for successful validation (strictly greater than)."""
    schema = ComparableSchema(_type=int).gt(10)
    result = schema.validate(15)
    assert result == 15


def test_gt_failure():
    """Test gt() method for failed validation (less than or equal to limit)."""
    schema = ComparableSchema(_type=int).gt(10)
    with pytest.raises(ValidationError) as excinfo:
        schema.validate(10)  # Equal to limit

    error = excinfo.value
    assert error.constraint.type == "gt"
    assert error.path == "~"
    assert error.invalid_value == 10
    expected_message = locale["gt"]((10,))  # Limit
    assert error.constraint.format_message == expected_message

    with pytest.raises(ValidationError) as excinfo:
        schema.validate(5)  # Less than limit

    error = excinfo.value
    assert error.constraint.type == "gt"
    assert error.path == "~"
    assert error.invalid_value == 5


def test_multiple_comparable_constraints():
    """Test a schema with multiple comparable constraints."""
    schema = ComparableSchema(_type=int).ge(5).le(15).lt(12).gt(7)  # Value must be > 7, <= 11
    result = schema.validate(8)
    assert result == 8
    result = schema.validate(11)
    assert result == 11

    with pytest.raises(ValidationError):
        schema.validate(7)  # Too small for gt(7)

    with pytest.raises(ValidationError):
        schema.validate(12)  # Too large for lt(12)


def test_icomparable_schema_protocol_conformance():
    """Test if EqualityComparableSchema conforms to IEqualityComparableSchema and ComparableSchema to IComparableSchema."""
    assert isinstance(EqualityComparableSchema(), IEqualityComparableSchema)
    assert isinstance(ComparableSchema(), IComparableSchema)

    class CustomEqualitySchema(EqualityComparableSchema):
        pass

    assert isinstance(CustomEqualitySchema(), IEqualityComparableSchema)

    class CustomComparableSchema(ComparableSchema):
        pass

    assert isinstance(CustomComparableSchema(), IComparableSchema)

    # Test classes that don't conform
    class NotComparableSchema(Schema):
        pass

    assert not isinstance(NotComparableSchema(), IEqualityComparableSchema)
    assert not isinstance(NotComparableSchema(), IComparableSchema)
