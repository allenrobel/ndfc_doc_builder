#!/usr/bin/env python
"""
Name: ndfc_template.py
Description:

Superclass for:
    - NdfcDocBuilder()
    - NdfcTemplates()
    - NdfcTemplateRaw()
"""
import inspect
import re
import sys
import json

class NdfcTemplate:
    """
    Superclass for NdfcTemplate*() classes
    """
    def __init__(self):
        self.class_name = self.__class__.__name__
        self._init_properties()
        self._init_translation()

    def _init_properties(self):
        """
        Initialize properties used in this class.
        """
        self._template = None
        self._template_dict = None
        self._template_json_file = None

    def _init_translation(self):
        """
        -   Initialize mapping between NDFC template item parameterType
            and Ansible types.
        -   Keys: NDFC template parameterType.
        -   Values: Ansible types.
        """
        self._parameter_type_translation = {}
        self._parameter_type_translation["bool"] = "bool"
        self._parameter_type_translation["boolean"] = "bool"
        self._parameter_type_translation["BOOLEAN"] = "bool"
        self._parameter_type_translation["enum"] = "str"
        self._parameter_type_translation["int"] = "int"
        self._parameter_type_translation["integer"] = "int"
        self._parameter_type_translation["INT"] = "int"
        self._parameter_type_translation["INTEGER"] = "int"
        self._parameter_type_translation["interfaceRange"] = "str"
        self._parameter_type_translation["integerRange"] = "str"
        self._parameter_type_translation["ipAddress"] = "str"
        self._parameter_type_translation["ipAddressList"] = "str"
        self._parameter_type_translation["ipV4Address"] = "str"
        self._parameter_type_translation["ipV4AddressWithSubnet"] = "str"
        self._parameter_type_translation["ipV6Address"] = "str"
        self._parameter_type_translation["ipV6AddressWithSubnet"] = "str"
        self._parameter_type_translation["ipv4"] = "str"
        self._parameter_type_translation["ipv6"] = "str"
        self._parameter_type_translation["ipv4_subnet"] = "str"
        self._parameter_type_translation["ipv6_subnet"] = "str"
        self._parameter_type_translation["list"] = "list"
        self._parameter_type_translation["macAddress"] = "str"
        self._parameter_type_translation["str"] = "str"
        self._parameter_type_translation["string"] = "str"
        self._parameter_type_translation["string[]"] = "str"
        self._parameter_type_translation["STRING"] = "str"
        self._parameter_type_translation["structureArray"] = "list"

    @property
    def template(self):
        return self._template
    @template.setter
    def template(self, value):
        """
        The template contents supported by the subclass
        """
        self._template = value

    @property
    def template_dict(self):
        return self._template_dict
    @template_dict.setter
    def template_dict(self, value):
        """
        A dictionary containing the template contents.

        If this is set, then template_json_file will not be used.
        """
        self._template_dict = value

    @property
    def template_json_file(self):
        return self._template_json_file
    @template_json_file.setter
    def template_json_file(self, value):
        """
        Full path to a file containing the template content
        in JSON format.
        """
        self._template_json_file = value

    @staticmethod
    def delete_key(key, item:dict):
        """
        Delete key from item
        """
        if key in item:
            del item[key]
        return item

    def get_default_value_meta_properties(self, item:dict):
        """
        Return the value of metaProperties.defaultValue if present.
        Return None otherwise.
        """
        try:
            result = item["metaProperties"]["defaultValue"]
        except KeyError:
            return None
        result = self.clean_string(result)
        return result

    def get_default_value_root(self, item:dict):
        """
        Return the value of defaultValue if present.
        Return None otherwise.
        """
        try:
            result = item["defaultValue"]
        except KeyError:
            return None
        result = self.clean_string(result)
        return result

    def get_default_value(self, item:dict):
        """
        -   Return the default value for item, if it exists.
        -   Return None otherwise.
        -   The default value may reside at the following locations:
                -   item.metaProperties.defaultValue
                -   item.defaultValue
        """
        result = self.get_default_value_meta_properties(item)
        if result is not None:
            return result
        result = self.get_default_value_root(item)
        return result


    def get_description(self, item:dict):
        """
        -   Return the description of an item.
        -   item.annotations.Description
        """
        try:
            description = item['annotations']['Description']
        except KeyError:
            description = "No description available"
        description = self.clean_string(description)
        description = self.clean_description(description)
        return description

    def get_dict_value(self, item:dict, key):
        """
        -   Return value of the first instance of key found via
            recursive search of dictionary.
        -   Return None if key is not found.
        """
        if not isinstance(item, dict):
            return None
        if key in item: return item[key]
        for k, v in item.items():
            if isinstance(v,dict):
                item = self.get_dict_value(v, key)
                if item is not None:
                    return item
        return None

    def get_display_name(self, item:dict):
        """
        -   Return the NDFC GUI label for an item.
        -   item.annotations.DisplayName
        """
        result = self.get_dict_value(item, "DisplayName")
        return self.clean_string(result)

    def get_enum(self, item:dict):
        """
        -   Return the enum for an item as a list().
        -   Return an empty list if the key does not exist.
        -   item.annotations.Enum
        """
        result = self.get_dict_value(item, "Enum")
        if result is None:
            return []
        result = self.clean_string(result)
        result = result.split(",")
        try:
            result = [int(x) for x in result]
        except ValueError:
            pass
        return result

    def get_min_max(self, item:dict):
        """
        -   Return the min and max values of an item from the item's description.
        -   Return None, None otherwise.
        -   If item.annotations.Description contains "(Min: X, Max: Y)"
            return int(X), and int(Y)
        """
        result = self.get_dict_value(item, "Description")
        if result is None:
            return None, None
        # (Min:240, Max:3600)
        m = re.search(r"\(Min:\s*(\d+),\s*Max:\s*(\d+)\)", result)
        if m:
            return int(m.group(1)), int(m.group(2))
        return None, None

    def get_min(self, item:dict):
        """
        -   Return the minimum value of an item.
        -   Return None otherwise.
        -   item.metaProperties.min
        """
        result = self.get_dict_value(item, "min")
        return self.clean_string(result)

    def get_max(self, item:dict):
        """
        -   Return the maximum value of an item.
        -   Return None otherwise.
        -   item.metaProperties.max
        """
        result = self.get_dict_value(item, "max")
        return self.clean_string(result)

    def get_min_length(self, item:dict):
        """
        -   Return the minimum length of an item.
        -   Return None otherwise.
        -   item.metaProperties.minLength
        """
        result = self.get_dict_value(item, "minLength")
        return self.clean_string(result)

    def get_max_length(self, item:dict):
        """
        -   Return the maximum length of an item.
        -   Return None otherwise.
        -   item.metaProperties.maxLength
        """
        result = self.get_dict_value(item, "maxLength")
        return self.clean_string(result)

    def get_name(self, item):
        """
        -   Return the name of an item
        -   Return None otherwise.
        -   item.name
        """
        try:
            result = item['name']
        except KeyError:
            result = "unknown"
        return self.clean_string(result)

    def is_internal(self, item:dict):
        """
        -   Return True if item.annotations.IsInternal is True.
        -   Return False otherwise.
        """
        result = self.get_dict_value(item, "IsInternal")
        return self.make_bool(result)

    def is_optional(self,item):
        """
        -   Return the optional status of an item (True or False) if it exists.
        -   Return None otherwise.
        -   item.optional
        """
        result = self.make_bool(item.get('optional', None))
        return result

    def get_parameter_type(self, item:dict):
        """
        -   Translate NDFC template types to Ansible types.
        -   Return translated item.parameterType if it exists.
        -   Return None if item.parameterType does not exist.
        -   Return item.parameterType if no translation exists.
        """
        result = self.get_dict_value(item, 'parameterType')
        if result is None:
            return None
        if result in self._parameter_type_translation:
            return self._parameter_type_translation[result]
        return result

    def get_section(self, item):
        """
        -   Return the Section annotation of an item
        -   Return None otherwise.
        -   item.annotations.Section
        """
        result = self.get_dict_value(item, "Section")
        return self.clean_string(result)

    def get_template_content_type(self, item:dict):
        """
        -   Return the type of the template if it exists.
        -   Return None otherwise.
        -   item.contentType
        """
        try:
            result = item['contentType']
        except KeyError:
            result = "unknown"
        return self.clean_string(result)

    def get_template_description(self, item:dict):
        """
        -   Return the description of the template if it exists.
        -   Return None otherwise.
        -   item.description.
        """
        try:
            result = item['description']
        except KeyError:
            result = "unknown"
        return self.clean_string(result)

    def get_template_name(self, item:dict):
        """
        -   Return the name of the template if it exists.
        -   Return None otherwise.
        -   item.name
        """
        try:
            result = item['name']
        except KeyError:
            result = "unknown"
        return self.clean_string(result)

    def get_template_subtype(self, item:dict):
        """
        -   Return the subtype of the template if it exists.
        -   Return None otherwise.
        -   item.templateSubType
        """
        try:
            result = item['templateSubType']
        except KeyError:
            result = "unknown"
        return self.clean_string(result)

    def get_template_supported_platforms(self, item:dict):
        """
        -   Return the supportedPlatforms of the template if it exists.
        -   Return None otherwise.
        -   item.supportedPlatforms
        """
        try:
            result = item['supportedPlatforms']
        except KeyError:
            result = "unknown"
        return self.clean_string(result)

    def get_template_tags(self, item:dict):
        """
        -   Return the tags of the template if it exists.
        -   Return None otherwise.
        -   item.tags
        """
        try:
            result = item['tags']
        except KeyError:
            result = "unknown"
        return self.clean_string(result)

    def get_template_type(self, item:dict):
        """
        -   Return the type of the template if it exists.
        -   Return None otherwise.
        -   item.templateType
        """
        try:
            result = item['templateType']
        except KeyError:
            result = "unknown"
        return self.clean_string(result)

    def get_valid_values(self, item:dict):
        """
        -   Return the validValues annotation of an item
        -   Return None otherwise.
        -   item.metaProperties.validValues
        """
        result = self.get_dict_value(item, "validValues")
        if result is None:
            return []
        result = result.split(",")
        try:
            result = [int(x) for x in result]
        except ValueError:
            pass
        return result

    def is_mandatory(self, item:dict):
        """
        -   Return the mandatory status of item.
                -   True if the item is mandatory.
                -   False if a default value exists for item.
                -   False if item is optional.
                -   False if the IsMandatory key does not exist.
        -   item.annotations.IsMandatory
        """
        default = self.get_default_value(item)
        if default is not None or default != "":
            return False
        result = self.get_dict_value(item, "IsMandatory")
        return self.make_bool(result)

    def is_hidden(self, item:dict):
        """
        -   Return True if item.annotations.Section is "Hidden".
        -   Return False otherwise.
        -   item.annotations.Section.
        """
        result = self.get_section(item)
        if "Hidden" in result:
            return True
        return False

    def is_required(self,item:dict):
        """
        -   Return the required status of an item (True or False)
        -   Return False if the item has a default value.
        -   Return the inverse of item.optional otherwise.
        -   Return None if all else fails.
        """
        default = self.get_default_value(item)
        if default is not None or default != "":
            return False
        result = self.make_bool(item.get('optional', None))
        if result is True:
            return False
        if result is False:
            return True
        return None

    @staticmethod
    def make_bool(value):
        """
        -   Translate various string values to a boolean value.
        -   Return True if value.lower() in [true, yes]
        -   Return False if value.lower() in [false, no]
        -   Return value otherwise.
        """
        try:
            if str(value).lower() in ["true", "yes"]:
                return True
            if str(value).lower() in ["false", "no"]:
                return False
        except:
            return value
        return value

    def clean_string(self, string):
        """
        Remove unwanted characters found in various locations
        within the returned NDFC JSON.
        """
        if string is None:
            return ""
        string = string.strip()
        string = re.sub('<br />', ' ', string)
        string = re.sub('&#39;', '', string)
        string = re.sub('&#43;', '+', string)
        string = re.sub('&#61;', '=', string)
        string = re.sub('amp;', '', string)
        string = re.sub(r'\[', '', string)
        string = re.sub(r'\]', '', string)
        string = re.sub('\"', '', string)
        string = re.sub("\'", '', string)
        string = re.sub(r"\s+", " ", string)
        string = self.make_bool(string)
        if string in [True, False]:
            return string
        try:
            string = int(string)
        except ValueError:
            pass
        if not isinstance(string, int):
            try:
                string = float(string)
            except ValueError:
                pass
        return string

    def clean_description(self, string):
        """
        -   Remove (Min: x, Max: y) from string.
        -   This is sometimes found in template descriptions.
        """
        string = re.sub(r'\(Min:\s*\d+,\s* Max:\s*\d+\)', '', string)
        return string

    def load(self):
        """
        Load the template from self.template_dict if it set.
        Else, the template from the file template_json_file.
        """
        method_name = inspect.stack()[0][3]
        if self.template_dict is None and self.template_json_file is None:
            msg = f"{self.class_name}.{method_name}: "
            msg += f"Set either {self.class_name}.template_dict "
            msg += f"or {self.class_name}.template_json_file "
            msg += f"before calling {self.class_name}.{method_name}. "
            msg += f"Got self.template_dict {self.template_dict}, "
            msg += f"self.template_json_file {self.template_json_file}"
            raise ValueError(msg)
        if self.template_dict is not None:
            msg = f"{self.class_name}.{method_name}: "
            msg += "loading from template_dict. "
            print(msg)
            self.template = self.template_dict
            return
        if self.template_json_file is not None:
            msg = f"{self.class_name}.{method_name}: "
            msg += f"loading from template_json_file {self.template_json_file}"
            print(msg)
            with open(self.template_json_file, 'r', encoding="utf-8") as handle:
                self.template = json.load(handle)
