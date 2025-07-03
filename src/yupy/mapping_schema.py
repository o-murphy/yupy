from dataclasses import dataclass, field
from typing import Any, MutableMapping, TypeAlias, Union

from typing_extensions import Self

from yupy.adapters import _REQUIRED_UNDEFINED_, ISchemaAdapter
from yupy.icomparable_schema import EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType, ISchema, ErrorMessage
from yupy.locale import locale
from yupy.util.concat_path import concat_path
from yupy.validation_error import ValidationError, Constraint

__all__ = ('MappingSchema',)

_SchemaShape: TypeAlias = MutableMapping[str, Union[ISchema[Any], ISchemaAdapter]]


@dataclass
class MappingSchema(EqualityComparableSchema):
    _type: _SchemaExpectedType = field(init=False, default=dict)
    _fields: _SchemaShape = field(init=False, default_factory=dict)

    def shape(self, fields: _SchemaShape) -> Self:
        if not isinstance(fields, dict):  # Перевірка залишається на dict, оскільки shape визначається через dict
            raise ValidationError(
                Constraint("shape", locale["shape"])
            )
        for key, item in fields.items():
            if not isinstance(item, (ISchema, ISchemaAdapter)):
                raise ValidationError(
                    Constraint("shape_fields", locale["shape_fields"]),
                    key,
                    invalid_value=item
                )
        self._fields = fields
        return self

    def strict(self, is_strict: bool = True, message: ErrorMessage = locale['strict']) -> Self:
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
                    invalid_value=x # The whole dictionary is the invalid value in this case
                )

        return self.test(_)

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        value = super().validate(value, abort_early, path)
        if value is None and self._nullability:
            return None
        return self._validate_shape(value, abort_early, path)

    def _validate_shape(self, value: MutableMapping[str, Any],
                        abort_early: bool = True,
                        path: str = "~") -> MutableMapping[str, Any]:

        errs: list[ValidationError] = []
        for key, field_schema in self._fields.items(): # Renamed 'field' to 'field_schema' to avoid confusion with dataclasses.field
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
                errs.append(err) # Append the original error to collect all

        if errs:
            # When collecting errors, the main error describes the object itself being invalid
            raise ValidationError(
                Constraint('mapping', locale['mapping']), # Use locale for 'object' message
                path, errs, invalid_value=value # Pass the original value as the invalid_value for the object itself
            )
        return value

    def __getitem__(self, item: str) -> Union[ISchema, ISchemaAdapter]:
        return self._fields[item]
