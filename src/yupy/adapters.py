from copy import deepcopy
from typing import Any, TypeVar, Protocol, runtime_checkable, Union

from typing_extensions import Self

from yupy.ischema import ISchema
from yupy.locale import locale, ErrorMessage
from yupy.validation_error import ValidationError, Constraint, _EMPTY_MESSAGE_

_REQUIRED_UNDEFINED_ = TypeVar("_REQUIRED_UNDEFINED_")

__all__ = (
    'ISchemaAdapter',
    'SchemaAdapter',
    'SchemaDefaultAdapter',
    'SchemaRequiredAdapter',
    'SchemaImmutableAdapter',
    '_REQUIRED_UNDEFINED_',
)


@runtime_checkable
class ISchemaAdapter(Protocol):
    """
    ISchemaAdapter defines the interface for schema adapters.

    Schema adapters wrap an existing schema (`ISchema` or another `ISchemaAdapter`)
    to modify its behavior, such as providing default values, enforcing requiredness,
    or ensuring immutability.

    Attributes:
        _schema (Union[ISchema, 'ISchemaAdapter']): The underlying schema
            that this adapter wraps.
        _message (ErrorMessage): The default error message for this adapter's
            specific validation logic.
    """
    _schema: Union[ISchema, 'ISchemaAdapter']
    _message: ErrorMessage

    # def __init__(self, schema: Union[ISchema, 'ISchemaAdapter'],
    #              message: ErrorMessage = _EMPTY_MESSAGE_) -> None: ...

    @property
    def schema(self) -> Union[ISchema, 'ISchemaAdapter']:
        """
        Returns the underlying schema wrapped by this adapter.

        Returns:
            Union[ISchema, 'ISchemaAdapter']: The wrapped schema.
        """

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        """
        Validates the given value using the adapter's logic and the wrapped schema.

        Args:
            value (Any, optional): The value to validate. Defaults to None.
            abort_early (bool, optional): If True, validation stops on the first
                error. If False, all errors are collected. Defaults to True.
            path (str, optional): The current path in the data structure, used
                for more informative error messages. Defaults to "~".

        Returns:
            Any: The validated and potentially modified value.

        Raises:
            ValidationError: If validation fails.
        """


class SchemaAdapter:
    """
    A base class for schema adapters.

    This class provides the fundamental structure for wrapping an `ISchema`
    or another `ISchemaAdapter` and delegating validation calls.

    Attributes:
        _schema (Union[ISchema, ISchemaAdapter]): The underlying schema
            that this adapter wraps.
        _message (ErrorMessage): The default error message for this adapter.
    """
    _schema: Union[ISchema, ISchemaAdapter]
    _message: ErrorMessage

    def __init__(self, schema: Union[ISchema, ISchemaAdapter],
                 message: ErrorMessage = _EMPTY_MESSAGE_) -> None:
        """
        Initializes a new SchemaAdapter instance.

        Args:
            schema (Union[ISchema, ISchemaAdapter]): The schema to wrap.
            message (ErrorMessage, optional): The default error message for
                this adapter. Defaults to `_EMPTY_MESSAGE_`.
        """
        self._schema = schema
        self._message = message

    @property
    def schema(self) -> Union[ISchema, ISchemaAdapter]:
        """
        Returns the underlying schema wrapped by this adapter.

        Returns:
            Union[ISchema, ISchemaAdapter]: The wrapped schema.
        """
        return self._schema

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        """
        Validates the given value by delegating to the wrapped schema's validate method.

        Args:
            value (Any, optional): The value to validate. Defaults to None.
            abort_early (bool, optional): If True, validation stops on the first
                error. If False, all errors are collected. Defaults to True.
            path (str, optional): The current path in the data structure.
                Defaults to "~".

        Returns:
            Any: The validated value returned by the wrapped schema.

        Raises:
            ValidationError: If validation fails in the wrapped schema.
        """
        return self._schema.validate(value, abort_early, path)


