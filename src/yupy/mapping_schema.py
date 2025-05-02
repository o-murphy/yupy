from dataclasses import dataclass, field
from typing import Any, Mapping, TypeVar, TypeAlias

from yupy.ischema import _SchemaExpectedType
from yupy.locale import locale
from yupy.schema import Schema
from yupy.util.concat_path import concat_path
from yupy.validation_error import ValidationError, Constraint

__all__ = ('MappingSchema',)

_T = TypeVar('_T')
Shape: TypeAlias = Mapping[str, Schema[Any]]

@dataclass
class MappingSchema(Schema[_T]):
    _type: _SchemaExpectedType = field(init=False, default=dict)
    _fields: Mapping[str, Schema[Any]] = field(init=False, default_factory=dict)
    _Self = TypeVar('_Self', bound='MappingSchema')

    def shape(self: _Self, fields: Shape) -> _Self:
        if not isinstance(fields, dict):  # Перевірка залишається на dict, оскільки shape визначається через dict
            raise ValidationError(
                Constraint("shape", None, locale["shape"])
            )
        if not all(isinstance(item, Schema) for item in fields.values()):
            raise ValidationError(
                Constraint(
                    "shape_values", None, locale["shape_values"]  # Todo: key there
                )
            )
        self._fields = fields
        return self

    def validate(self, value: Any, abort_early: bool = True, path: str = "") -> Any:
        super().validate(value, abort_early, path)
        self._validate_shape(value, abort_early, path)
        return value

    def _validate_shape(self, value: Mapping[str, Any], abort_early: bool = True, path: str = "") -> None:
        errs: list[ValidationError] = []
        for k, f in self._fields.items():
            path_ = concat_path(path, k)
            try:
                if not self._fields[k]._optional and k not in value:
                    raise ValidationError(
                        Constraint(
                            "required",
                            path_,
                            self._fields[k]._required,
                        ),
                        path_,
                    )
                if k in value:
                    self._fields[k].validate(value[k], abort_early, path_)
            except ValidationError as err:
                if abort_early:
                    raise ValidationError(err.constraint, path_)
                errs.append(err)
        if errs:
            raise ValidationError(
                Constraint(
                    'object',  # Виправлено з 'array' на 'object'
                    path,
                    'invalid object'
                ),
                path, errs
            )

    def __getitem__(self, item: str) -> Schema[Any]:
        return self._fields[item]
