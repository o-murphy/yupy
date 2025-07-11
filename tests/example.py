from yupy import string, number, array, mapping, required, ValidationError

if __name__ == "__main__":

    s = string().max(5).min(2).lowercase()
    # n = number().required().integer().ge(10).le(100).multiple_of(30)
    n = required(number().integer().ge(10).le(100).multiple_of(30))
    li = required(array().of(s).min(2))

    s.validate("ab")
    n.validate(60)

    shp = mapping().shape(
        {
            "email": required(string().email()),
            "s": s,
            "n": n,
            "shp": required(mapping()
            .shape(
                {
                    "s": s,
                    "n": n,
                    # 'li': li,
                    "o": mapping().shape({"n": li}),
                }
            ))
        }
    )

    # shp.validate({'s': "ab", 'n': 60})
    try:
        shp.validate(
            {
                "email": "a@gmail.com",
                "s": "wd",
                "n": 60,
                "shp": {"n": "a", "li": ["ab", "b"], "o": {"n": ["g", "g"]}},
            }, False
        )
    except ValidationError as err:

        for e in err.errors:
            print("Violation:")
            print(f"\tPath\t:\t{e.path}")
            print(f"\tValue\t:\t{e.invalid_value!r}")
            print(f"\tReason\t:\t{e.constraint.format_message}")


    # m = mixed().one_of(['G1', 'G7'])
    # m.validate('F')

    def check():
        try:
            shp.validate(
                {
                    "email": "a@gmail.com",
                    "s": "wd",
                    "n": 60,
                    "shp": {"n": "a", "li": ["ab", "b"], "o": {"n": ["g", "g"]}},
                }, False
            )
        except ValidationError as err:
            print(err)


    from timeit import timeit

    print(timeit(check, number=100000))
