from typing import Any, Tuple

import pytest

from yupy.locale import locale, set_locale, get_error_message, ErrorMessage


# Helper to reset locale after tests to avoid side effects
@pytest.fixture(autouse=True)
def reset_locale():
    original_locale = locale.copy()
    yield
    locale.clear()
    locale.update(original_locale)


def test_initial_locale_content():
    """Test that the initial locale dictionary contains expected keys and values."""
    assert "undefined" in locale
    assert locale["undefined"] == "Undefined validation error"
    assert "const" in locale
    assert callable(locale["const"])
    assert "required" in locale
    assert locale["required"] == "Value is required"


def test_set_locale_with_new_values():
    """Test setting new values to the locale dictionary."""
    new_messages = {
        "new_key": "This is a new message",
        "undefined": "Custom undefined message",
        "const": lambda args: f"Custom const message for {args[0]}"  #
    }
    set_locale(new_messages)

    assert locale["new_key"] == "This is a new message"
    assert locale["undefined"] == "Custom undefined message"
    assert callable(locale["const"])
    # Pass a tuple to the lambda, as it expects args to be an iterable to access args[0]
    assert locale["const"](("value",)) == "Custom const message for value"
    assert "required" in locale  # Ensure other keys are still present
    assert locale["required"] == "Value is required"


def test_set_locale_with_none():
    """Test set_locale when None is passed, should return current locale without changes."""
    original_undefined_message = locale["undefined"]
    result = set_locale(None)
    assert result is locale  # Should return a reference to the global locale
    assert locale["undefined"] == original_undefined_message  # Ensure no change


def test_get_error_message_for_existing_key_string():
    """Test retrieving an existing error message that is a string."""
    assert get_error_message("required") == "Value is required"


def test_get_error_message_for_existing_key_callable():
    """Test retrieving an existing error message that is a callable."""
    message = get_error_message("type")
    assert callable(message)
    # The 'type' message expects a tuple of two arguments for %r, %r formatting
    assert message(("string", "int")) == "Value is not of type 'string', got 'int'"


def test_get_error_message_for_non_existent_key():
    """Test retrieving an error message for a key that does not exist."""
    assert get_error_message("non_existent_key") == "undefined"


def test_get_error_message_for_undefined_key():
    """Test retrieving the message for the 'undefined' key."""
    assert get_error_message("undefined") == "Undefined validation error"


def test_get_error_message_after_locale_update():
    """Test get_error_message behavior after locale has been updated."""
    set_locale({"custom_error": "This is a custom message"})
    assert get_error_message("custom_error") == "This is a custom message"
    assert get_error_message("undefined") == "Undefined validation error"  # Original undefined should still be there

    set_locale({"undefined": "New default error"})
    assert get_error_message("undefined") == "New default error"


def test_error_message_type_alias():
    """Test that ErrorMessage type alias works as expected."""

    def test_callable_message(args: Tuple[Any, ...]) -> str:
        return f"Callable message with {args[0]}"

    string_message: ErrorMessage = "A simple string message"
    callable_message: ErrorMessage = test_callable_message

    assert isinstance(string_message, str)
    assert callable(callable_message)
    # Pass as a tuple to match the expected argument handling for args[0]
    assert callable_message(("test_arg",)) == "Callable message with test_arg"
