#!/usr/bin/env python
"""
# Name: ndfc_template_save.py

# Description

Save NDFC template parameters to a file.

# Usage

./ndfc_template_save.py \
    --template Easy_Fabric \
    --filename Easy_Fabric.json \
    --filepath /path/where/filename/is/saved

# Caveats

All paths below are relative to the DCNM Ansible Collection top-level directory.

1.  Currently, Templates() class in plugins/module_utils/common/api/... limits
    template names to a specific set defined in 
    plugins/module_utils/common/fabric/fabric_types.py.
    This script will exit with error if the template name is not in that set.
    This will be fixed in a future release.
    
    The current set of allowed templates is:
    - Easy_Fabric
    - Easy_Fabric_IPFM
    - External_Fabric
    - LAN_Classic
    - MSD_Fabric
"""
import inspect
import json
import sys
from optparse import OptionParser

from ansible_collections.cisco.dcnm.plugins.module_utils.common.response_handler import \
    ResponseHandler
from ansible_collections.cisco.dcnm.plugins.module_utils.common.rest_send_v2 import \
    RestSend
from ansible_collections.cisco.dcnm.plugins.module_utils.common.sender_requests import \
    Sender
from ansible_collections.cisco.dcnm.plugins.module_utils.common.log_v2 import \
    Log
from ansible_collections.cisco.dcnm.plugins.module_utils.fabric.template_get import \
    TemplateGet

class TemplateSave(TemplateGet):
    def __init__(self):
        super().__init__()
        self.class_name = self.__class__.__name__
        self._filepath = None
        self._filename = None

    def write_template(self):
        method_name = inspect.stack()[0][3]
        if self.filepath is None:
            msg = f"{self.class_name}.{method_name}"
            msg += f"set {self.class_name}.filepath "
            msg += f"before calling {self.class_name}.{method_name}"
            raise ValueError(msg)
        if self.filename is None:
            msg = f"{self.class_name}.{method_name}"
            msg += f"set {self.class_name}.filename "
            msg += f"before calling {self.class_name}.{method_name}"
            raise ValueError(msg)
        if self.filepath[-1] == "/":
            file = f"{self.filepath}{self.filename}"
        else:
            file = f"{self.filepath}/{self.filename}"
        self.log.debug(f"Writing template to {file}")
        with open(file, "w") as fn:
            fn.write(json.dumps(self.template))

    @property
    def filepath(self):
        return self._filepath
    @filepath.setter
    def filepath(self, value):
        self._filepath = value

    @property
    def filename(self):
        return self._filename
    @filename.setter
    def filename(self, value):
        self._filename = value


parser = OptionParser()
parser.add_option("-t", "--template", dest="template_name",
                  help=f"Name of the template to save e.g. aaa_radius",
                  metavar="TEMPLATE_NAME")
parser.add_option("-f", "--filename", dest="filename",
                  help=f"Name of the file in which template will be saved. e.g. aaa_radius.json",
                  metavar="FILENAME")
parser.add_option("-p", "--filepath", dest="filepath",
                  help=f"Path where filename will be saved e.g. /path/where/filename/is/saved",
                  metavar="FILEPATH")

(options, args) = parser.parse_args()
if options.template_name is None:
    parser.error("Need a template name. E.g. --template aaa_radius")
    sys.exit(1)
if options.filename is None:
    parser.error("Need a file name. E.g. --filename aaa_radius.json")
    sys.exit(1)
if options.filepath is None:
    parser.error("Need a directory path. E.g. --filepath /path/where/filename/is/saved")
    sys.exit(1)

# Logging setup
try:
    log = Log()
    log.commit()
except ValueError as error:
    print(error)
    sys.exit(1)

# RestSend setup
sender = Sender()
sender.login()
rest_send = RestSend({})
rest_send.response_handler = ResponseHandler()
rest_send.sender = sender

# Save the template
instance = TemplateSave()
instance.rest_send = rest_send
instance.template_name = options.template_name
instance.refresh()
instance.filename = options.filename
instance.filepath = options.filepath
instance.write_template()
