from dataclasses import dataclass, field
from typing import Any, List, Iterable

from typing_extensions import Self

from yupy.ischema import _SchemaExpectedType, ISchema
from yupy.isized_schema import SizedSchema
from yupy.locale import locale
from yupy.schema import Schema
from yupy.util.concat_path import concat_path
from yupy.validation_error import ErrorMessage, Constraint, ValidationError

__all__ = ('ArraySchema',)


@dataclass
class ArraySchema(SizedSchema):
    _type: _SchemaExpectedType = field(init=False, default=(list, tuple))
    _fields: List[ISchema] = field(init=False, default_factory=list)
    _type_of: Schema = field(init=False, default_factory=Schema)

    def of(self, schema: ISchema, message: ErrorMessage = locale["array_of"]) -> Self:
        if not isinstance(schema, Schema):
            raise ValidationError(Constraint("array_of", message, type(schema)), invalid_value=schema)
        self._type_of = schema
        return self

    def validate(self, value: Any, abort_early: bool = True, path: str = "~") -> Any:
        super().validate(value, abort_early, path)
        return self._validate_array(value, abort_early, path)  # Convert tuple to list for iteration

    def _validate_array(self, value: Iterable, abort_early: bool = True,
                        path: str = "~") -> Iterable:
        errs: List[ValidationError] = []
        for i, v in enumerate(value):
            path_ = concat_path(path, i)
            try:
                self._type_of.validate(v, abort_early, path_)
            except ValidationError as err:
                if abort_early:
                    raise ValidationError(err.constraint, path_, invalid_value=v)
                else:
                    errs.append(err)
        if errs:
            raise ValidationError(
                Constraint('array', 'invalid array', path),
                path, errs, invalid_value=value)
        return value

    def __getitem__(self, item: int) -> ISchema:
        return self._fields[item]
