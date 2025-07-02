from dataclasses import dataclass, field
from typing import Any, List, Iterable

from typing_extensions import Self

from yupy.icomparable_schema import ComparableSchema, EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType, ISchema
from yupy.isized_schema import SizedSchema
from yupy.locale import locale
from yupy.schema import Schema
from yupy.util.concat_path import concat_path
from yupy.validation_error import ErrorMessage, Constraint, ValidationError

__all__ = ('ArraySchema',)


@dataclass
class ArraySchema(SizedSchema, ComparableSchema, EqualityComparableSchema):
    _type: _SchemaExpectedType = field(init=False, default=(list, tuple))
    _fields: List[ISchema] = field(init=False, default_factory=list)
    _of_schema_type: ISchema = field(init=False, default_factory=Schema)

    # @property
    # def fields(self) -> List[ISchema]:
    #     return self._fields

    def of(self, schema: ISchema, message: ErrorMessage = locale["array_of"]) -> Self:
        if not isinstance(schema, ISchema):
            raise ValidationError(Constraint("array_of", message, type(schema)), invalid_value=schema)
        self._of_schema_type = schema
        return self

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        value = super().validate(value, abort_early, path)
        return self._validate_array(value, abort_early, path)  # Convert tuple to list for iteration

    def _validate_array(self, value: Iterable, abort_early: bool = True,
                        path: str = "~") -> Iterable:
        errs: List[ValidationError] = []
        for i, v in enumerate(value):
            path_ = concat_path(path, i)
            try:
                value = self._of_schema_type.validate(v, abort_early, path_)
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
