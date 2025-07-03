from .adapters import *
from .array_schema import *
from .icomparable_schema import *
from .ischema import *
from .isized_schema import *
from .locale import *
from .mapping_schema import *
from .mixed_schema import *
from .number_schema import *
from .schema import *
from .string_schema import *
from .union_schema import *
from .validation_error import *

string = StringSchema
number = NumberSchema
mapping = MappingSchema
array = ArraySchema
mixed = MixedSchema
union = UnionSchema

immutable = SchemaImmutableAdapter
default = SchemaDefaultAdapter
required = SchemaRequiredAdapter
json = SchemaJsonAdapter

__all__ = (
    'ErrorMessage',
    'ValidatorFunc',
    'ValidationError',
    'Constraint',

    'Schema',
    'StringSchema',
    'NumberSchema',
    'MappingSchema',
    'ArraySchema',
    'MixedSchema',
    'UnionSchema',

    'ISchema',
    'IComparableSchema',
    'ComparableSchema',
    'IEqualityComparableSchema',
    'EqualityComparableSchema',
    'ISizedSchema',
    'SizedSchema',

    'ISchemaAdapter',
    'SchemaAdapter',
    'SchemaJsonAdapter',
    'SchemaDefaultAdapter',
    'SchemaRequiredAdapter',
    'SchemaImmutableAdapter',
    '_REQUIRED_UNDEFINED_',

    'string',
    'number',
    'mapping',
    'array',
    'mixed',
    'union',

    'immutable',
    'required',
    'default',
    'json',

    'locale',
    'set_locale',

    'util',
)
