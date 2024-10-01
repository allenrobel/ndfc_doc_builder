#!/usr/bin/env python
"""
Write an NDFC template to a file.

Usage:

To write the list of all templates to a file:

./ndfc_template_save.py --template templates

To write a specific template to a file (in this case aaa_radius):

./ndfc_template_save.py --template aaa_radius
"""
from ndfc_get_template import NdfcGetTemplate
from ndfc import NDFC
from optparse import OptionParser
import sys
from ansible_collections.cisco.dcnm.plugins.module_utils.common.log_v2 import \
    Log

template_dir = "/Users/arobel/repos/ansible_dev/ndfc_doc_builder/util/templates/321e"

parser = OptionParser()
parser.add_option("-t", "--template", dest="template_name",
                  help=f"Name of the template to save (will be saved in {template_dir})",
                  metavar="TEMPLATE_NAME")

(options, args) = parser.parse_args()
if options.template_name is None:
    parser.error("Need a template name. E.g. --template aaa_radius")
    sys.exit(1)

# Logging setup
try:
    log = Log()
    log.commit()
except ValueError as error:
    print(error)
    sys.exit(1)
ndfc = NDFC()
ndfc.verb = "GET"
ndfc.login()

template = NdfcGetTemplate()
template.ndfc = ndfc
template.template = options.template_name
template.filename = f"{template_dir}/{template.template}.json"
template.get_template()
template.write_template()
