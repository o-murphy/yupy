from dataclasses import dataclass, field
from typing import Any, List, Tuple, TypeVar, Union

from yupy.ischema import _SchemaExpectedType
from yupy.isized import SizedSchema
from yupy.locale import locale
from yupy.schema import Schema
from yupy.util.concat_path import concat_path
from yupy.validation_error import ErrorMessage, Constraint, ValidationError

__all__ = ('ArraySchema',)

_T = TypeVar('_T')


@dataclass
class ArraySchema(SizedSchema[_T]):
    _type: _SchemaExpectedType = field(init=False, default=(list, tuple))
    _fields: List[Schema[Any]] = field(init=False, default_factory=list)
    _type_of: Schema[Any] = field(init=False, default_factory=Schema)
    _Self = TypeVar('_Self', bound='ArraySchema')

    def of(self: _Self, schema: Schema[Any], message: ErrorMessage = locale["array_of"]) -> _Self:
        if not isinstance(schema, Schema):
            raise ValidationError(Constraint("array_of", type(schema), message))
        self._type_of = schema
        return self

    def validate(self, value: Any, abort_early: bool = True, path: str = "") -> Any:
        super().validate(value, abort_early, path)
        self._validate_array(list(value), abort_early, path)  # Convert tuple to list for iteration
        return value

    def _validate_array(self, value: Union[List[Any], Tuple[Any, ...]], abort_early: bool = True,
                        path: str = "") -> None:
        errs: List[ValidationError] = []
        for i, v in enumerate(value):
            path_ = concat_path(path, i)
            try:
                self._type_of.validate(v, abort_early, path_)
            except ValidationError as err:
                if abort_early:
                    raise ValidationError(err.constraint, path_)
                else:
                    errs.append(err)
        if errs:
            raise ValidationError(
                Constraint(
                    'array',
                    path,
                    'invalid array'
                ),
                path, errs)

    def __getitem__(self, item: int) -> Schema[Any]:
        return self._fields[item]
