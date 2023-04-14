from main import generate_table


def test_one():
    data = [
        {
            "a": [{"d": 10, "e": 15},  {"d": 30, "e": 40}],
            "b": 2,
            "c": [{"d": 13, "e": 20}, {"d": 100, "e": 70}],
        },
        {
            "a": [{"d": 12, "e": 17}],
            "b": 5,
            "c": [{"d": 13, "e": 20}, {"d": 100, "e": 70}],
        },
        {
            "a": [{"d": 13, "e": 20}, {"d": 100, "e": 70}],
            "b": 8,
            "c": [{"d": 13, "e": 20}, {"d": 100, "e": 70}],
        }
    ]
    schema = [{
        "a": {
            "type": [
                {
                    "d": {
                        "type": "integer",
                        "header": "d",
                    },
                    "e": {
                        "type": "integer",
                        "header": "e",
                    }
                },
                ],
            "header": "a",

        },
        "b": {
            "type": "integer",
            "header": "b",
        },
        "c": {
            "type": [
                {
                    "d": {
                        "type": "integer",
                        "header": "d",
                    },
                    "e": {
                        "type": "integer",
                        "header": "e",
                    }
                },
            ],
            "header": "a",

        }
    }]
    expected = [
        ["a", None, "b", "c", None],
        ["d", "e", None, "d", "e"],
        [10, 15, 2, 13, 20],
        [30, 40, None, 100, 70],
        [12, 17, 5, 13, 20],
        [None, None, None, 100, 70],
        [13, 20, 8, 13, 20],
        [100, 70, None, 100, 70],
    ]
    assert generate_table(data, schema) == expected
