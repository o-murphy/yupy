import json
import warnings
from json import JSONDecodeError
from typing import Union, Any, Optional
from unittest.mock import patch

import pytest

from yupy._json_decode import get_json_parser, loads

orjson: Optional[Any]

try:
    from orjson import orjson
except ImportError:
    orjson = None


# Import the functions directly from your _json_decode.py file
# Assuming _json_decode.py is accessible in the test environment


# Define a mock orjson for testing when it's supposed to be installed
class MockOrjson:
    """A mock object to simulate orjson module behavior."""

    def loads(self, fp: Union[bytes, str], **kwargs: Any) -> Any:
        # Simulate orjson's loads behavior, which typically doesn't take many kwargs
        # and is strict about what it receives.
        if kwargs:
            # In a real scenario, orjson.loads would raise a TypeError for unsupported kwargs.
            # For this mock, we'll just acknowledge them if they were filtered.
            pass
        if isinstance(fp, (bytes, bytearray, memoryview)):
            return json.loads(fp.decode('utf-8'))  # Decode bytes for standard json parsing
        return json.loads(fp)

    # Add OPT_* attributes if needed for more advanced orjson testing, e.g.:
    # OPT_INDENT_2 = 1 # Example option for dumps, not loads


if orjson is None:
    orjson = MockOrjson()


class TestGetJsonParser:
    """
    Tests for the get_json_parser function in _json_decode.py.
    """

    @patch('yupy._json_decode.orjson', new=MockOrjson())
    def test_get_json_parser_orjson_available(self):
        """
        Tests that get_json_parser returns orjson when it's installed.
        """
        parser = get_json_parser("orjson")
        assert isinstance(parser, MockOrjson)  # Check if it's our mock orjson

    @patch('yupy._json_decode.orjson', new=None)
    def test_get_json_parser_orjson_not_available_falls_back_to_json(self):
        """
        Tests that get_json_parser falls back to json and warns when orjson is not installed.
        """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Ensure all warnings are caught
            parser = get_json_parser("orjson")
            assert parser is json
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "orjson is not installed. Falling back to the standard 'json' library." in str(w[-1].message)

    def test_get_json_parser_json(self):
        """
        Tests that get_json_parser returns json when "json" is explicitly requested.
        """
        parser = get_json_parser("json")
        assert parser is json

    def test_get_json_parser_unsupported(self):
        """
        Tests that get_json_parser raises ValueError for unsupported parser types.
        """
        with pytest.raises(ValueError,
                           match="Unsupported parser specified: 'unsupported'. Must be 'json' or 'orjson'."):
            get_json_parser("unsupported")  # type: ignore


class TestLoadsFunction:
    """
    Tests for the loads function in _json_decode.py.
    """

    json_data_str = '{"name": "Test", "value": 123, "is_active": true}'
    json_data_bytes = b'{"id": 1, "data": "binary_test"}'
    expected_dict_str = {"name": "Test", "value": 123, "is_active": True}
    expected_dict_bytes = {"id": 1, "data": "binary_test"}

    @pytest.mark.parametrize("parser_type", ["json", "orjson"])
    def test_loads_simple_string_data(self, parser_type):
        """
        Tests loads with simple JSON string data for both json and orjson.
        """
        if parser_type == "orjson" and not orjson:
            pytest.skip("orjson not installed, skipping orjson test.")

        result = loads(self.json_data_str, parser_type)
        assert result == self.expected_dict_str
        assert isinstance(result, dict)

    @pytest.mark.parametrize("parser_type", ["json", "orjson"])
    def test_loads_simple_bytes_data(self, parser_type):
        """
        Tests loads with simple JSON bytes data for both json and orjson.
        """
        if parser_type == "orjson" and not orjson:
            pytest.skip("orjson not installed, skipping orjson test.")

        result = loads(self.json_data_bytes, parser_type)
        assert result == self.expected_dict_bytes
        assert isinstance(result, dict)

    def test_loads_json_with_kwargs(self):
        """
        Tests loads with "json" parser and keyword arguments (e.g., object_hook).
        """

        def custom_hook(obj):
            if "value" in obj:
                obj["value_plus_one"] = obj["value"] + 1
            return obj

        result = loads(self.json_data_str, "json", object_hook=custom_hook)
        assert result == {"name": "Test", "value": 123, "is_active": True, "value_plus_one": 124}

    @patch('yupy._json_decode.orjson', new=MockOrjson())  # Ensure orjson is mocked for this test
    def test_loads_orjson_with_unsupported_kwargs_warns(self):
        """
        Tests that loads with "orjson" parser warns about unsupported kwargs.
        """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Pass a kwarg that orjson.loads does not support (e.g., 'cls')
            result = loads(self.json_data_str, "orjson", cls=json.JSONDecoder)
            assert result == self.expected_dict_str
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "Unsupported arguments passed to orjson.loads: cls." in str(w[-1].message)

    @patch('yupy._json_decode.orjson', new=None)  # Ensure orjson is not available
    @patch('yupy._json_decode.warnings.warn')  # Patch the warning for get_json_parser
    def test_loads_orjson_not_installed_fallback(self, mock_warn):
        """
        Tests that loads falls back to json if orjson is specified but not installed.
        """
        # The get_json_parser will issue a warning, then loads will use json.
        result = loads(self.json_data_str, "orjson")
        assert result == self.expected_dict_str
        mock_warn.assert_called_once_with(
            "orjson is not installed. Falling back to the standard 'json' library.",
            UserWarning
        )

    def test_loads_invalid_json_string(self):
        """
        Tests that loads raises JSONDecodeError for invalid JSON strings.
        """
        invalid_json = '{"key": "value'  # Malformed JSON
        with pytest.raises(JSONDecodeError):
            loads(invalid_json, "json")

        if orjson:
            with pytest.raises(JSONDecodeError):
                loads(invalid_json, "orjson")

    def test_loads_invalid_json_bytes(self):
        """
        Tests that loads raises JSONDecodeError for invalid JSON bytes.
        """
        invalid_json_bytes = b'{"key": "value'
        with pytest.raises(JSONDecodeError):
            loads(invalid_json_bytes, "json")

        if orjson:
            with pytest.raises(JSONDecodeError):
                loads(invalid_json_bytes, "orjson")

    def test_loads_empty_string(self):
        """
        Tests loads with an empty string, which should raise JSONDecodeError.
        """
        with pytest.raises(JSONDecodeError):
            loads("", "json")

        if orjson:
            with pytest.raises(JSONDecodeError):
                loads(b"", "orjson")
