# YuPy - Python Schema Validation Library

## Dead simple object schema validation for Python

[![license]][LGPL-3]
[![pypi]][PyPiUrl]
[![pypi-pre]][pypi-pre-url]
[![py-versions]][sources]
[![Test](https://github.com/o-murphy/yupy/actions/workflows/pytest.yml/badge.svg)](https://github.com/o-murphy/yupy/actions/workflows/pytest.yml)
[![Ruff](https://github.com/o-murphy/yupy/actions/workflows/mypy.yml/badge.svg)](https://github.com/o-murphy/yupy/actions/workflows/mypy.yml)
[![Mypy](https://github.com/o-murphy/yupy/actions/workflows/ruff.yml/badge.svg)](https://github.com/o-murphy/yupy/actions/workflows/ruff.yml)
[![coverage]][coverage]
[![downloads]][pepy]
[![downloads/month]][pepy]
[![Made in Ukraine]][SWUBadge]

[sources]:
https://github.com/o-murphy/yupy

[license]:
https://img.shields.io/github/license/o-murphy/yupy

[LGPL-3]:
https://opensource.org/licenses/MIT

[pypi]:
https://img.shields.io/pypi/v/yupy?logo=pypi

[PyPiUrl]:
https://pypi.org/project/yupy/

[pypi-pre]:
https://img.shields.io/github/v/release/o-murphy/yupy?include_prereleases&logo=pypi&label=pypi%20pre

[pypi-pre-url]:
https://pypi.org/project/yupy/#history

[downloads]:
https://img.shields.io/pepy/dt/yupy

[downloads/month]:
https://static.pepy.tech/personalized-badge/yupy?period=month&units=abbreviation&left_color=grey&right_color=blue&left_text=downloads%2Fmonth

[pepy]:
https://pepy.tech/project/yupy

[py-versions]:
https://img.shields.io/pypi/pyversions/yupy?style=flat-square

[coverage]:
./coverage.svg

[Made in Ukraine]:
https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7&style=flat-square

[SWUBadge]:
https://stand-with-ukraine.pp.ua

*Inspired by [**yup js library**](https://github.com/jquense/yup)*

YuPy is a schema builder for runtime value parsing and validation. Define a schema, transform a value to match, assert
the shape of an existing value, or both. YuPy schemas are extremely expressive and allow modeling complex,
interdependent validations or value transformations.

---

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
    - [Basic validation](#basic-validation)
    - [Nullability](#nullability)
    - [Arrays](#arrays)
    - [Dictionaries (Mappings)](#dictionaries-mappings)
    - [Union](#union)
- [Adapters](#-adapters)
    - [required](#required)
    - [default](#default)
    - [immutable](#immutable)
- [API Reference](#-api-reference)
    - [Base Schema](#base-schema)
    - [Sized Schema](#sized-schema)
    - [Comparable Schema](#comparable-schema)
    - [String Schema](#string-schema)
    - [Number Schema](#number-schema)
    - [Array Schema](#array-schema)
    - [Mapping Schema](#mapping-schema)
    - [Mixed Schema](#mixed-schema)
    - [Union Schema](#union-schema)
- [Extending](#-extending)
- [Running Tests](#-running-tests)
- [Contributing](#-contributing)
- [License](#-license)

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

### Base Schema

**Inheritance:** `Schema` (implements `ISchema`)

Base class for all schema types providing core validation functionality.

| Method                                                                   | Description                                            |
|--------------------------------------------------------------------------|--------------------------------------------------------|
| `nullable() -> Self`                                                     | Makes the schema accept `None` values                  |
| `not_nullable(message: ErrorMessage = None) -> Self`                     | Explicitly disallows `None` values with custom message |
| `test(func: ValidatorFunc) -> Self`                                      | Adds a custom validation function                      |
| `const(value: Any, message: ErrorMessage = None) -> Self`                | Validates that the value equals a constant             |
| `transform(func: TransformFunc) -> Self`                                 | Adds a transformation function                         |
| `validate(value: Any, abort_early: bool = True, path: str = "~") -> Any` | Validates the value against the schema                 |

### Sized Schema

**Inheritance:** `Schema` → `SizedSchema` (implements `ISizedSchema`)

Provides size-based validation methods for sequences and collections.

| Method                                                     | Description              |
|------------------------------------------------------------|--------------------------|
| `length(limit: int, message: ErrorMessage = None) -> Self` | Validates exact length   |
| `min(limit: int, message: ErrorMessage = None) -> Self`    | Validates minimum length |
| `max(limit: int, message: ErrorMessage = None) -> Self`    | Validates maximum length |

### Comparable Schema

**Inheritance:** `Schema` → `ComparableSchema` (implements `IComparableSchema`)

Provides comparison-based validation methods.

| Method                                                 | Description                                |
|--------------------------------------------------------|--------------------------------------------|
| `le(limit: Any, message: ErrorMessage = None) -> Self` | Validates value ≤ limit                    |
| `ge(limit: Any, message: ErrorMessage = None) -> Self` | Validates value ≥ limit                    |
| `lt(limit: Any, message: ErrorMessage = None) -> Self` | Validates value < limit                    |
| `gt(limit: Any, message: ErrorMessage = None) -> Self` | Validates value > limit                    |
| `eq(value: Any, message: ErrorMessage = None) -> Self` | Validates value equals specified value     |
| `ne(value: Any, message: ErrorMessage = None) -> Self` | Validates value not equals specified value |

### String Schema

**Inheritance:** `Schema` → `SizedSchema`, `ComparableSchema`, `EqualityComparableSchema` → `StringSchema`

Validates string values with text-specific methods.

| Method                                                                                          | Description                                  |
|-------------------------------------------------------------------------------------------------|----------------------------------------------|
| `email(message: ErrorMessage = None) -> Self`                                                   | Validates email format                       |
| `url(message: ErrorMessage = None) -> Self`                                                     | Validates URL format                         |
| `uuid(message: ErrorMessage = None) -> Self`                                                    | Validates UUID format                        |
| `matches(regex: re.Pattern, message: ErrorMessage = None, exclude_empty: bool = False) -> Self` | Validates against regex pattern              |
| `lowercase(message: ErrorMessage = None) -> Self`                                               | Validates string is lowercase                |
| `uppercase(message: ErrorMessage = None) -> Self`                                               | Validates string is uppercase                |
| `ensure() -> Self`                                                                              | Transforms empty/null values to empty string |

### Number Schema

**Inheritance:** `Schema` → `ComparableSchema`, `EqualityComparableSchema` → `NumberSchema`

Validates numeric values (int, float) with number-specific methods.

| Method                                                                             | Description                                     |
|------------------------------------------------------------------------------------|-------------------------------------------------|
| `positive(message: ErrorMessage = None) -> Self`                                   | Validates number > 0                            |
| `negative(message: ErrorMessage = None) -> Self`                                   | Validates number < 0                            |
| `integer(message: ErrorMessage = None) -> Self`                                    | Validates number is integer (no decimals)       |
| `multiple_of(multiplier: Union[int, float], message: ErrorMessage = None) -> Self` | Validates number is multiple of specified value |

### Array Schema

**Inheritance:** `Schema` → `SizedSchema`, `ComparableSchema`, `EqualityComparableSchema` → `ArraySchema`

Validates list and tuple values.

| Method                                                                             | Description                                 |
|------------------------------------------------------------------------------------|---------------------------------------------|
| `of(schema: Union[ISchema, ISchemaAdapter], message: ErrorMessage = None) -> Self` | Validates all array elements against schema |

### Mapping Schema

**Inheritance:** `Schema` → `EqualityComparableSchema` → `MappingSchema`

Validates dictionary/mapping values with object shape validation.

| Method                                                                 | Description                          |
|------------------------------------------------------------------------|--------------------------------------|
| `shape(fields: Dict[str, Union[ISchema, ISchemaAdapter]]) -> Self`     | Defines the expected shape/structure |
| `strict(is_strict: bool = True, message: ErrorMessage = None) -> Self` | Disallows unknown keys when True     |

### Mixed Schema

**Inheritance:** `Schema` → `EqualityComparableSchema` → `MixedSchema`

Validates values of any type with flexible type checking.

| Method                                                                         | Description                                   |
|--------------------------------------------------------------------------------|-----------------------------------------------|
| `of(type_or_types: _SchemaExpectedType, message: ErrorMessage = None) -> Self` | Validates value is of specified type(s)       |
| `one_of(items: Iterable, message: ErrorMessage = None) -> Self`                | Validates value is one of the specified items |

### Union Schema

**Inheritance:** `Schema` → `EqualityComparableSchema` → `UnionSchema`

Validates values that can match one of multiple schemas.

| Method                                                                                        | Description                                                  |
|-----------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| `one_of(options: List[Union[ISchema, ISchemaAdapter]], message: ErrorMessage = None) -> Self` | Validates value matches at least one of the provided schemas |

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

### Custom Adapter

```python
from yupy import SchemaAdapter, string


class CustomAdapter(SchemaAdapter):
    def validate(self, value, abort_early=True, path="~"):
        # Custom logic before validation
        result = super().validate(value, abort_early, path)
        # Custom logic after validation
        return result


# Usage
custom = CustomAdapter(string().min(3))
custom.validate("hello")
```

---

## ✅ Running Tests

```bash
pytest
```

---

## 🤝 Contributing

Contributions are welcome! Please open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License  
Copyright (c) YuPy Contributors