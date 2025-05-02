import re
from dataclasses import field, dataclass

from yupy.ischema import _SchemaExpectedType
from yupy.locale import locale
from yupy.schema import Schema
from yupy.sized_mixin import SizedMixin
from yupy.validation_error import ErrorMessage, ValidationError, Constraint

__all__ = ('StringSchema',)

rUUID_pattern = re.compile(
    r"^(?:[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}|00000000-0000-0000-0000-000000000000)$",
    re.IGNORECASE,
)

rEmail_pattern = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
    re.IGNORECASE,
)

rUrl_pattern = re.compile(
    r"^((https?|ftp):)?//(((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[ -퟿豈-﷏ﷰ-￯])|(([a-z]|\d|[ -퟿豈-﷏ﷰ-￯])([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])*([a-z]|\d|[ -퟿豈-﷏ﷰ-￯])))\.)+(([a-z]|[ -퟿豈-﷏ﷰ-￯])|(([a-z]|[ -퟿豈-﷏ﷰ-￯])([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])*([a-z]|[ -퟿豈-﷏ﷰ-￯])))\.?)(:\d*)?)(/((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)+(/(([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)|[-]|/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)|/|\?)*)?$",
    re.IGNORECASE,
)


@dataclass
class StringSchema(Schema[str], SizedMixin[str]):
    _type: _SchemaExpectedType = field(init=False, default=str)

    # def matches(self, regex: re.Pattern, message: ErrorMessage, exclude_empty: bool = False) -> Schema:
    #     def _(x: str):
    #         if not re.match(regex, x):
    #             raise ValidationError(message)
    #     self._validators.append(_)
    #     return self

    def email(self, message: ErrorMessage = locale["email"]) -> 'Schema[str]':
        def _(x: str) -> None:
            if not re.match(rEmail_pattern, x):
                raise ValidationError(Constraint("email", None, message))

        return self.test(_)

    def url(self, message: ErrorMessage = locale["url"]) -> 'Schema[str]':
        def _(x: str) -> None:
            if not re.match(rUrl_pattern, x):
                raise ValidationError(Constraint("url", None, message))

        return self.test(_)

    def uuid(self, message: ErrorMessage = locale["uuid"]) -> 'Schema[str]':
        def _(x: str) -> None:
            if not re.match(rUUID_pattern, x):
                raise ValidationError(Constraint("uuid", None, message))

        return self.test(_)

    # def datetime(self, message: ErrorMessage, precision: int, allow_offset: bool = False):
    #     def _(x: str):
    #         if ...:
    #             raise ValidationError(message)
    #     self._validators.append(_)
    #     return self

    def ensure(self) -> 'Schema[str]':
        def _(x: str) -> str:
            return x if x else ""

        self._transforms.append(_)
        return self

    # def trim(self, message: ErrorMessage):
    #     ...

    def lowercase(self, message: ErrorMessage = locale["lowercase"]) -> 'Schema[str]':
        def _(x: str) -> None:
            if x.lower() != x:
                raise ValidationError(Constraint("lowercase", None, message))

        return self.test(_)

    def uppercase(self, message: ErrorMessage = locale["uppercase"]) -> 'Schema[str]':
        def _(x: str) -> None:
            if x.upper() != x:
                raise ValidationError(Constraint("uppercase", None, message))

        return self.test(_)
