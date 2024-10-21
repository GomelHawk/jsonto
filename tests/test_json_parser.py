import pytest
from app import create_app
from application.json_parser import parse_json_structures

json_full = '''
{
    "name": "John Doe",
    "age": 30,
    "contact": {
        "email": "john@example.com",
        "phone": "123456789"
    },
    "addresses": [
        {"street": "123 Main St", "city": "New York"},
        {"street": "456 Elm St", "city": null}
    ]
}
'''

json_minimal = '''
{
    "name": "Jane Doe",
    "contact": {
        "email": "jane@example.com"
    },
    "addresses": [
        {"street": "789 Oak St"}
    ]
}
'''

expected_model = {
    'RootModel': {
        'name': ('string', False, {'string'}),
        'age': ('int', True, {'int'}),
        'contact': ('Contact', False, {'Contact'}),
        'addresses': ('array<Address>', False, {'array<Address>'})
    },
    'Contact': {
        'email': ('string', False, {'string'}),
        'phone': ('string', True, {'string'})
    },
    'Address': {
        'street': ('string', False, {'string'}),
        'city': ('string', True, {'string'})
    }
}

json_mixed_nullable = '''
{
    "data": [
        {
            "type": 1
        },
        {
            "type": "asd",
            "option": true
        }
    ]
}
'''

expected_model_mixed_nullable = {
    'RootModel': {
        'data': ('array<Datum>', False, {'array<Datum>'})
    },
    'Datum': {
        'type': ('mixed', False, {'string', 'int'}),
        'option': ('bool', True, {'bool'})
    }
}


# Test parsing logic.
@pytest.mark.parametrize("json_full_data, json_minimal_data, expected_output", [
    (json_full, json_minimal, expected_model),
    (json_mixed_nullable, json_mixed_nullable, expected_model_mixed_nullable)
])
def test_json_model_parser(json_full_data: str, json_minimal_data: str, expected_output: dict):
    app = create_app()

    # Define context to prevent Config generation error (request is needed).
    with app.test_request_context('/'):
        # Parse the JSON data
        parsed_structure = parse_json_structures(json_full_data, json_minimal_data)[0]

        # Assert that the parsed structure matches the expected output
        assert parsed_structure == expected_output, f"Failed parsing: {parsed_structure}"
