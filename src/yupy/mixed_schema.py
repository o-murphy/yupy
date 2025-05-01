from typing import Any, Type

from yupy.locale import locale
from yupy.schema import Schema
from yupy.validation_error import ErrorMessage, Constraint, ValidationError

__all__ = ('MixedSchema',)


class MixedSchema(Schema[Any]):  # Inherit with explicit Any for _T
    _type: Type[Any] = Any

    def one_of(self, items: list[Any], message: ErrorMessage = locale['one_of']) -> 'Self':
        """
        Adds a validation to check if the value is one of the provided items.
        """

        def _(x: Any) -> None:
            if x not in items:
                raise ValidationError(
                    Constraint(
                        'one_of',
                        items,
                        message
                    )
                )

        return self.test(_)
