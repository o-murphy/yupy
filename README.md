# YuPy - Python Schema Validation Library

## Dead simple object schema validation for Python
*Inspired by [**yup js library**](https://github.com/jquense/yup)*

YuPy is a schema builder for runtime value parsing and validation. Define a schema, transform a value to match, assert the shape of an existing value, or both. YuPy schemas are extremely expressive and allow modeling complex, interdependent validations or value transformations.

---

## 🔧 Features

- ✅ Schema-based validation: strings, numbers, arrays, dictionaries
- 🔍 Type checking
- ❓ Nullability control (`None`)
- 🔄 Value transformation
- 🧪 Custom validators
- 🧾 Detailed error reporting
- 🌐 Locale support
- 🔌 Built-in adapters: `default`, `required`, `immutable`
- 📏 Comparison and size constraints
- 🔁 Mixed types and Union schema support

---

## 📦 Installation

```bash
pip install yupy
```

---

## 🚀 Usage

### Basic validation

```python
from yupy import string, number

string().min(3).max(10).validate("hello")  # ✅
number().positive().integer().validate(42)  # ✅
```

### Nullability

```python
string().nullable().validate(None)  # ✅
```

### Arrays

```python
from yupy import array

array().of(string().min(2)).min(1).validate(["ok", "yes"])
```

### Dictionaries (Mappings)

```python
from yupy import mapping

user_schema = mapping().shape({
    "name": string().min(3),
    "age": number().ge(18)
})
```

### Union

```python
from yupy import union

union().one_of([string(), number()]).validate("hello")
union().one_of([string(), number()]).validate(10)
```

---

## 🧩 Adapters

### required

```python
from yupy import required

required(string().min(3)).validate("abc")
```

### default

```python
from yupy import default

default("N/A", string()).validate(None)  # → "N/A"
```

### immutable

```python
from yupy import immutable

immutable(string()).validate("data")  # -> creates deep copy
```

---

## 📘 API Reference

### Base

```python
nullable(self) -> Self
not_nullable(self, message: ErrorMessage) -> Self
test(self, func: ValidatorFunc) -> Self
const(self, value: Optional[_SchemaExpectedType], message: ErrorMessage) -> Self
transform(self, func: TransformFunc) -> Self
```

### Sized

```python
length(self, limit: int, message: ErrorMessage) -> Self
min(self, limit: int, message: ErrorMessage) -> Self
max(self, limit: int, message: ErrorMessage) -> Self
```

### Comparable

```python
le(self, limit: Any, message: ErrorMessage) -> Self
ge(self, limit: Any, message: ErrorMessage) -> Self
lt(self, limit: Any, message: ErrorMessage) -> Self
gt(self, limit: Any, message: ErrorMessage) -> Self
```

### StringSchema

```python
email(self, message: ErrorMessage) -> Self
url(self, message: ErrorMessage) -> Self
uuid(self, message: ErrorMessage) -> Self
matches(self, regex: re.Pattern, message: ErrorMessage, exclude_empty: bool = False) -> Self
lowercase(self, message: ErrorMessage) -> Self
uppercase(self, message: ErrorMessage) -> Self
ensure(self) -> Self
```

### NumberSchema

```python
positive(self, message: ErrorMessage) -> Self
negative(self, message: ErrorMessage) -> Self
integer(self, message: ErrorMessage) -> Self
multiple_of(self, multiplier: Union[int, float], message: ErrorMessage) -> Self
```

### ArraySchema

```python
of(self, schema: Union[ISchema, ISchemaAdapter], message: ErrorMessage) -> Self
```

### MappingSchema

```python
shape(self, fields: _SchemaShape) -> Self
strict(self, is_strict: bool = True, message: ErrorMessage) -> Self
```

### MixedSchema

```python
of(self, type_or_types: _SchemaExpectedType, message: ErrorMessage) -> Self
one_of(self, items: Iterable, message: ErrorMessage) -> Self
```

### UnionSchema

```python
one_of(self, options: UnionOptionsType, message: ErrorMessage) -> Self
```

---

## 🛠 Extending

### Custom Validator

```python
from yupy import string, ValidationError

def is_palindrome(value):
    if value != value[::-1]:
        raise ValidationError("Not a palindrome")

string().test(is_palindrome).validate("madam")
```

---

## ✅ Running Tests

```bash
pytest
```

---

## 🤝 Contributing

Contributions are welcome! Please open issues or submit pull requests.

---

## 📄 License

MIT License  
Copyright (c)