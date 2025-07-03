from dataclasses import dataclass, field
from typing import Any, List, Union, Optional

from typing_extensions import Self

from yupy.adapters import ISchemaAdapter
from yupy.icomparable_schema import ComparableSchema, EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType, ISchema
from yupy.isized_schema import SizedSchema
from yupy.locale import locale
from yupy.util.concat_path import concat_path
from yupy.validation_error import Constraint, ValidationError

__all__ = ('ArraySchema',)


@dataclass
class ArraySchema(SizedSchema, ComparableSchema, EqualityComparableSchema):
    """
    A schema for validating array-like structures (lists and tuples).

    This schema allows defining rules for the overall array (e.g., length, comparisons)
    and for the type/schema of its individual elements using the `of()` method.

    Inherits from `SizedSchema` for length-based validations, `ComparableSchema`
    for comparison operations, and `EqualityComparableSchema` for equality checks.

    Attributes:
        _type (_SchemaExpectedType): The expected Python type(s) for the schema's value.
            Initialized to `(list, tuple)` to accept both lists and tuples.
        _fields (List[Union[ISchema, ISchemaAdapter]]): A list to potentially hold
            schemas for specific indices (though currently not directly used for this
            purpose in the provided methods).
        _of_schema_type (Optional[Union[ISchema, ISchemaAdapter]]): An optional schema
            that defines the validation rules for each element within the array.
            If None, elements are not individually validated by this schema.
    """
    _type: _SchemaExpectedType = field(init=False, default=(list, tuple))
    _fields: List[Union[ISchema, ISchemaAdapter]] = field(init=False, default_factory=list)
    _of_schema_type: Optional[Union[ISchema, ISchemaAdapter]] = field(init=False, default=None)

    def of(self, schema: Union[ISchema, ISchemaAdapter]) -> Self:
        """
        Specifies the schema that each element in the array must conform to.

        Args:
            schema (Union[ISchema, ISchemaAdapter]): The schema to apply to each
                individual element of the array.
            message (ErrorMessage): The error message to use if the provided `schema`
                is not a valid schema type. Defaults to the locale-defined message
                for "array_of".

        Returns:
            Self: The schema instance, allowing for method chaining.

        Raises:
            TypeError: If the provided `schema` is not an instance of
                `ISchema` or `ISchemaAdapter`.
        """
        if not isinstance(schema, (ISchema, ISchemaAdapter)):
            raise TypeError("schema must be an instance of ISchema or ISchemaAdapter")

        self._of_schema_type = schema
        return self

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        """
        Validates the given value as an array.

        This method first performs general schema validation (e.g., type, nullability)
        inherited from base classes, then delegates to `_validate_array` for
        element-wise validation if an `_of_schema_type` is set.

        Args:
            value (Any, optional): The value to validate. Defaults to None.
            abort_early (bool, optional): If True, validation stops on the first
                error encountered during element-wise validation. If False, all
                errors are collected. Defaults to True.
            path (str, optional): The current path in the data structure, used
                for more informative error messages. Defaults to "~".

        Returns:
            Any: The validated and potentially transformed array (list or tuple).

        Raises:
            ValidationError: If validation fails at the array level or for any element.
        """
        value = super().validate(value, abort_early, path)
        if value is None and self._nullability:
            return None
        return self._validate_array(value, abort_early, path)  # Convert tuple to list for iteration

    def _validate_array(self, value: Union[list, tuple], abort_early: bool = True,
                        path: str = "~") -> Union[list, tuple]:
        """
        Internal method to perform element-wise validation of the array.

        If `_of_schema_type` is not set, the array is returned as is.
        Otherwise, it iterates through each item, validates it against `_of_schema_type`,
        and collects errors if `abort_early` is False.

        Args:
            value (Union[list, tuple]): The array (list or tuple) to validate.
            abort_early (bool, optional): If True, validation stops on the first
                element error. If False, all element errors are collected. Defaults to True.
            path (str, optional): The current path in the data structure.
                Defaults to "~".

        Returns:
            Union[list, tuple]: The validated array, potentially with transformed elements.
                The type (list or tuple) is preserved from the original input.

        Raises:
            ValidationError: If any element fails validation, or a general "array"
                constraint error if multiple errors are collected.
        """
        if self._of_schema_type is None:
            return value

        errs: List[ValidationError] = []
        validated_result = []
        original_type = type(value)

        for i, item in enumerate(value):
            item_path = concat_path(path, i)
            try:
                validated_item = self._of_schema_type.validate(item, abort_early, item_path)
                validated_result.append(validated_item)
            except ValidationError as err:
                if abort_early:
                    raise err
                else:
                    errs.append(err)
                    validated_result.append(item)

        if errs:
            raise ValidationError(
                Constraint('array', locale["array"], path),
                path, errs, invalid_value=value
            )

        if original_type is tuple:
            return tuple(validated_result)
        return validated_result

    def __getitem__(self, item: int) -> Union[ISchema, ISchemaAdapter]:
        """
        Allows accessing schema definitions for specific array indices.

        Note: This method currently accesses `_fields`, which is not populated
        by the `of()` method. Its utility depends on how `_fields` is intended
        to be used elsewhere (e.g., for fixed-size arrays with different schemas
        per index).

        Args:
            item (int): The integer index of the schema to retrieve.

        Returns:
            Union[ISchema, ISchemaAdapter]: The schema associated with the given index.

        Raises:
            IndexError: If the index is out of bounds for `_fields`.
        """
        return self._fields[item]
