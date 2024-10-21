import json
import inflect
from application.config import Config


class JSONParser:
    """
    Parse JSON object to the dictionary structure:
        key => model name
        value => tuple with base model type (str), nullable (bool) and set of possible types (set)
    """

    def __init__(self):
        self.models = {}
        self.config = Config()
        self.base_types = {"int", "string", "bool", "float"}

    @staticmethod
    def detect_type(value) -> str:
        """Detect the data type."""
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            # Handle arrays of objects and base types
            detected_types = {JSONParser.detect_type(v) for v in value if v is not None}
            if len(detected_types) == 1:
                return f"array<{detected_types.pop()}>"
            else:
                return "array<mixed>"
        elif isinstance(value, dict):
            return "object"
        else:
            raise ValueError(f"Unknown type for value '{value}'.")

    def _merge_property(self, model_name: str, key: str, new_type: str, is_nullable: bool):
        """Merge a property into the existing model structure, handling type conflicts."""
        if key in self.models[model_name]:
            # If the model exists, merge the types and update nullable status
            existing_type, existing_nullable, type_set = self.models[model_name][key]
            new_nullable = existing_nullable or is_nullable

            # Check for conflict between base type and object/array
            if (existing_type not in self.base_types and new_type in self.base_types) or \
                    (new_type not in self.base_types and existing_type in self.base_types):
                raise ValueError(f"Type conflict for key '{key}': cannot combine '{existing_type}' with '{new_type}'.")

            # If the types differ, add both to the set of types
            if new_type != existing_type:
                type_set.add(new_type)

            # If there are multiple base types, set the main type as 'mixed'
            if len(type_set) > 1 and (existing_type in self.base_types or new_type in self.base_types):
                existing_type = 'mixed'

            self.models[model_name][key] = (existing_type, new_nullable, type_set)
        else:
            # Add new model property
            self.models[model_name][key] = (new_type, is_nullable, {new_type})

    def parse_model(self, obj, minimized_obj, model_name: str = "RootModel") -> dict:
        """Parse a given object and update the model data."""
        if model_name not in self.models:
            self.models[model_name] = {}

        for key, value in obj.items():
            # If no value and the model exists, update nullable status
            if value is None and key in self.models[model_name]:
                existing_type, existing_nullable, type_set = self.models[model_name][key]
                self._merge_property(model_name, key, existing_type, True)
                continue

            detected_type = self.detect_type(value)
            is_nullable = key not in minimized_obj  # Mark nullable if the key is not in minimized JSON

            if detected_type == "object" and isinstance(value, dict):
                # Recursively parse nested objects (sub-models)
                sub_model_name = f"{model_name}{key.capitalize()}" if self.config.common_with_prefixes \
                    else key.capitalize()
                minimized_sub_obj = minimized_obj.get(key, {})
                self.parse_model(value, minimized_sub_obj, sub_model_name)
                current_type = sub_model_name
            elif detected_type == "array<object>" and isinstance(value, list) and len(value) > 0:
                # Detect arrays of objects and create a nested model class for them
                sub_model_name = f"{model_name}{key.capitalize()}" if self.config.common_with_prefixes \
                    else key.capitalize()
                # Use inflect to create singular noun for the model name (in case list of elements)
                sub_model_name_singular = inflect.engine().singular_noun(sub_model_name)
                sub_model_name = sub_model_name_singular if sub_model_name_singular else sub_model_name
                # Process each object in the array and merge its structure
                for element in value:
                    if isinstance(element, dict):
                        minimized_sub_obj = minimized_obj.get(key, [{}])
                        self.parse_model(element, minimized_sub_obj[0], sub_model_name)
                current_type = f"array<{sub_model_name}>"
            else:
                current_type = detected_type

            # Merge this property into the model
            self._merge_property(model_name, key, current_type, is_nullable if value is not None else True)

        return self.models


def parse_json_structures(full_json_string: str, minimized_json_string: str) -> tuple:
    """
    Main function to parse and merge two JSON versions into a single model.
    Returns dictionary and error message in case error.
    """
    parser = JSONParser()

    # Do nothing if main JSON is empty
    if full_json_string.split() == '':
        return dict(), None

    # Because minimized JSON is optional
    minimized_json_string = full_json_string if minimized_json_string.strip() == '' else minimized_json_string

    try:
        # Load the full and minimized JSON
        full_json = json.loads(full_json_string)
        minimized_json = json.loads(minimized_json_string)

        # Merge both structures into a single model data (dictionary)
        merged_models_dict = parser.parse_model(full_json, minimized_json)

        return merged_models_dict, None
    except (json.JSONDecodeError, AttributeError):
        return dict(), "Error: JSON parsing error"
    except ValueError as e:
        return dict(), f"Error: {e}"
