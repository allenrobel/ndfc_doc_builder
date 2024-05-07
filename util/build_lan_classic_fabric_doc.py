#!/usr/bin/env python
"""
Print Ansible documentation for the NDFC Easy Fabric Template.

Use documentation_json to print the documentation in JSON format.
Use documentation_yaml to print the documentation in YAML format.
"""
from util.ndfc_template_doc_builder import NdfcTemplateDocBuilder
from ndfc_template_all import NdfcTemplates

# path to the template(s)
base_path = "/Users/arobel/repos/ansible_dev/dcnm_doc_builder/util/templates/12_1_3b"
fabric_template_json = f"{base_path}/LAN_Classic.json"
all_templates_json = f"{base_path}/templates.json"

doc_builder = NdfcTemplateDocBuilder()
doc_builder.template_json = fabric_template_json
doc_builder.load()

# NdfcTemplates() instance is required to get the choices for
# several parameters e.g. default_network_universal choices
# of Default_Network_Universal and Service_Network_Universal
all_template = NdfcTemplates()
all_template.template_json = all_templates_json
all_template.load()

doc_builder.template_all = all_template
doc_builder.build_documentation()
#doc_builder.documentation_json()
doc_builder.documentation_yaml()