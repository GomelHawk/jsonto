import pytest

from application.functions import to_camel_case, to_pascal_case, to_snake_case


@pytest.mark.parametrize("input_str, expected", [
    ("snake_case", "snakeCase"),
    ("kebab-case", "kebabCase"),
    ("camelCase", "camelCase"),
    ("PascalCase", "pascalCase"),
    ("HTTPRequest", "httpRequest"),
    ("ParserForXML", "parserForXml"),
    ("userIDNumber", "userIdNumber"),
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
    ("HTTPRequest", "HttpRequest"),
    ("ParserForXML", "ParserForXml"),
    ("userIDNumber", "UserIdNumber"),
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
    ("HTTPRequest", "http_request"),
    ("ParserForXML", "parser_for_xml"),
    ("userIDNumber", "user_id_number"),
    ("mixedUp_Case-Name", "mixed_up_case_name"),
    ("", ""),
])
def test_to_snake_case(input_str, expected):
    assert to_snake_case(input_str) == expected
