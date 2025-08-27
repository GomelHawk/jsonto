from flask import request


class Config:
    """
    Configuration class to store classes generation preferences.
    """

    def __init__(self):
        self.common_with_prefixes = True if request.form.get("common_with_prefixes", None) == "enabled" else False
        self.php_jms_annotation = True if request.form.get("php_jms_annotation", None) == "enabled" else False
        self.php_old_version = True if request.form.get("php_old_version", None) == "enabled" else False
        self.java_use_properties = True if request.form.get("java_use_properties", None) == "enabled" else False
