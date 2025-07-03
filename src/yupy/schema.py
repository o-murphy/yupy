from dataclasses import field, dataclass
from typing import Any, List, Optional

from typing_extensions import Self

from yupy.adapters import _REQUIRED_UNDEFINED_
from yupy.ischema import TransformFunc, ValidatorFunc, _SchemaExpectedType
from yupy.locale import locale, ErrorMessage
from yupy.validation_error import ValidationError, Constraint

__all__ = ('Schema',)


@dataclass
class Schema:
    """
    The base class for all validation schemas in Yupy.

    This class provides fundamental validation capabilities including:
    - Type checking
    - Nullability control
    - Data transformation
    - Custom validation tests
    - Constant value checks

    It serves as the foundation upon which more specific schemas (e.g., StringSchema, NumberSchema)
    are built.

    Attributes:
        message (ErrorMessage): message of type ValidationError
        _type (_SchemaExpectedType): The expected Python type(s) for the schema's value.
            Defaults to `object`, meaning any type is initially allowed.
        _transforms (List[TransformFunc]): A list of transformation functions
            applied to the value before validation. Initialized as an empty list.
        _validators (List[ValidatorFunc]): A list of custom validator functions
            applied to the value after transformations and type checks. Initialized as an empty list.
        _nullability (bool): Indicates whether the schema allows `None` as a valid value.
            Defaults to `False`.
        _not_nullable (ErrorMessage): The error message to use when a non-nullable
            field receives `None`. Defaults to the locale-defined message for "not_nullable".
    """
    message: ErrorMessage = field(default=locale['type'])
    _type: _SchemaExpectedType = field(default=object)
    _transforms: List[TransformFunc] = field(init=False, default_factory=list)
    _validators: List[ValidatorFunc] = field(init=False, default_factory=list)
    _nullability: bool = False
    _not_nullable: ErrorMessage = locale["not_nullable"]

    @property
    def nullability(self) -> bool:
        """
        Returns whether the schema allows null values.

        Returns:
            bool: True if the schema is nullable, False otherwise.
        """
        return self._nullability

    def nullable(self) -> Self:
        """
        Configures the schema to allow `None` as a valid value.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """
        self._nullability: bool = True
        return self

    def not_nullable(self, message: ErrorMessage = locale["not_nullable"]) -> Self:
        """
        Configures the schema to disallow `None` as a valid value.

        Args:
            message (ErrorMessage): The error message to use if `None` is provided.
                Defaults to the locale-defined message for "not_nullable".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """
        self._nullability: bool = False
        self._not_nullable: ErrorMessage = message
        return self

    def _nullable_check(self, value: Any) -> None:
        """
        Internal method to perform a nullability check on the given value.

        Raises a `ValidationError` if the value is `None` and the schema is not nullable.

        Args:
            value (Any): The value to check for nullability.

        Raises:
            ValidationError: If the value is `None` and the schema is not nullable.
        """
        if not self._nullability and value is None:
            raise ValidationError(
                Constraint("nullable", self._not_nullable),
                invalid_value=value
            )

    def _type_check(self, value: Any) -> None:
        """
        Internal method to perform a type check on the given value against `_type`.

        Raises a `ValidationError` if the value does not match the expected type(s).
        If `_type` is `Any`, no type check is performed.

        Args:
            value (Any): The value to check against the schema's expected type.

        Raises:
            ValidationError: If the value's type does not match `_type`.
        """
        type_ = self._type
        if type_ is Any:
            return
        if not isinstance(value, type_):
            raise ValidationError(
                Constraint("type", self.message, type_, type(value)),
                invalid_value=value
            )

    def transform(self, func: TransformFunc) -> Self:
        """
        Adds a transformation function to be applied to the value before validation.

        Transformation functions modify the value. They are applied in the order
        they are added to the schema.

        Args:
            func (TransformFunc): A callable that takes one argument (the value)
                and returns the transformed value.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """
        self._transforms: List[TransformFunc]
        self._transforms.append(func)
        return self

    def _transform(self, value: Any) -> Any:
        """
        Applies all registered transformation functions to the given value.

        Args:
            value (Any): The value to be transformed.

        Returns:
            Any: The transformed value after applying all transformation functions.
        """
        transformed: Any = value
        for t in self._transforms:
            transformed = t(transformed)
        return transformed

    def test(self, func: ValidatorFunc) -> Self:
        """
        Adds a custom validation test function to the schema.

        Test functions perform additional validation logic and should raise
        a `ValidationError` if the value is invalid. These tests are run
        after transformations and type checks.

        Args:
            func (ValidatorFunc): A callable that takes one argument (the value)
                and performs validation. It should raise `ValidationError` on failure.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """
        self._validators.append(func)
        return self

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        """
        Validates the given value against the schema's rules.

        This is the primary method for performing validation. It applies:
        1. Nullability check.
        2. Handles `_REQUIRED_UNDEFINED_` for missing values.
        3. Applies transformations.
        4. Performs type checking.
        5. Runs all custom validation tests.

        Args:
            value (Any, optional): The value to validate. Defaults to None.
            abort_early (bool, optional): If True, validation stops on the first
                error encountered. If False, all errors are collected (though this
                base method will still raise on the first error if not caught
                by a higher-level schema like `MappingSchema` or `ArraySchema`).
                Defaults to True.
            path (str, optional): The current path in the data structure, used
                for more informative error messages. Defaults to "~".

        Returns:
            Any: The validated and potentially transformed value.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            self._nullable_check(value)

            if value is _REQUIRED_UNDEFINED_:
                value = None

            if value is None and self._nullability:
                return None

            transformed = self._transform(value)
            self._type_check(transformed)

            for v in self._validators:
                v(transformed)
            return transformed
        except ValidationError as err:
            raise ValidationError(err.constraint, path, invalid_value=value)

    def const(self, value: Optional[_SchemaExpectedType], message: ErrorMessage = locale["const"]) -> Self:
        """
        Configures the schema to validate that the value is strictly equal to a constant.

        Args:
            value (Optional[_SchemaExpectedType]): The constant value that the
                validated input must match.
            message (ErrorMessage): The error message to use if the value does not match
                the constant. Defaults to the locale-defined message for "const".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: Any) -> None:
            if x != value:
                raise ValidationError(Constraint("const", message, value), invalid_value=x)

        return self.test(_)
