#!/usr/bin/env python
"""
Name: ndfc_template_all.py

Description:

Retrieve and process previously-stored list of NDFC templates.

The stored JSON should have been retieved from the following URL:

https://<ndfc_ip>/appcenter/cisco/ndfc/api/v1/configtemplate/rest/config/templates #noqa
"""
import inspect
import sys
from ndfc_template import NdfcTemplate

class NdfcTemplates(NdfcTemplate):
    def __init__(self):
        super().__init__()
        self.class_name = self.__class__.__name__

    def get_template_names_by_tag(self, tag):
        """
        return a list of template names that match tag
        """
        method_name = inspect.stack()[0][3]
        if self.template is None:
            msg = f"{self.class_name}.{method_name}: "
            msg += f"Call {self.class_name}.load() before calling "
            msg += f"{self.class_name}.{method_name}"
            raise ValueError(msg)
        template_name_list = []
        for template_name in self.template:
            tags = self.template[template_name].get("tags", None)
            if tags is None:
                continue
            tags = self.clean_string(tags)
            tags = tags.split(",")
            tags = [x.strip() for x in tags]
            if tag not in tags:
                continue
            template_name_list.append(self.template[template_name].get("name", None))
        return template_name_list



