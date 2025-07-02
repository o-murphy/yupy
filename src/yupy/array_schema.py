from dataclasses import dataclass, field
from typing import Any, List, Union, Optional

from typing_extensions import Self

from yupy.adapters import ISchemaAdapter
from yupy.icomparable_schema import ComparableSchema, EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType, ISchema
from yupy.isized_schema import SizedSchema
from yupy.locale import locale
from yupy.util.concat_path import concat_path
from yupy.validation_error import ErrorMessage, Constraint, ValidationError

__all__ = ('ArraySchema',)


@dataclass
class ArraySchema(SizedSchema, ComparableSchema, EqualityComparableSchema):
    _type: _SchemaExpectedType = field(init=False, default=(list, tuple))
    _fields: List[Union[ISchema, ISchemaAdapter]] = field(init=False, default_factory=list)
    _of_schema_type: Optional[Union[ISchema, ISchemaAdapter]] = field(init=False, default=None)

    def of(self, schema: Union[ISchema, ISchemaAdapter], message: ErrorMessage = locale["array_of"]) -> Self:
        if not isinstance(schema, (ISchema, ISchemaAdapter)):
            raise ValidationError(Constraint("array_of", message, type(schema)), invalid_value=schema)
        self._of_schema_type = schema
        return self

    def validate(self, value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
        value = super().validate(value, abort_early, path)
        if value is None and self._nullability:
            return None
        return self._validate_array(value, abort_early, path)  # Convert tuple to list for iteration

    def _validate_array(self, value: Union[list, tuple], abort_early: bool = True,
                        path: str = "~") -> Union[list, tuple]:
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
        return self._fields[item]
