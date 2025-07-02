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
                    Constraint("shape_fields", locale["shape_values"]),
                    key,
                    invalid_value=item
                )
        self._fields = fields
        return self

    def strict(self, message: ErrorMessage = locale['strict']) -> Self:
        def _(x: dict) -> None:
            defined_keys = set(self._fields.keys())
            input_keys = set(x.keys())

            unknown_keys = input_keys - defined_keys
            print(defined_keys, input_keys)

            if unknown_keys:
                raise ValidationError(
                    Constraint("strict", message, list(unknown_keys)),
                    invalid_value=x
                )

        return self.test(_)

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        value = super().validate(value, abort_early, path)
        return self._validate_shape(value, abort_early, path)

    def _validate_shape(self, value: MutableMapping[str, Any],
                        abort_early: bool = True,
                        path: str = "~") -> MutableMapping[str, Any]:

        errs: list[ValidationError] = []
        for key, field in self._fields.items():
            path_ = concat_path(path, key)
            try:
                value[key] = field.validate(value.get(key, _REQUIRED_UNDEFINED_), abort_early, path_)
            except ValidationError as err:
                if abort_early:
                    raise ValidationError(err.constraint, path_, invalid_value=value)
                errs.append(err)
        if errs:
            raise ValidationError(
                Constraint('object', 'invalid object', path),
                path, errs, invalid_value=value
            )
        return value

    def __getitem__(self, item: str) -> Union[ISchema, ISchemaAdapter]:
        return self._fields[item]