class SchemaDefaultAdapter(SchemaAdapter):
    """
    An adapter that provides a default value for a schema if the input value is `None`.

    It can also be configured to "ensure" a default value, meaning if validation
    of the input (or default) fails, the default value will be returned instead
    of raising an error.

    Attributes:
        _default (Any): The default value to use.
        _ensure (bool): If True, the default value is returned on validation error.
    """
    _default: Any
    _ensure: bool

    def __init__(self,
                 default_value: Any,
                 schema: Union[ISchema, ISchemaAdapter],
                 message: ErrorMessage = _EMPTY_MESSAGE_):
        """
        Initializes a new SchemaDefaultAdapter instance.

        Args:
            default_value (Any): The value to use as a default.
            schema (Union[ISchema, ISchemaAdapter]): The schema to wrap.
            message (ErrorMessage, optional): The default error message for
                this adapter. Defaults to `_EMPTY_MESSAGE_`.
        """
        super().__init__(schema, message)
        self._default = default_value
        self._ensure = False

    def ensure(self) -> Self:
        """
        Configures the adapter to return the default value if validation fails.

        Returns:
            Self: The adapter instance, allowing for method chaining.
        """
        self._ensure = True
        return self

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        """
        Validates the given value, applying the default if the input is `None`.

        If `_ensure` is True and validation fails, the `_default` value is returned.
        Otherwise, validation errors are propagated.

        Args:
            value (Any, optional): The value to validate. Defaults to None.
            abort_early (bool, optional): If True, validation stops on the first
                error. If False, all errors are collected. Defaults to True.
            path (str, optional): The current path in the data structure.
                Defaults to "~".

        Returns:
            Any: The validated value, or the default value if `_ensure` is True
                and validation failed.

        Raises:
            ValidationError: If validation fails and `_ensure` is False.
        """
        if value is None:
            value = self._default
        try:
            return super().validate(value, abort_early, path)
        except ValidationError as e:
            if not self._ensure:
                raise e
        return self._default


class SchemaRequiredAdapter(SchemaAdapter):
    """
    An adapter that enforces a schema field as required.

    If the input value is `_REQUIRED_UNDEFINED_` (indicating a missing field),
    a `ValidationError` is immediately raised. Otherwise, validation is
    delegated to the wrapped schema.
    """

    def __init__(self, schema: Union[ISchema, ISchemaAdapter],
                 message: ErrorMessage = locale['required']):
        """
        Initializes a new SchemaRequiredAdapter instance.

        Args:
            schema (Union[ISchema, ISchemaAdapter]): The schema to wrap.
            message (ErrorMessage, optional): The error message to use if the
                field is missing. Defaults to the locale-defined message for "required".
        """
        super().__init__(schema, message)

    def validate(self, value: Any = _REQUIRED_UNDEFINED_, abort_early: bool = True, path: str = "~", path_=None) -> Any:
        """
        Validates the given value, ensuring it is not `_REQUIRED_UNDEFINED_`.

        If `value` is `_REQUIRED_UNDEFINED_`, a "required" validation error is raised.
        Otherwise, validation is delegated to the wrapped schema.

        Args:
            value (Any, optional): The value to validate. Defaults to `_REQUIRED_UNDEFINED_`.
            abort_early (bool, optional): If True, validation stops on the first
                error. If False, all errors are collected. Defaults to True.
            path (str, optional): The current path in the data structure.
                Defaults to "~".
            path_ (Any, optional): An unused parameter, likely a remnant.

        Returns:
            Any: The validated value returned by the wrapped schema.

        Raises:
            ValidationError: If `value` is `_REQUIRED_UNDEFINED_` or if validation
                fails in the wrapped schema.
        """
        if value is _REQUIRED_UNDEFINED_:
            raise ValidationError(
                Constraint("required", self._message, path),
                path, invalid_value=value
            )
        return self._schema.validate(value, abort_early, path)


class SchemaImmutableAdapter(SchemaAdapter):
    def __init__(self, schema: Union[ISchema, ISchemaAdapter],
                 message: ErrorMessage = _EMPTY_MESSAGE_):
        """
        Initializes a new SchemaImmutableAdapter instance.

        Args:
            schema (Union[ISchema, ISchemaAdapter]): The schema to wrap.
            message (ErrorMessage, optional): The default error message for
                this adapter. Defaults to `_EMPTY_MESSAGE_`.
        """
        super().__init__(schema, message)

    def validate(self, value: Any = _REQUIRED_UNDEFINED_, abort_early: bool = True, path: str = "~", path_=None) -> Any:
        """
        Validates the given value by deep copying it and passing the copy to the
        wrapped schema. The original value is always returned.

        This ensures that any transformations or modifications performed by the
        wrapped schema do not affect the original input value.

        Args:
            value (Any, optional): The value to validate. Defaults to `_REQUIRED_UNDEFINED_`.
            abort_early (bool, optional): If True, validation stops on the first
                error. If False, all errors are collected. Defaults to True.
            path (str, optional): The current path in the data structure.
                Defaults to "~".
            path_ (Any, optional): An unused parameter, likely a remnant.

        Returns:
            Any: The original, unmodified input value.

        Raises:
            ValidationError: If validation of the deep copy fails in the wrapped schema.
        """
        value_copy = deepcopy(value)
        self._schema.validate(value_copy, abort_early, path)
        return value
