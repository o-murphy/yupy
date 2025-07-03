from dataclasses import dataclass, field
from typing import Any, List, Union, Tuple

from typing_extensions import Self

from yupy.adapters import ISchemaAdapter
from yupy.icomparable_schema import EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType, ISchema
from yupy.locale import locale, ErrorMessage
from yupy.util.concat_path import concat_path
from yupy.validation_error import Constraint, ValidationError

__all__ = ('UnionSchema',)

UnionOptionsType = Union[List[Union[ISchema, ISchemaAdapter]], Tuple[Union[ISchema, ISchemaAdapter], ...]]


@dataclass
class UnionSchema(EqualityComparableSchema):
    """
    A schema for validating a value against a set of alternative schemas (a union type).

    The value is considered valid if it successfully validates against at least one
    of the provided schemas.

    Inherits from `EqualityComparableSchema` for equality comparison methods.

    Attributes:
        _type (_SchemaExpectedType): The expected Python type(s) for the schema's value.
            Initialized to `object`, as a union can represent any type.
        _options (UnionOptionsType): A list or tuple of `ISchema` or `ISchemaAdapter`
            instances, representing the alternative schemas for validation.
    """
    _type: _SchemaExpectedType = field(init=False, default=object)
    _options: UnionOptionsType = field(init=False, default_factory=list)

    def one_of(self, options: UnionOptionsType, message: ErrorMessage = locale["one_of"]) -> Self:
        """
        Specifies the set of alternative schemas that the value must conform to.

        The value will be considered valid if it passes validation against any
        one of the schemas in the `options` list/tuple.

        Args:
            options (UnionOptionsType): An iterable (list or tuple) containing
                `ISchema` or `ISchemaAdapter` instances, each representing a
                possible valid schema for the value.
            message (ErrorMessage): The error message to use if any schema in
                `options` is not a valid schema type. Defaults to the locale-defined
                message for "one_of".

        Returns:
            Self: The schema instance, allowing for method chaining.

        Raises:
            ValidationError: If any item in `options` is not an instance of
                `ISchema` or `ISchemaAdapter`.
        """
        for schema in options:
            if not isinstance(schema, ISchema):
                raise TypeError("each union schema must be an instance of ISchema or ISchemaAdapter")
        self._options = options
        return self

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        """
        Validates the given value against the union's alternative schemas.

        This method first performs general schema validation (e.g., type, nullability)
        inherited from base classes, then delegates to `_validate_union` for
        trying each alternative schema.

        Args:
            value (Any, optional): The value to validate. Defaults to None.
            abort_early (bool, optional): If True, validation stops on the first
                successful schema match. If False, it attempts to validate against
                all schemas and collects all errors if no match is found. Defaults to True.
            path (str, optional): The current path in the data structure, used
                for more informative error messages. Defaults to "~".

        Returns:
            Any: The validated and potentially transformed value from the first
                successfully matching schema.

        Raises:
            ValidationError: If the value does not validate against any of the
                alternative schemas.
        """
        value = super().validate(value, abort_early, path)
        if value is None and self._nullability:
            return None
        return self._validate_union(value, abort_early, path)  # Convert tuple to list for iteration

    def _validate_union(self, value: Any, abort_early: bool = True,
                        path: str = "~") -> Any:
        """
        Internal method to iterate through alternative schemas and attempt validation.

        It tries to validate the `value` against each schema in `_options`.
        If a schema successfully validates the value, that validated value is returned.
        If no schema validates the value, a `ValidationError` is raised,
        potentially containing all the errors from the failed attempts.

        Args:
            value (Any): The value to validate against the union options.
            abort_early (bool, optional): If True, returns on the first successful
                validation. If False, continues to collect errors from all failed
                attempts before raising a final error if no match is found. Defaults to True.
            path (str, optional): The current path in the data structure.
                Defaults to "~".

        Returns:
            Any: The validated value from the first matching schema.

        Raises:
            ValidationError: If the value fails to validate against all alternative schemas.
        """
        matching_value = value
        errs: List[ValidationError] = []
        for i, opt in enumerate(self._options):
            path_ = concat_path(path, i)
            try:
                matching_value = opt.validate(value, abort_early, path_)
                # If an option successfully validates, we've found a match
                return matching_value
            except ValidationError as err:
                errs.append(err)

        # If we reach here and no match was found, raise a Union-specific error
        if len(errs) >= len(self._options):  # This condition will always be true if no option matched
            raise ValidationError(
                Constraint('one_of', locale["one_of"], path),
                # The path passed to the constraint should reflect the current union path
                path, errs, invalid_value=value
            )
        # This part should ideally not be reached if no option matched and errs were collected
        return matching_value  # Fallback,
