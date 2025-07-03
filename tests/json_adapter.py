from yupy import json, mapping, number

s = json(
    mapping().shape({
        "a": number()
    }), json_parser='orjson'
)

print(s.validate('{"a": 0}'))

# print(s.validate('{"a": "b"}'))
print(s.validate("\\s"))
