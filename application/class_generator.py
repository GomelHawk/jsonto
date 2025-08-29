from application.config import Config
from application.functions import to_camel_case, to_pascal_case, to_snake_case


class ClassGenerator:
    """
    Generate classes code for appropriate language.
    """

    def __init__(self, json_models):
        self.models = json_models
        self.config = Config()

    def generate_php_classes(self) -> dict:
        """Generate PHP classes."""
        php_classes = {}
        for model_name, properties in self.models.items():
            php_classes[model_name] = self._generate_php_class(model_name, properties)
        return php_classes

    def generate_java_classes(self) -> dict:
        """Generate Java classes."""
        java_classes = {}
        for model_name, properties in self.models.items():
            java_classes[model_name] = self._generate_java_class(model_name, properties)
        return java_classes

    def generate_python_classes(self) -> dict:
        """Generate Python classes."""
        python_classes = ["from typing import List\nfrom typing import Any\nfrom dataclasses import dataclass"]
        for model_name in list(self.models.keys())[::-1]:
            python_classes.append(self._generate_python_class(model_name, self.models[model_name]))
        return {"dataclass": "\n\n\n".join(python_classes)}

    @staticmethod
    def create_zip_response(class_dict, language_extension):
        """Save generated classes to a zip archive in-memory and return as response."""
        import zipfile
        from io import BytesIO

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for class_name, class_content in class_dict.items():
                filename = f"{class_name}.{language_extension}"
                zf.writestr(filename, class_content)

        # Reset buffer
        zip_buffer.seek(0)

        return zip_buffer

    def _generate_php_class(self, class_name: str, properties: dict):
        """Generate a PHP class."""
        class_lines = [
            "<?php declare(strict_types=1);",
            "",
            f"namespace App\\Model;",
            ""
        ]

        if self.config.php_jms_annotation:
            class_lines.append(f"use JMS\\Serializer\\Annotation as Serializer;")
            class_lines.append("")

        class_lines.append(f"final class {class_name}")
        class_lines.append(f"{{")

        for prop, (prop_type, nullable, prop_types) in properties.items():
            php_prop = to_camel_case(prop)
            php_type = self._map_to_php_type(prop_type) if prop_type != 'mixed' else self._map_to_php_type(prop_types)

            if self.config.php_old_version:
                nullable_prefix = 'null|' if nullable else ''
                class_lines.append(f"    /**")
                class_lines.append(f"     * @var {nullable_prefix}{prop_type}")
                if self.config.php_jms_annotation:
                    class_lines.append(f"     *")
                    if "array" in prop_type:
                        class_lines.append(f"     * @Serializer\\Type(\"{prop_type}\")")
                    else:
                        class_lines.append(f"     * @Serializer\\Type(\"{php_type}\")")
                    class_lines.append(f"     * @Serializer\\SerializedName(\"{prop}\")")
                class_lines.append(f"     */")
                class_lines.append(f"    public ${php_prop};")
                class_lines.append("")
            else:
                nullable_prefix = '?' if nullable else ''
                if "array" in prop_type:
                    php_type = "array"
                    class_lines.append(f"    /** @var {prop_type} */")
                    if self.config.php_jms_annotation:
                        class_lines.append(f"    #[Serializer\\Type(\"{prop_type}\")]")
                if "mixed" in prop_type and self.config.php_jms_annotation:
                    class_lines.append(f"    #[Serializer\\Type(\"{php_type}\")]")
                if self.config.php_jms_annotation:
                    class_lines.append(f"    #[Serializer\\SerializedName(\"{prop}\")]")
                class_lines.append(f"    public {nullable_prefix}{php_type} ${php_prop};")
                if self.config.php_jms_annotation:
                    class_lines.append("")

        class_lines.append("}")

        return "\n".join(class_lines)

    def _generate_java_class(self, class_name: str, properties: dict):
        """Generate a Java class."""
        class_lines = [f"public class {class_name} {{"]

        if self.config.java_use_properties:
            for prop, (prop_type, nullable, prop_types) in properties.items():
                java_prop = to_camel_case(prop)
                java_type = self._map_to_java_type(prop_type) if prop_type != 'mixed' \
                    else self._map_to_java_type(prop_types)
                class_lines.append(f"    @JsonProperty(\"{prop}\")")
                class_lines.append(f"    public {java_type} get{to_pascal_case(prop)}() {{")
                class_lines.append(f"        return this.{java_prop};")
                class_lines.append("    }}")
                class_lines.append(f"    public void set{to_pascal_case(prop)}({java_type} {java_prop}) {{")
                class_lines.append(f"        this.{java_prop} = {java_prop};")
                class_lines.append("    }}")
                class_lines.append(f"    {java_type} {java_prop};")
                class_lines.append("")
        else:
            for prop, (prop_type, nullable, prop_types) in properties.items():
                java_prop = to_camel_case(prop)
                java_type = self._map_to_java_type(prop_type) if prop_type != 'mixed' \
                    else self._map_to_java_type(prop_types)
                class_lines.append(f"    @JsonProperty(\"{prop}\")")
                class_lines.append(f"    public {java_type} {java_prop};")

        class_lines.append("}")

        return "\n".join(class_lines)

    def _generate_python_class(self, class_name: str, properties: dict):  # noqa: C901
        """Generates Python dataclass code with a from_dict method."""
        lines = ["@dataclass", f"class {class_name}:"]

        # Generate class fields
        for prop_name, (prop_type, is_nullable, _) in properties.items():
            python_prop = to_snake_case(prop_name)
            prop_type = self._map_to_python_type(prop_type)
            if is_nullable:
                prop_type = f"Optional[{prop_type}]"
            elif prop_type.startswith("array<"):
                prop_type = prop_type.replace("array<", "List[")[:-1] + "]"

            lines.append(f"    {python_prop}: {prop_type}")

        # Handle empty class
        if len(lines) == 1:
            lines.append("    pass")

        # Generate the from_dict static method
        lines.append("\n    @staticmethod")
        lines.append(f"    def from_dict(obj: Any) -> '{class_name}':")
        from_dict_lines = []

        # Create a mapping line for each property
        for prop_name, (prop_type, is_nullable, type_set) in properties.items():
            python_prop = to_snake_case(prop_name)
            prop_type = self._map_to_python_type(prop_type)
            if "array<" in prop_type:
                nested_type = prop_type[6:-1]  # Extract type from 'array<NestedType>'
                from_dict_lines.append(
                    f"        _{python_prop} = ["
                    f"{nested_type}.from_dict(item) if isinstance(item, dict) "
                    f"else item for item in obj.get('{prop_name}', [])]"
                )
            elif prop_type.startswith("Optional["):
                actual_type = prop_type[9:-1]
                if actual_type == "Any":
                    from_dict_lines.append(f"        _{python_prop} = obj.get('{prop_name}', None)")
                elif actual_type in ["str", "int", "float", "bool"]:
                    from_dict_lines.append(f"        _{python_prop} = obj.get('{prop_name}', None)")
                elif actual_type == "list":
                    from_dict_lines.append(f"        _{python_prop} = [v for v in obj.get('{prop_name}')]")
                elif actual_type in self.models:
                    from_dict_lines.append(
                        f"        _{python_prop} = {actual_type}.from_dict(obj.get('{prop_name}')) "
                        f"if obj.get('{python_prop}') is not None else None")
                else:
                    from_dict_lines.append(f"        _{python_prop} = obj.get('{prop_name}', None)")
            elif prop_type == "Any":
                from_dict_lines.append(f"        _{python_prop} = obj.get('{prop_name}')")
            elif prop_type in ["str", "int", "float", "bool"]:
                from_dict_lines.append(f"        _{python_prop} = {prop_type}(obj.get('{prop_name}'))")
            elif prop_type == "list":
                from_dict_lines.append(f"        _{python_prop} = [v for v in obj.get('{prop_name}')]")
            elif prop_type in self.models:
                from_dict_lines.append(f"        _{python_prop} = {prop_type}.from_dict(obj.get('{prop_name}'))")

        # Join the mapped properties
        lines.extend(from_dict_lines)
        lines.append(f"        return {class_name}(")
        lines.append(f"            {', '.join(f'_{to_snake_case(prop_name)}' for prop_name in properties.keys())}")
        lines.append("        )")

        return "\n".join(lines)

    def _map_to_php_type(self, prop_type) -> str:
        """Map internal types to PHP types."""
        type_map = {
            "int": "int",
            "float": "float",
            "bool": "bool",
            "string": "string",
            "array<int>": "array",
            "array<bool>": "array",
            "array<float>": "array",
            "array<string>": "array",
            "object": "object"
        }
        if isinstance(prop_type, set):
            types = [self._map_to_php_type(subtype) for subtype in prop_type]
            types.sort()
            return "|".join(types)
        return type_map.get(prop_type, prop_type)

    def _map_to_java_type(self, prop_type):
        """Map internal types to Java types."""
        type_map = {
            "int": "int",
            "float": "double",
            "bool": "boolean",
            "string": "String",
            "array<int>": "ArrayList<int>",
            "array<bool>": "ArrayList<boolean>",
            "array<float>": "ArrayList<double>",
            "array<string>": "ArrayList<String>",
            "object": "Object"
        }
        if isinstance(prop_type, set):
            types = [self._map_to_java_type(subtype) for subtype in prop_type]
            types.sort()
            return "|".join(types)
        return type_map.get(prop_type, prop_type).replace("array<", "ArrayList<")

    def _map_to_python_type(self, prop_type):
        """Map internal types to Python types."""
        type_map = {
            "int": "int",
            "float": "float",
            "bool": "bool",
            "string": "str",
            "array<int>": "list",
            "array<bool>": "list",
            "array<float>": "list",
            "array<string>": "list",
            "object": "dict",
            "mixed": "Any"
        }
        return type_map.get(prop_type, prop_type)
