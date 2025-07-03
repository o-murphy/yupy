import re
from dataclasses import field, dataclass
from datetime import date

from typing_extensions import Self

from yupy.icomparable_schema import ComparableSchema, EqualityComparableSchema
from yupy.ischema import _SchemaExpectedType
from yupy.isized_schema import SizedSchema
from yupy.locale import locale, ErrorMessage
from yupy.validation_error import ValidationError, Constraint

__all__ = ('StringSchema',)

rUUID_pattern = re.compile(
    r"^(?:[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}|00000000-0000-0000-0000-000000000000)$",
    re.IGNORECASE,
)
"""
Regular expression pattern for validating UUIDs (versions 1-5) and the null UUID.
The validation is case-insensitive.
"""

rEmail_pattern = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
    re.IGNORECASE,
)
"""
Regular expression pattern for validating email addresses.
The validation is case-insensitive.
"""

rUrl_pattern = re.compile(
    r"^((https?|ftp):)?//(((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[ -퟿豈-﷏ﷰ-￯])|(([a-z]|\d|[ -퟿豈-﷏ﷰ-￯])([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])*([a-z]|\d|[ -퟿豈-﷏ﷰ-￯])))\.)+(([a-z]|[ -퟿豈-﷏ﷰ-￯])|(([a-z]|[ -퟿豈-﷏ﷰ-￯])([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])*([a-z]|[ -퟿豈-﷏ﷰ-￯])))\.?)(:\d*)?)(/((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)+(/(([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)|[-]|/|\?)*)?(#((([a-z]|\d|-|\.|_|~|[ -퟿豈-﷏ﷰ-￯])|(%[\da-f]{2})|[!$&'()*+,;=]|:|@)|/|\?)*)?$",
    re.IGNORECASE,
)
"""
Regular expression pattern for validating URLs.
The validation is case-insensitive.
"""


