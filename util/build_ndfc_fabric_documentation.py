#!/usr/bin/env python
"""
This script is used to build the documentation from NDFC templates.

### Usage

1. Set shell variables

```shell
export NDFC_USERNAME="my_username" # defaults to admin
export NDFC_PASSWORD="my_password"
export NDFC_IP4="10.1.1.1"
export NDFC_DOMAIN=local # defaults to local
```

2. Edit this script to change the template_name variable to the desired template name.

3. Edit this script to change the other variables as needed e.g.:
    - module_author
    - module_name
    - module_states
    - module_default_state

4. Run the script from the top-level of this repo

```shell
cd $HOME/repos/ndfc_doc_builder
./util/build_ndfc_fabric_documentation.py
```
"""
from util.ndfc_doc_builder import NdfcDocBuilder
from util.ndfc_templates import NdfcTemplates
from ansible_collections.cisco.dcnm.plugins.module_utils.common.response_handler import \
    ResponseHandler
from ansible_collections.cisco.dcnm.plugins.module_utils.common.rest_send_v2 import \
    RestSend
from ansible_collections.cisco.dcnm.plugins.module_utils.common.sender_requests import \
    Sender
from ansible_collections.cisco.dcnm.plugins.module_utils.fabric.template_get import \
    TemplateGet
from ansible_collections.cisco.dcnm.plugins.module_utils.fabric.template_get_all import \
    TemplateGetAll

def get_template_all():
    instance = TemplateGetAll()
    instance.rest_send = rest_send
    instance.refresh()
    return instance.templates

def get_template(template_name):
    instance = TemplateGet()
    instance.rest_send = rest_send
    instance.template_name = template_name
    instance.refresh()
    return instance.template

template_name = "Easy_Fabric"
sender = Sender()
sender.login()
rest_send = RestSend({})
rest_send.response_handler = ResponseHandler()
rest_send.sender = sender

print("Retrieving all templates")
template_all_dict = get_template_all()
print(f"Retrieving template {template_name}")
template_dict = get_template(template_name)

doc_builder = NdfcDocBuilder()
doc_builder.template_dict = template_dict

# NdfcTemplates() instance is required to get the choices for
# several parameters e.g. default_network_universal choices
# of Default_Network_Universal and Service_Network_Universal
ndfc_templates_instance = NdfcTemplates()
ndfc_templates_instance.template_dict = template_all_dict
ndfc_templates_instance.load()

doc_builder.template_all = ndfc_templates_instance
doc_builder.module_author = "Allen Robel (@quantumonion)"
doc_builder.module_name = "dcnm_fabric"
doc_builder.module_states = ["deleted", "merged", "query", "replaced"]
doc_builder.module_default_state = "merged"
print("Building documentation")
doc_builder.commit()
print("Printing documentation")
#doc_builder.documentation_json()
doc_builder.documentation_yaml()
