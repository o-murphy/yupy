from dataclasses import dataclass, field
from typing import Any, Iterable

from typing_extensions import Self

from yupy.ischema import _SchemaExpectedType
from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ErrorMessage, Constraint, ValidationError

__all__ = ('MixedSchema',)


@dataclass
class MixedSchema(Schema):
    _type: _SchemaExpectedType = field(default=object)

    def one_of(self, items: Iterable, message: ErrorMessage = locale['one_of']) -> Self:
        """
        Adds a validation to check if the value is one of the provided items.
        """

        def _(x: Any) -> None:
            if x not in items:
                raise ValidationError(Constraint('one_of', message, items), invalid_value=x)

        return self.test(_)
