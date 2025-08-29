import pytest

from application.functions import to_camel_case, to_pascal_case, to_snake_case


@pytest.mark.parametrize("input_str, expected", [
    ("snake_case", "snakeCase"),
    ("kebab-case", "kebabCase"),
    ("camelCase", "camelCase"),
    ("PascalCase", "pascalCase"),
    ("mixedUp_Case-Name", "mixedUpCaseName"),
    ("", ""),
])
def test_to_camel_case(input_str, expected):
    assert to_camel_case(input_str) == expected


@pytest.mark.parametrize("input_str, expected", [
    ("snake_case", "SnakeCase"),
    ("kebab-case", "KebabCase"),
    ("camelCase", "CamelCase"),
    ("PascalCase", "PascalCase"),
    ("mixedUp_Case-Name", "MixedUpCaseName"),
    ("", ""),
])
def test_to_pascal_case(input_str, expected):
    assert to_pascal_case(input_str) == expected


@pytest.mark.parametrize("input_str, expected", [
    ("snake_case", "snake_case"),
    ("kebab-case", "kebab_case"),
    ("camelCase", "camel_case"),
    ("PascalCase", "pascal_case"),
    ("mixedUp_Case-Name", "mixed_up_case_name"),
    ("", ""),
])
def test_to_snake_case(input_str, expected):
    assert to_snake_case(input_str) == expected
