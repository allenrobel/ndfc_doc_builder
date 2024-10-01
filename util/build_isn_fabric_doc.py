#!/usr/bin/env python
"""
Print Ansible documentation for the NDFC LAN_Classic Template.

Use documentation_json to print the documentation in JSON format.
Use documentation_yaml to print the documentation in YAML format.
"""
from util.ndfc_doc_builder import NdfcDocBuilder
from util.ndfc_templates import NdfcTemplates

# path to the template(s)
base_path = "/Users/arobel/repos/ansible_dev/ndfc_doc_builder/util/templates/321e"
fabric_template_json = f"{base_path}/External_Fabric.json"
all_templates_json = f"{base_path}/templates.json"

doc_builder = NdfcDocBuilder()
doc_builder.template_json = fabric_template_json

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