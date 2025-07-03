import json
import warnings
from typing import Any, Literal, TypedDict, Optional, Union

orjson: Optional[Any]

# Attempt to import orjson; if not available, fall back to None
try:
    import orjson
except ImportError:
    orjson = None

__all__ = (
    'SUPPORTED_JSON_PARSER',
    'loads',
    'get_json_parser',
)

# Define a TypeVar for the parser type (e.g., "json" or "orjson")
SUPPORTED_JSON_PARSER = Literal["json", "orjson"]


class JsonLoadsKwargs(TypedDict, total=False):
    """Represents options typically used with the standard 'json' library."""
    cls: Any
    object_hook: Any
    parse_float: Any
    parse_int: Any
    parse_constant: Any
    object_pairs_hook: Any
    strict: bool


def get_json_parser(parser: SUPPORTED_JSON_PARSER) -> Any:
    """
    Returns the appropriate JSON parser module (json or orjson) based on the input.

    Args:
        parser: The parser type, either "json" or "orjson".

    Returns:
        The json or orjson module.

    Raises:
        ValueError: If an unsupported parser type is provided.
    """
    if parser == "orjson":
        if orjson is None:
            warnings.warn(
                "orjson is not installed. Falling back to the standard 'json' library.",
                UserWarning
            )
            return json  # Fallback to json module
        return orjson
    elif parser == "json":
        return json
    else:
        # This case should ideally be caught by type checkers due to Literal,
        # but provides a robust runtime check.
        raise ValueError(f"Unsupported parser specified: '{parser}'. Must be 'json' or 'orjson'.")


def loads(
        fp: Union[bytes, bytearray, memoryview, str],  # Reverted to str as per user's latest code
        parser: SUPPORTED_JSON_PARSER,  # The parser type is constrained to "json" or "orjson"
        **kwargs: JsonLoadsKwargs  # Accept any keyword arguments, to be filtered later
) -> Any:
    """
    Parses a JSON string or byte-like object using either 'json' or 'orjson' library.

    Args:
        fp: The JSON string or byte-like object to parse.
        parser: The parser to use, either "json" or "orjson".
                If "orjson" is specified but not installed, it falls back to "json".
        **kwargs: Additional keyword arguments to pass to the chosen parser's loads function.
                  Arguments not supported by the chosen parser will be ignored,
                  and a warning will be issued.

    Returns:
        The parsed Python object (dict, list, str, int, float, bool, None).

    Raises:
        ValueError: If an unsupported parser type is provided.
        json.JSONDecodeError: If the JSON string is invalid.
        orjson.JSONDecodeError: If the JSON string is invalid.
    """
    json_parser = get_json_parser(parser)

    if json_parser is orjson:
        unsupported_keys = [k for k in kwargs]
        if unsupported_keys:
            warnings.warn(
                f"Unsupported arguments passed to orjson.loads: {', '.join(unsupported_keys)}. "
                "These arguments will be ignored.",
                UserWarning
            )
        return orjson.loads(fp)
    else:  # This implies json_parser is json
        # json.loads primarily expects str, but can handle bytes if encoding is specified.
        # If bytes are passed, json.loads will attempt to decode them.
        return json_parser.loads(fp, **kwargs)
