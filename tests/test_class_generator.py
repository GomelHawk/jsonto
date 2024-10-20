import pytest
from app import create_app
from application.class_generator import ClassGenerator

parsed_model = {
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
        'city': ('string', True, {'string'}),
        'code': ('mixed', False, {'int', 'string'}),
    }
}

expected_php_classes = {
    'RootModel': '''<?php declare(strict_types=1);

namespace App\\Model\\RootModel;

final class RootModel {
    public string $name;
    public ?int $age;
    public Contact $contact;
    /** @var array<Address> */
    public array $addresses;
}
''',

    'Contact': '''<?php declare(strict_types=1);

namespace App\\Model\\Contact;

final class Contact {
    public string $email;
    public ?string $phone;
}
''',

    'Address': '''<?php declare(strict_types=1);

namespace App\\Model\\Address;

final class Address {
    public string $street;
    public ?string $city;
    public int|string $code;
}
'''
}

expected_java_classes = {
    'RootModel': '''public class RootModel {
    public String name;
    public int age;
    public Contact contact;
    public ArrayList<Address> addresses;
}
''',

    'Contact': '''public class Contact {
    public String email;
    public String phone;
}
''',

    'Address': '''public class Address {
    public String street;
    public String city;
    public String|int code;
}
'''
}

expected_python_classes = {
    'dataclass': '''from typing import List
from typing import Any
from dataclasses import dataclass


@dataclass
class Address:
    street: str
    city: Optional[str]
    code: Any

    @staticmethod
    def from_dict(obj: Any) -> 'Address':
        _street = str(obj.get('street'))
        _city = str(obj.get('city'))
        _code = obj.get('code')
        return Address(
            _street, _city, _code
        )


@dataclass
class Contact:
    email: str
    phone: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> 'Contact':
        _email = str(obj.get('email'))
        _phone = str(obj.get('phone'))
        return Contact(
            _email, _phone
        )


@dataclass
class RootModel:
    name: str
    age: Optional[int]
    contact: Contact
    addresses: List[Address]

    @staticmethod
    def from_dict(obj: Any) -> 'RootModel':
        _name = str(obj.get('name'))
        _age = int(obj.get('age'))
        _contact = Contact.from_dict(obj.get('contact'))
        _addresses = [Address.from_dict(item) if isinstance(item, dict) else item for item in obj.get('addresses', [])]
        return RootModel(
            _name, _age, _contact, _addresses
        )
'''
}


# Test classes generation for all languages.
@pytest.mark.parametrize("language, expected_classes", [
    ("php", expected_php_classes),
    ("python", expected_python_classes),
    ("java", expected_java_classes),
])
def test_class_generator(language, expected_classes):
    app = create_app()

    # Define context to prevent Config generation error (request is needed).
    with app.test_request_context('/'):
        # Initialize the ClassGenerator
        generator = ClassGenerator(parsed_model)

        # Generate classes based on the parsed model
        generated_classes = getattr(generator, f"generate_{language}_classes")()

        # Check if the generated classes match the expected output for each class
        for class_name, expected_code in expected_classes.items():
            assert generated_classes[class_name] == expected_code.strip(), \
                f"Failed for {class_name} in {language}"
