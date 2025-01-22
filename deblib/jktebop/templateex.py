"""
Subclass of string.Template which extends it be allowing the definition
of a placeholder's name and default value in the form `${name|default}`
"""
from typing import Dict
from string import Template
import re

class TemplateEx(Template):
    """
    Subclass of string.Template which extends it be allowing the definition
    of a placeholder's name and default value in the form `${name|default}`
    """

    def __init__(self, template):
        """
        Initializes a new instance of this Template; parsing the template text for placeholders with
        default values (of the form ${name:default}) to record the default values to be used.
        """
        # The regex pattern for placeholders with default should look something like this;
        #       \${(?:(?P<name>(?a:[_a-z][_a-z0-9]*))\|(?P<default>[^}]*))}
        # matches only on placeholders like ${name|default} and captures the groups name and default
        delim = fr"\{Template.delimiter}" if Template.delimiter == "$" else Template.delimiter
        with_defs_pattern = re.compile(
            fr"{delim}{{(?:(?P<name>{Template.idpattern})\|(?P<default>[^}}]*))}}",
            re.IGNORECASE | re.VERBOSE)

        # First extract the details of any defaults
        self._defaults = { }
        for mo in with_defs_pattern.finditer(template):
            name = mo.group("name")
            if name is not None and name not in self._defaults:
                self._defaults[name] = mo.group("default") or ""

        # Update the template to remove the custom syntax for defaults; from ${name:def} to S{name}
        template = with_defs_pattern.sub(fr"{Template.delimiter}{{\g<name>}}", template)
        super().__init__(template)

    @classmethod
    def get_template_identifiers(cls, template: Template):
        """
        This is based on a copy of get_identifiers(self) found on newer versions of Template.
        Here it's renamed and implemented as a classmethod so it can be used with any Template.
        """
        get_identifiers = getattr(template, "get_identifiers", None)
        if get_identifiers:
            return get_identifiers()

        ids = []
        for mo in template.pattern.finditer(template.template):
            named = mo.group('named') or mo.group('braced')
            if named is not None and named not in ids:
                # add a named group only the first time it appears
                ids.append(named)
            elif (named is None
                and mo.group('invalid') is None
                and mo.group('escaped') is None):
                # If all the groups are None, there must be
                # another group we're not expecting
                raise ValueError('Unrecognized named group in pattern', template.pattern)
        return ids

    def get_identifiers_and_defaults(self) -> Dict[str, any]:
        """
        Gets the identifiers from this template in a Dict with any associated default values
        """
        ids = TemplateEx.get_template_identifiers(self)
        return { i: self._defaults.get(i, None) for i in ids }
