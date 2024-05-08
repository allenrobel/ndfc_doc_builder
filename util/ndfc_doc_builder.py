#!/usr/bin/env python
"""
Name: ndfc_template_easy_fabric.py
Description:

Generate documetation from previously-stored NDFC EasyFabric template.

The stored JSON should have been retieved via the following URL:

https://<ndfc_ip>/appcenter/cisco/ndfc/api/v1/configtemplate/rest/config/templates/Easy_Fabric #noqa
"""
import inspect
import json
import sys
import yaml
from util.ndfc_template import NdfcTemplate

class NdfcDocBuilder:
    def __init__(self):
        self.class_name = self.__class__.__name__
        self.ndfc_template = NdfcTemplate()
        self.suboptions = None
        self._init_properties()
        self._init_documentation()

    def _init_properties(self):
        self._properties = {}
        self._properties["module_name"] = None
        self._properties["module_author"] = None

    @property
    def module_author(self):
        """
        The author of the module.  e.g. jimi_hendrix (@jimi)

        getter: return module_name
        setter: set module_name

        Mandatory
        """
        return self._properties["module_author"]
    @module_author.setter
    def module_author(self, value):
        self._properties["module_author"] = value


    @property
    def module_name(self):
        """
        The name of the module.  e.g. dcnm_fabric.

        getter: return module_name
        setter: set module_name

        Mandatory
        """
        return self._properties["module_name"]
    @module_name.setter
    def module_name(self, value):
        self._properties["module_name"] = value

    @property
    def template_all(self):
        return self._properties["template_all"]
    @template_all.setter
    def template_all(self, value):
        """
        An instance of NdfcTemplateAll()
        """
        self._properties["template_all"] = value

    @property
    def template_json(self):
        return self._properties["template_json"]
    @template_json.setter
    def template_json(self, value):
        """
        Full path to a file containing the template content
        in JSON format
        """
        self._properties["template_json"] = value

    def _init_documentation(self):
        self.documentation = {}

    def init_translation(self):
        """
        Builds a dictionary which maps between NDFC's expected
        parameter names and the corresponding playbook names.
        e.g.:
        DEAFULT_QUEUING_POLICY_CLOUDSCALE -> DEFAULT_QUEUING_POLICY_CLOUDSCALE

        The dictionary excludes hidden and internal parameters.
        """
        if self.ndfc_template is None:
            msg = "exiting. call instance.ndfc_template() first."
            print(f"{msg}")
            sys.exit(1)

        if self.ndfc_template.template is None:
            msg = "exiting. call instance.ndfc_template.load_template() first."
            print(f"{msg}")
            sys.exit(1)
        self.translation = {}
        typo_keys = {
            "DEAFULT_QUEUING_POLICY_CLOUDSCALE": "DEFAULT_QUEUING_POLICY_CLOUDSCALE",
            "DEAFULT_QUEUING_POLICY_OTHER": "DEFAULT_QUEUING_POLICY_OTHER",
            "DEAFULT_QUEUING_POLICY_R_SERIES": "DEFAULT_QUEUING_POLICY_R_SERIES",
        }
        for item in self.ndfc_template.template.get("parameters"):
            if self.ndfc_template.is_internal(item):
                continue
            if self.ndfc_template.is_hidden(item):
                continue
            name = self.ndfc_template.get_name(item)
            if not name:
                continue
            if name in typo_keys:
                self.translation[name] = typo_keys[name]
                continue

    def validate_base_prerequisites(self):
        """
        1. Validate that the prerequisites are met before proceeding.
            Specifically:
            - User has set self.template
            - User has set self.template_all
        2. Call self.init_translation() if self.translation is None
        """

        if self.template_json is None:
            msg = "exiting. call instance.template_json first."
            print(f"{msg}")
            sys.exit(1)

        self.ndfc_template.template_json = self.template_json
        self.ndfc_template.load()

        self.init_translation()


    def add_module_name(self):
        method_name = inspect.stack()[0][3]
        if self.module_name is None:
            msg = "module_name must be set before calling commit()"
            raise ValueError(msg)
        self.documentation["module"] = self.module_name

    def add_module_author(self):
        method_name = inspect.stack()[0][3]
        if self.module_author is None:
            msg = "module_author must be set before calling commit()"
            raise ValueError(msg)
        self.documentation["author"] = self.module_author

    def module_description(self):
        self.documentation["description"] = []
        self.documentation["description"].append(
            "Manage creation and configuration of NDFC fabrics."
        )
        # self.documentation["description"].append(
        #     self.get_template_description(self.template)
        # )

    def commit(self):
        """
        Build the documentation for the template.
        """
        self.validate_base_prerequisites()
        if self.template_all is None:
            msg = "exiting. call instance.template_all first."
            print(f"{msg}")
            sys.exit(1)
        self.add_module_name()
        self.add_module_author()
        self.module_description()
        self.documentation["options"] = {}
        self.documentation["options"]["state"] = {}
        self.documentation["options"]["state"]["description"] = []
        value = "The state of DCNM after module completion"
        self.documentation["options"]["state"]["description"].append(value)
        value = "I(deleted), I(merged), and I(query) states are supported."
        self.documentation["options"]["state"]["description"].append(value)
        self.documentation["options"]["state"]["type"] = "str"
        self.documentation["options"]["state"]["choices"] = ["deleted", "merged", "query", "replaced"]
        self.documentation["options"]["state"]["default"] = "merged"
        self.documentation["options"]["config"] = {}
        self.documentation["options"]["config"]["description"] = []
        value = "A list of fabric configuration dictionaries"
        self.documentation["options"]["config"]["description"].append(value)
        self.documentation["options"]["config"]["type"] = "list"
        self.documentation["options"]["config"]["elements"] = "dict"
        self.documentation["options"]["config"]["suboptions"] = {}

        suboptions = {}
        for item in self.ndfc_template.template.get("parameters"):
            if self.ndfc_template.is_internal(item):
                continue
            if self.ndfc_template.is_hidden(item):
                continue
            if not item.get('name', None):
                continue
            name = self.translation.get(item['name'], item['name'])
            suboptions[name] = {}
            suboptions[name]["description"] = []
            description = self.ndfc_template.get_description(item)
            if description is None or description == "":
                description = "No description available"
            # ndfc_label = self.get_display_name(item)
            # ndfc_section = self.get_section(item)
            # min_value, max_value = self.get_min_max(item)
            # if min_value is not None:
            #     suboptions[name]["min"] = min_value
            # if max_value is not None:
            #     suboptions[name]["max"] = max_value
            suboptions[name]["description"].append(description)
            # if ndfc_label is not None:
            #     suboptions[name]["description"].append(f"ndfc_label, {ndfc_label}")
            # if ndfc_section is not None:
            #     suboptions[name]["description"].append(f"ndfc_section, {ndfc_section}")
            suboptions[name]["type"] = self.ndfc_template.get_parameter_type(item)
            suboptions[name]["required"] = self.ndfc_template.is_required(item)
            default = self.ndfc_template.get_default_value(item)
            if default is not None:
                suboptions[name]["default"] = default
            choices  = self.ndfc_template.get_enum(item)
            if len(choices) > 0:
                if "TEMPLATES" in str(choices[0]):
                    tag = str(choices[0]).split(".")[1]
                    choices = self.template_all.get_templates_by_tag(tag)
                suboptions[name]["choices"] = choices

        self.documentation["options"]["config"]["suboptions"] = {}
        for key in sorted(suboptions.keys()):
            self.documentation["options"]["config"]["suboptions"][key] = suboptions[key]

    def documentation_yaml(self):
        """
        Dump the documentation in YAML format
        """
        if self.documentation is None:
            msg = "Call instance.commit() before calling instance.documentation_yaml()"
            raise ValueError(msg)
        print(yaml.dump(self.documentation, indent=4))

    def documentation_json(self):
        """
        Dump the documentation in JSON format
        """
        if self.documentation is None:
            msg = "Call instance.commit() before calling instance.documentation_json()"
            raise ValueError(msg)
        print(json.dumps(self.documentation, indent=4))
