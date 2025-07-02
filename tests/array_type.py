from functools import wraps
from typing import Any

from yupy import mixed, ValidationError, Constraint, ErrorMessage, locale, ISchema


# def required(schema: ISchema, message: ErrorMessage = locale['required']) -> ISchema:
#     original_validate_method = schema.validate
#     @wraps(original_validate_method)  # Wraps the previous `validate` function
#     def new_validate(value: Any = None, abort_early: bool = True, path: str = "~") -> Any:
#         if value is None:
#             raise ValidationError(Constraint("required", message), path=path, invalid_value=value)
#         return original_validate_method(value, abort_early, path)
#     schema.validate = new_validate.__get__(schema, schema.__class__)
#     return schema

try:
    s = (mixed()
         .nullable()
         .of(int)
         .one_of([1, 2, 3]))
    s.validate()
except ValidationError as exc:
    for e in exc.errors:
        print(e)
