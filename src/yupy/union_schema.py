from dataclasses import dataclass, field
from typing import Any, List, Union, Tuple

from typing_extensions import Self

from yupy.adapters import ISchemaAdapter
from yupy.icomparable_schema import EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType, ISchema
from yupy.locale import locale
from yupy.util.concat_path import concat_path
from yupy.validation_error import ErrorMessage, Constraint, ValidationError

__all__ = ('UnionSchema',)

UnionOptionsType = Union[List[Union[ISchema, ISchemaAdapter]], Tuple[Union[ISchema, ISchemaAdapter], ...]]

@dataclass
class UnionSchema(EqualityComparableSchema):
    _type: _SchemaExpectedType = field(init=False, default=object)
    _options: UnionOptionsType = field(init=False, default_factory=list)

    def one_of(self, options: UnionOptionsType, message: ErrorMessage = locale["one_of"]) -> Self:
        for schema in options:
            if not isinstance(schema, ISchema):
                raise ValidationError(Constraint("one_of",
                                      message, type(schema)),
                                      invalid_value=schema)
        self._options = options
        return self

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        value = super().validate(value, abort_early, path)
        if value is None and self._nullability:
            return None
        return self._validate_union(value, abort_early, path)  # Convert tuple to list for iteration

    def _validate_union(self, value: Any, abort_early: bool = True,
                        path: str = "~") -> Any:
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
        if len(errs) >= len(self._options): # This condition will always be true if no option matched
            raise ValidationError(
                Constraint('one_of', locale["one_of"], path), # The path passed to the constraint should reflect the current union path
                path, errs, invalid_value=value
            )
        # This part should ideally not be reached if no option matched and errs were collected
        return matching_value # Fallback,