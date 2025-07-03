from typing import List, Any
from unittest.mock import patch

from yupy.validation_error import ValidationError, Constraint, _EMPTY_MESSAGE_


def test_constraint_init_with_type_and_message():
    constraint = Constraint("test_type", "Test message")
    assert constraint.type == "test_type"
    assert constraint.args == ()
    assert constraint.message == "Test message"


def test_constraint_init_with_type_and_no_message():
    # Patch get_error_message where it is used by the Constraint class,
    # i.e., within the yupy.validation_error module's namespace, as it's imported at the top.
    with patch('yupy.validation_error.get_error_message',
               return_value="Default error message") as mock_get_error_message:
        constraint = Constraint("test_type")
        assert constraint.type == "test_type"
        assert constraint.args == ()
        assert constraint.message == "Default error message"
        # Assert that the mocked get_error_message was called
        mock_get_error_message.assert_called_once_with("undefined")


def test_constraint_init_with_args():
    constraint = Constraint("range", "Out of range", 10, 20)
    assert constraint.type == "range"
    assert constraint.args == (10, 20)
    assert constraint.message == "Out of range"


def test_constraint_format_message_callable():
    def custom_message_formatter(args: List[Any]) -> str:
        return f"Value {args[0]} is not equal to {args[1]}"

    constraint = Constraint("equality", custom_message_formatter, 5, 10)
    assert constraint.format_message == "Value 5 is not equal to 10"


def test_constraint_format_message_string():
    constraint = Constraint("min_length", "Too short")
    assert constraint.format_message == "Too short"


def test_validation_error_init_no_args():
    error = ValidationError()
    assert error.constraint.type == "undefined"
    assert error.path == ""
    assert error._errors == []
    assert error.invalid_value is None


def test_validation_error_init_with_constraint_and_path():
    constraint = Constraint("min_value", "Value too small", 10)
    error = ValidationError(constraint=constraint, path="data.age", invalid_value=5)
    assert error.constraint == constraint
    assert error.path == "data.age"
    assert error.invalid_value == 5


def test_validation_error_init_with_nested_errors():
    nested_constraint1 = Constraint("required", "Field is required")
    nested_error1 = ValidationError(constraint=nested_constraint1, path="data.name")

    nested_constraint2 = Constraint("type", "Invalid type")
    nested_error2 = ValidationError(constraint=nested_constraint2, path="data.value")

    main_constraint = Constraint("composite", "Multiple issues")
    main_error = ValidationError(constraint=main_constraint, path="data", errors=[nested_error1, nested_error2])

    assert main_error._errors == [nested_error1, nested_error2]
    assert main_error.path == "data"


def test_validation_error_str_representation():
    constraint = Constraint("invalid_format", "Incorrect format")
    error = ValidationError(constraint=constraint, path="user.email")
    assert str(
        error) == ("(path='user.email', "
                   "constraint=Constraint(type='invalid_format', args=(), origin=None), "
                   "message='Incorrect format')")


def test_validation_error_repr_representation():
    constraint = Constraint("null_value", "Cannot be null")
    error = ValidationError(constraint=constraint, path="item.id")
    print(repr(error))
    assert repr(
        error) == ("ValidationError(path='item.id', "
                   "constraint=Constraint(type='null_value', args=(), origin=None), "
                   "message='Cannot be null')")


def test_validation_error_errors_property_single_error():
    constraint = Constraint("min", "Too small")
    error = ValidationError(constraint=constraint, path="age")
    errors_list = list(error.errors)
    assert len(errors_list) == 1
    assert errors_list[0] == error


def test_validation_error_errors_property_nested_errors():
    c1 = Constraint("c1", "m1")
    e1 = ValidationError(c1, "p1")
    c2 = Constraint("c2", "m2")
    e2 = ValidationError(c2, "p2")
    c3 = Constraint("c3", "m3")
    e3 = ValidationError(c3, "p3", errors=[e1, e2])
    c4 = Constraint("c4", "m4")
    e4 = ValidationError(c4, "p4")
    main_error = ValidationError(Constraint("main", "main"), "main_path", errors=[e3, e4])

    all_errors = list(main_error.errors)
    assert len(all_errors) == 5
    assert all_errors[0] == main_error
    assert all_errors[1] == e3
    assert all_errors[2] == e1
    assert all_errors[3] == e2
    assert all_errors[4] == e4


def test_validation_error_message_property():
    constraint = Constraint("max_length", "Too long")
    error = ValidationError(constraint=constraint, path="description")
    assert error.message == "'description':Too long"


def test_validation_error_messages_property():
    c1 = Constraint("c1", "m1")
    e1 = ValidationError(c1, "p1")
    c2 = Constraint("c2", "m2")
    e2 = ValidationError(c2, "p2")
    c3 = Constraint("c3", "m3")
    e3 = ValidationError(c3, "p3", errors=[e1, e2])

    messages = list(e3.messages)
    assert len(messages) == 3
    assert messages[0] == "'p3':m3"
    assert messages[1] == "'p1':m1"
    assert messages[2] == "'p2':m2"


def test_empty_message_constant():
    assert _EMPTY_MESSAGE_ == ""
