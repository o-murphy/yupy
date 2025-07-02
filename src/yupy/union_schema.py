from dataclasses import dataclass, field
from typing import Any, List, Union, Tuple

from typing_extensions import Self

from yupy.icomparable_schema import EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType, ISchema
from yupy.locale import locale
from yupy.util.concat_path import concat_path
from yupy.validation_error import ErrorMessage, Constraint, ValidationError

__all__ = ('UnionSchema',)

UnionOptionsType = Union[List[ISchema], Tuple[ISchema, ...]]

@dataclass
class UnionSchema(EqualityComparableSchema):
    _type: _SchemaExpectedType = field(init=False, default=object)
    _options: Union[List[ISchema], Tuple[ISchema, Any]] = field(init=False, default_factory=list)

    def one_of(self, options: UnionOptionsType, message: ErrorMessage = locale["one_of"]) -> Self:
        for schema in options:
            if not isinstance(schema, ISchema):
                raise ValidationError(Constraint("one_of", message, type(schema)), invalid_value=schema)
        self._options = options
        return self

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        value = super().validate(value, abort_early, path)
        return self._validate_union(value, abort_early, path)  # Convert tuple to list for iteration

    def _validate_union(self, value: Any, abort_early: bool = True,
                        path: str = "~") -> Any:
        matching_value = value
        errs: List[ValidationError] = []
        for i, opt in enumerate(self._options):
            path_ = concat_path(path, i)
            try:
                matching_value = opt.validate(value, abort_early, path_)
            except ValidationError as err:
                errs.append(err)

        if len(errs) >= len(self._options):
            raise ValidationError(
                Constraint('one_of', 'not match any expected Schema', path),
                path, errs, invalid_value=value)
        return matching_value