@dataclass
class StringSchema(SizedSchema, ComparableSchema, EqualityComparableSchema):
    """
    A schema for validating string values with various constraints.

    This schema extends `SizedSchema` for length-based validations,
    `ComparableSchema` for comparison operations, and
    `EqualityComparableSchema` for equality checks. It provides methods
    for regex matching, specific format validation (email, URL, UUID),
    case enforcement, and ensuring non-empty strings.

    Attributes:
        _type (_SchemaExpectedType): The expected Python type for the schema's value.
            Initialized to `str`.
    """
    _type: _SchemaExpectedType = field(init=False, default=str)

    def matches(self, regex: re.Pattern, message: ErrorMessage = locale["matches"],
                exclude_empty: bool = False) -> Self:
        """
        Adds a validation rule to ensure the string matches a given regular expression pattern.

        Args:
            regex (re.Pattern): The compiled regular expression pattern to match.
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "matches".
            exclude_empty (bool): If True, an empty string will not trigger this
                validation rule and will be considered valid for this specific check.
                Defaults to False.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if exclude_empty and not x:
                return

            if not re.match(regex, x):
                raise ValidationError(Constraint("matches", message, regex.pattern), invalid_value=x)

        return self.test(_)

    def email(self, message: ErrorMessage = locale["email"]) -> Self:
        """
        Adds a validation rule to ensure the string is a valid email address format.

        This method uses the pre-compiled `rEmail_pattern` for validation.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "email".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if not re.match(rEmail_pattern, x):
                raise ValidationError(Constraint("email", message), invalid_value=x)

        return self.test(_)

    def url(self, message: ErrorMessage = locale["url"]) -> Self:
        """
        Adds a validation rule to ensure the string is a valid URL format.

        This method uses the pre-compiled `rUrl_pattern` for validation.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "url".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if not re.match(rUrl_pattern, x):
                raise ValidationError(Constraint("url", message), invalid_value=x)

        return self.test(_)

    def uuid(self, message: ErrorMessage = locale["uuid"]) -> Self:
        """
        Adds a validation rule to ensure the string is a valid UUID format.

        This method uses the pre-compiled `rUUID_pattern` for validation,
        which includes support for UUID versions 1-5 and the null UUID.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "uuid".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if not re.match(rUUID_pattern, x):
                raise ValidationError(Constraint("uuid", message), invalid_value=x)

        return self.test(_)

    # # FIXME
    # def datetime(self, message: ErrorMessage = locale["datetime"], precision: Optional[Literal[0, 3, 6]] = None,
    #              allow_offset: bool = True) -> Self:
    #     """
    #     Adds a validation rule to ensure the string is a valid ISO 8601 datetime.
    #
    #     This method attempts to parse the string using `datetime.datetime.fromisoformat()`.
    #     It also supports optional validation for fractional second precision and control over timezone offsets.
    #
    #     Args:
    #         message (ErrorMessage): The error message to use if the validation fails.
    #             Defaults to the locale-defined message for "datetime".
    #         precision (Optional[Literal[0, 3, 6]]): If specified, validates the fractional
    #             second precision of the datetime string.
    #             - `0`: No fractional seconds (e.g., `YYYY-MM-DDTHH:MM:SS`).
    #             - `3`: Milliseconds precision (e.g., `YYYY-MM-DDTHH:MM:SS.mmm`).
    #             - `6`: Microseconds precision (e.g., `YYYY-MM-DDTHH:MM:SS.mmmmmm`).
    #             If `None`, any valid precision is allowed.
    #         allow_offset (bool): If `False`, disallows timezone offsets (e.g., `Z`, `+01:00`).
    #             If `True`, allows them. Defaults to `True`.
    #
    #     Returns:
    #         Self: The schema instance, allowing for method chaining.
    #
    #     Raises:
    #         ValueError: If an invalid `precision` value (not 0, 3, 6, or None) is provided
    #             during schema definition.
    #     """
    #     if precision is not None and precision not in [0, 3, 6]:
    #         raise ValueError("Invalid precision value. Must be 0, 3, 6, or None.")
    #
    #     def _(x: str) -> None:
    #         # Check for strict ISO 8601 format (must contain 'T' separator for datetime)
    #         # We need to be more specific: if the string looks like a datetime but uses space instead of 'T'
    #         if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', x):
    #             raise ValidationError(Constraint("datetime", message), invalid_value=x)
    #
    #         try:
    #             dt_obj = datetime.fromisoformat(x)
    #         except ValueError:
    #             raise ValidationError(Constraint("datetime", message), invalid_value=x)
    #
    #         # Validate offset presence based on allow_offset
    #         if not allow_offset and dt_obj.tzinfo is not None:
    #             raise ValidationError(Constraint("datetime", message), invalid_value=x)
    #
    #         # Validate fractional second precision
    #         if precision is not None:
    #             actual_microseconds = dt_obj.microsecond
    #             if precision == 0:  # No fractional seconds allowed
    #                 if actual_microseconds != 0:
    #                     raise ValidationError(Constraint("datetime", message), invalid_value=x)
    #             elif precision == 3:  # Milliseconds allowed (0-3 significant digits)
    #                 # Check if there are non-zero digits beyond milliseconds (i.e., microsecond % 1000 != 0)
    #                 # For example, 0.123456 seconds has 123456 microseconds.
    #                 # If precision=3, we only want 123000. So 123456 should fail.
    #                 # `actual_microseconds % 1000 != 0` correctly identifies this.
    #                 if actual_microseconds % 1000 != 0:
    #                     raise ValidationError(Constraint("datetime", message), invalid_value=x)
    #             # For precision == 6, fromisoformat handles up to 6 digits, so no further check needed.
    #
    #     return self.test(_)

    def date(self, message: ErrorMessage = locale["date"]) -> Self:
        """
        Adds a validation rule to ensure the string is a valid ISO 8601 date (YYYY-MM-DD).

        This method attempts to parse the string using `datetime.date.fromisoformat()`.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "date".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            try:
                # datetime.date.fromisoformat only accepts YYYY-MM-DD format
                # It will raise ValueError for any time components or invalid formats.
                date.fromisoformat(x)
            except ValueError:
                raise ValidationError(Constraint("date", message), invalid_value=x)

        return self.test(_)

    def ensure(self) -> Self:
        """
        Adds a transformation to ensure that if the string value is falsy (e.g., empty string),
        it is transformed into an empty string `""`.

        This is useful for normalizing values where `None` or other falsy values
        should be treated as an empty string.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> str:
            return x if x else ""

        self._transforms.append(_)
        return self

    def trim(self) -> Self:
        """
        Adds a transformation to remove leading and trailing whitespace from the string.

        This transformation uses Python's built-in `str.strip()` method.

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> str:
            return x.strip()

        self._transforms.append(_)
        return self

    def lowercase(self, message: ErrorMessage = locale["lowercase"]) -> Self:
        """
        Adds a validation rule to ensure the string contains only lowercase characters.

        The validation checks if the string is identical to its lowercase version.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "lowercase".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if x.lower() != x:
                raise ValidationError(Constraint("lowercase", message), invalid_value=x)

        return self.test(_)

    def uppercase(self, message: ErrorMessage = locale["uppercase"]) -> Self:
        """
        Adds a validation rule to ensure the string contains only uppercase characters.

        The validation checks if the string is identical to its uppercase version.

        Args:
            message (ErrorMessage): The error message to use if the validation fails.
                Defaults to the locale-defined message for "uppercase".

        Returns:
            Self: The schema instance, allowing for method chaining.
        """

        def _(x: str) -> None:
            if x.upper() != x:
                raise ValidationError(Constraint("uppercase", message), invalid_value=x)

        return self.test(_)
