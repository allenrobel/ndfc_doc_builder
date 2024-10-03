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
    """
    - ### Build Ansible documentation in YAML format from an NDFC template.

    - ### Can also dump the documentation as a JSON document.

    - Example shell setup

      In your shell environment, set the following environment variables:

      ```shell
      export NDFC_IP4=10.1.1.1
      export NDFC_USERNAME=my_username
      export NDFC_PASSWORD=my_password
      export NDFC_DOMAIN=local
      ```

    - Example script
    ```python
        from util.ndfc_doc_builder import NdfcDocBuilder
        from util.ndfc_templates import NdfcTemplates

        # path to the template(s)
        base_path = "/Users/arobel/repos/ansible_dev/ndfc_doc_builder/util/templates/12_1_3b"
        fabric_template_json_file = f"{base_path}/LAN_Classic.json"
        all_templates_json = f"{base_path}/templates.json"

        doc_builder = NdfcDocBuilder()
        doc_builder.template_json_file = fabric_template_json
        # OR use template_dict to pass a python dictionary representation of the template
        # doc_builder.template_dict = <template dictionary>

        # NdfcTemplates() instance is required to get the choices for
        # several parameters e.g. default_network_universal choices
        # of Default_Network_Universal and Service_Network_Universal
        all_template = NdfcTemplates()
        all_template.template_json = all_templates_json
        all_template.load()

        doc_builder.template_all = all_template
        doc_builder.module_author = "Allen Robel (@quantumonion)"
        doc_builder.module_name = "dcnm_fabric"
        doc_builder.module_states = ["deleted", "merged", "query", "replaced"]
        doc_builder.module_default_state = "merged"
        doc_builder.commit()
        #doc_builder.documentation_json()
        doc_builder.documentation_yaml()
    ```
    """
    def __init__(self):
        self.class_name = self.__class__.__name__
        self.ndfc_template = NdfcTemplate()
        self.suboptions = None
        self._valid_ansible_states = ["deleted", "merged", "overridden", "query", "replaced"]
        self._init_properties()
        self._init_documentation()

    def _init_properties(self):
        self._module_name = None
        self._module_author = None
        self._module_default_state = None
        self._module_states = None
        self._template_all = None
    def _init_documentation(self):
        self.documentation = {}
        self.documentation["options"] = {}

    @property
    def module_author(self):
        """
        The author of the module.  e.g. jimi_hendrix (@jimi)

        getter: return module_name
        setter: set module_name

        Mandatory
        """
        return self._module_author
    @module_author.setter
    def module_author(self, value):
        self._module_author = value

    @property
    def module_name(self):
        """
        The name of the module.  e.g. dcnm_fabric.

        getter: return module_name
        setter: set module_name

        Mandatory
        """
        return self._module_name
    @module_name.setter
    def module_name(self, value):
        self._module_name = value

    @property
    def module_default_state(self):
        """
        The default Ansible state for the module.

        -   getter: return the default Ansible state.
        -   setter: set the default Ansible state.
        -   setter: raise ``ValueError`` if module_default_state is not
            a valid Ansible state.
        -   Mandatory
        """
        return self._module_default_state

    @module_default_state.setter
    def module_default_state(self, value):
        if value not in self._valid_ansible_states:
            msg = f"Invalid Ansible state {value}. "
            msg += f"Expected one of {','.join(sorted(self._valid_ansible_states))}"
            raise ValueError(msg)
        self._module_default_state = value

    @property
    def module_states(self):
        """
        A python list of Ansible states support by the module.

        Example
        ```python
        instance.module_states = ["deleted", "merged", "query", "replaced"]
        ```

        -   getter: return module_states
        -   setter: set module_states
        -   setter: raise ``ValueError`` if module_states is not a list()
        -   setter: raise ``ValueError`` if any of the states in the list()
                    is not a valid Ansible state.
        -   Mandatory
        """
        return self._module_states
    @module_states.setter
    def module_states(self, value):
        if not isinstance(value, list):
            msg = "Expected list() for instance.module_states. "
            msg += f"Got: {type(value).__name__}."
            raise ValueError(msg)
        for item in value:
            if item in self._valid_ansible_states:
                continue
            msg = f"Invalid Ansible state {item}. "
            msg += f"Expected one of {','.join(sorted(self._valid_ansible_states))}"
            raise ValueError(msg)
        self._module_states = value

    @property
    def template_all(self):
        """
        An instance of NdfcTemplateAll()
        """
        return self._template_all
    @template_all.setter
    def template_all(self, value):
        self._template_all = value

    @property
    def template_dict(self):
        """
        Template content as a python dictionary.
        """
        return self._template_dict
    @template_dict.setter
    def template_dict(self, value):
        self._template_dict = value


    def init_translation(self):
        """
        ### Summary
        Builds a dictionary which maps between NDFC's expected
        parameter names and the corresponding playbook names.

        For example

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

        if self.template_dict is None:
            msg = "exiting. call instance.template_dict first."
            print(f"{msg}")
            sys.exit(1)

        self.ndfc_template.template_dict = self.template_dict
        self.ndfc_template.load()

        self.init_translation()

    def add_module_name(self):
        method_name = inspect.stack()[0][3]
        if self.module_name is None:
            msg = f"{self.class_name}.{method_name}: "
            msg += f"Call {self.class_name}.module_name before calling "
            msg += f"{self.class_name}.commit()"
            raise ValueError(msg)
        self.documentation["module"] = self.module_name

    def add_module_author(self):
        method_name = inspect.stack()[0][3]
        if self.module_author is None:
            msg = f"{self.class_name}.{method_name}: "
            msg += f"Call {self.class_name}.module_author before calling "
            msg += f"{self.class_name}.commit()"
            raise ValueError(msg)
        self.documentation["author"] = self.module_author

    def add_module_state(self):
        method_name = inspect.stack()[0][3]
        if self.module_states is None:
            msg = f"{self.class_name}.{method_name}: "
            msg += f"Call {self.class_name}.module_states before calling "
            msg += f"{self.class_name}.commit()"
            raise ValueError(msg)
        if self.module_default_state is None:
            msg = f"{self.class_name}.{method_name}: "
            msg = f"Call {self.class_name}.module_default_state before calling "
            msg += f"{self.class_name}.commit()"
            raise ValueError(msg)
        self.documentation["options"]["state"] = {}
        self.documentation["options"]["state"]["description"] = []
        value = "The state of DCNM after module completion"
        self.documentation["options"]["state"]["description"].append(value)
        # states = [f"I({x})" for x in self.module_states]
        self.documentation["options"]["state"]["type"] = "str"
        self.documentation["options"]["state"]["choices"] = self.module_states
        self.documentation["options"]["state"]["default"] = self.module_default_state

    def add_module_description(self):
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
        self.add_module_description()
        self.add_module_state()
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
                    choices = self.template_all.get_template_names_by_tag(tag)
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
