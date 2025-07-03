from types import UnionType
from typing import Protocol, TypeVar, Callable, Any, TypeAlias, runtime_checkable, List, Type, Optional, Union

from typing_extensions import Self

from yupy.locale import ErrorMessage

__all__ = (
    'ISchema',
    'TransformFunc',
    'ValidatorFunc',
    '_SchemaExpectedType'
)

_T = TypeVar("_T")
"""
A generic TypeVar used to represent the type of the value being validated
by a schema.
"""

_SchemaExpectedType: TypeAlias = Union[type[_T], UnionType, tuple[Any, ...]]
"""
Type alias for the expected type(s) that a schema can validate against.

This can be:
- A single type (e.g., `str`, `int`).
- A `UnionType` (e.g., `str | int` in Python 3.10+).
- A tuple of types (e.g., `(str, int)` for `isinstance` checks).
"""

_P = TypeVar('_P', bound=_SchemaExpectedType)
"""
A TypeVar used to bind the `ISchema` protocol to a specific `_SchemaExpectedType`,
ensuring type consistency across the schema's validation methods.
"""

TransformFunc: TypeAlias = Callable[[Any], Any]
"""
Type alias for a transformation function.

A `TransformFunc` takes any value as input and returns a transformed value.
These functions are applied to the input value before validation.
"""

ValidatorFunc: TypeAlias = Callable[[_T], None]
"""
Type alias for a validator function.

A `ValidatorFunc` takes a value of type `_T` as input and performs validation.
It should raise a `ValidationError` if the value is invalid; otherwise, it
returns `None`.
"""


@runtime_checkable
class ISchema(Protocol[_P]):
    """
    ISchema defines the interface for all schema types in the Yupy validation library.

    This protocol outlines the core methods and properties that any schema
    must implement to support type checking, nullability, data transformation,
    custom validation tests, and constant value checks.

    Attributes:
        _type (Type[_P]): The expected Python type(s) for the schema's value.
        _transforms (List[TransformFunc]): A list of transformation functions
            applied to the value before validation.
        _validators (List[ValidatorFunc]): A list of custom validator functions
            applied to the value.
        _nullability (bool): Indicates whether the schema allows `None` as a valid value.
        _not_nullable (ErrorMessage): The error message to use when a non-nullable
            field receives `None`.
    """

    _type: Type[_P]
    _transforms: List[TransformFunc]
    _validators: List[ValidatorFunc]
    _nullability: bool
    _not_nullable: ErrorMessage

    @property
    def nullability(self) -> bool:
        """
        Returns whether the schema allows null values.

        Returns:
            bool: True if the schema is nullable, False otherwise.
        """

    def nullable(self) -> Self:
        """
        Configures the schema to allow `None` as a valid value.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

    def not_nullable(self, message: ErrorMessage) -> Self:
        """
        Configures the schema to disallow `None` as a valid value.

        Args:
            message (ErrorMessage): The error message to use if `None` is provided.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

    def _nullable_check(self, value: Any) -> None:
        """
        Internal method to perform a nullability check on the given value.

        Raises a ValidationError if the value is `None` and the schema is not nullable.

        Args:
            value (Any): The value to check for nullability.
        """

    def _type_check(self, value: Any) -> None:
        """
        Internal method to perform a type check on the given value against `_type`.

        Raises a ValidationError if the value does not match the expected type(s).

        Args:
            value (Any): The value to check against the schema's expected type.
        """

    def transform(self, func: TransformFunc) -> Self:
        """
        Adds a transformation function to be applied to the value before validation.

        Transformation functions modify the value. They are applied in the order
        they are added.

        Args:
            func (TransformFunc): A callable that takes one argument (the value)
                and returns the transformed value.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

    def _transform(self, value: Any) -> Any:
        """
        Applies all registered transformation functions to the given value.

        Args:
            value (Any): The value to be transformed.

        Returns:
            Any: The transformed value after applying all transformation functions.
        """

    def test(self, func: ValidatorFunc) -> Self:
        """
        Adds a custom validation test function to the schema.

        Test functions perform additional validation logic and should raise
        a `ValidationError` if the value is invalid.

        Args:
            func (ValidatorFunc): A callable that takes one argument (the value)
                and performs validation. It should raise `ValidationError` on failure.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "") -> _P:
        """
        Validates the given value against the schema's rules.

        This is the primary method for performing validation. It applies
        transformations, type checks, nullability checks, and custom tests.

        Args:
            value (Any, optional): The value to validate. Defaults to None.
            abort_early (bool, optional): If True, validation stops on the first
                error encountered. If False, all errors are collected. Defaults to True.
            path (str, optional): The current path in the data structure, used
                for more informative error messages. Defaults to "".

        Returns:
            _P: The validated and potentially transformed value.

        Raises:
            ValidationError: If validation fails. If `abort_early` is False,
                this error may contain a list of nested errors.
        """

    def const(self, value: Optional[_P], message: ErrorMessage) -> Self:
        """
        Configures the schema to validate that the value is strictly equal to a constant.

        Args:
            value (Optional[_P]): The constant value that the validated input must match.
            message (ErrorMessage): The error message to use if the value does not match
                the constant.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """
