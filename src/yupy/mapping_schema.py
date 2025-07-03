from dataclasses import dataclass, field
from typing import Any, MutableMapping, TypeAlias, Union

from typing_extensions import Self

from yupy.adapters import _REQUIRED_UNDEFINED_, ISchemaAdapter
from yupy.icomparable_schema import EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType, ISchema
from yupy.locale import locale, ErrorMessage
from yupy.util.concat_path import concat_path
from yupy.validation_error import ValidationError, Constraint

__all__ = ('MappingSchema',)

_SchemaShape: TypeAlias = MutableMapping[str, Union[ISchema[Any], ISchemaAdapter]]
"""
Type alias for the shape definition of a mapping schema.

It represents a dictionary where keys are strings (field names) and values
are instances of `ISchema` or `ISchemaAdapter`.
"""


@dataclass
class MappingSchema(EqualityComparableSchema):
    """
    A schema for validating dictionary-like (mapping) structures.

    This schema allows defining the expected fields and their corresponding
    schemas, enforcing strictness (disallowing unknown keys), and collecting
    multiple validation errors from nested fields.

    Inherits from `EqualityComparableSchema` for equality comparison methods.

    Attributes:
        _type (_SchemaExpectedType): The expected Python type(s) for the schema's value.
            Initialized to `dict`.
        _fields (_SchemaShape): A dictionary defining the expected fields of the
            mapping and their respective schemas.
    """
    _type: _SchemaExpectedType = field(init=False, default=dict)
    _fields: _SchemaShape = field(init=False, default_factory=dict)

    def shape(self, fields: _SchemaShape) -> Self:
        """
        Defines the expected shape (fields and their schemas) of the mapping.

        Args:
            fields (_SchemaShape): A dictionary where keys are field names (strings)
                and values are `ISchema` or `ISchemaAdapter` instances defining
                the validation rules for each field.

        Returns:
            Self: The schema instance, allowing for method chaining.

        Raises:
            TypeError: If `fields` is not a dictionary or if any value
                in `fields` is not an `ISchema` or `ISchemaAdapter` instance.
        """
        if not isinstance(fields, dict):
            raise TypeError("Shape definition must be a dictionary.")
        for key, item in fields.items():
            # TODO: possibly need check if keys are immutable
            # if not isinstance(key, (int, str, Enum)):
            #     raise TypeError("each shape key must be an instance of int or str")
            if not isinstance(item, (ISchema, ISchemaAdapter)):
                raise TypeError("each shape value must be an instance of ISchema or ISchemaAdapter")
        self._fields = fields
        return self

    def strict(self, is_strict: bool = True, message: ErrorMessage = locale['strict']) -> Self:
        """
        Configures the schema to enforce strictness, disallowing unknown keys.

        If `is_strict` is True, any keys present in the input mapping that are
        not defined in the schema's `shape` will cause a validation error.
        If `is_strict` is False, unknown keys are ignored.

        Args:
            is_strict (bool, optional): If True, strict mode is enabled. Defaults to True.
            message (ErrorMessage): The error message to use if unknown keys are found.
                Defaults to the locale-defined message for "strict".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """
        if not is_strict:
            # If not strict, do not apply the test
            return self

        def _(x: dict) -> None:
            defined_keys = set(self._fields.keys())
            input_keys = set(x.keys())

            unknown_keys = input_keys - defined_keys
            # print(defined_keys, input_keys) # Keep for debugging if needed

            if unknown_keys:
                raise ValidationError(
                    Constraint("strict", message, list(unknown_keys)),
                    invalid_value=x  # The whole dictionary is the invalid value in this case
                )

        return self.test(_)

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        """
        Validates the given value as a mapping (dictionary).

        This method first performs general schema validation (e.g., type, nullability)
        inherited from base classes, then delegates to `_validate_shape` for
        field-wise validation.

        Args:
            value (Any, optional): The value to validate. Defaults to None.
            abort_early (bool, optional): If True, validation stops on the first
                error encountered during field validation. If False, all errors
                are collected. Defaults to True.
            path (str, optional): The current path in the data structure, used
                for more informative error messages. Defaults to "~".

        Returns:
            Any: The validated and potentially transformed mapping.

        Raises:
            ValidationError: If validation fails at the mapping level or for any field.
        """
        value = super().validate(value, abort_early, path)
        if value is None and self._nullability:
            return None
        return self._validate_shape(value, abort_early, path)

    def _validate_shape(self, value: MutableMapping[str, Any],
                        abort_early: bool = True,
                        path: str = "~") -> MutableMapping[str, Any]:
        """
        Internal method to perform field-wise validation of the mapping.

        It iterates through each defined field in `_fields`, validates its
        corresponding value in the input `value` against the field's schema,
        and collects errors if `abort_early` is False.

        Args:
            value (MutableMapping[str, Any]): The mapping (dictionary) to validate.
            abort_early (bool, optional): If True, validation stops on the first
                field error. If False, all field errors are collected. Defaults to True.
            path (str, optional): The current path in the data structure.
                Defaults to "~".

        Returns:
            MutableMapping[str, Any]: The validated mapping, potentially with
                transformed field values.

        Raises:
            ValidationError: If any field fails validation, or a general "mapping"
                constraint error if multiple errors are collected.
        """
        errs: list[ValidationError] = []
        for key, field_schema in self._fields.items():  # Renamed 'field' to 'field_schema' to avoid confusion with dataclasses.field
            path_ = concat_path(path, key)
            try:
                # Pass _REQUIRED_UNDEFINED_ if key is not in value
                field_value = value.get(key, _REQUIRED_UNDEFINED_)
                value[key] = field_schema.validate(field_value, abort_early, path_)
            except ValidationError as err:
                if abort_early:
                    # When abort_early is True, re-raise the original error with the correct path and invalid_value
                    # The original err.path is already correct
                    raise err
                errs.append(err)  # Append the original error to collect all

        if errs:
            # When collecting errors, the main error describes the object itself being invalid
            raise ValidationError(
                Constraint('mapping', locale['mapping']),  # Use locale for 'object' message
                path, errs, invalid_value=value  # Pass the original value as the invalid_value for the object itself
            )
        return value

    def __getitem__(self, item: str) -> Union[ISchema, ISchemaAdapter]:
        """
        Allows accessing the schema definition for a specific field by its name.

        Args:
            item (str): The name of the field whose schema is to be retrieved.

        Returns:
            Union[ISchema, ISchemaAdapter]: The schema associated with the given field name.

        Raises:
            KeyError: If the field name is not found in the schema's defined fields.
        """
        return self._fields[item]
