"""
Subclass of string.Template which extends it be allowing the definition
of a placeholder's name and default value in the form `${name|default}`
"""
from typing import Dict
from string import Template
import re
from collections import ChainMap as _ChainMap

# Used as a default for substitute mapping arg so we know if it's not set
_sentinel_dict = { }

class TemplateEx(Template):
    """
    Subclass of string.Template which extends it be allowing the definition
    of a placeholder's name and default value in the form `${name|default}`
    """

    def __init_subclass__(cls):
        # The regex pattern for placeholders with a defined default, in the form
        # ${name|default} or ${name|}, with capture groups for name and default
        delim = fr"\{Template.delimiter}" if Template.delimiter == "$" else Template.delimiter
        cls.pattern_for_defaults = re.compile(
            fr"{delim}{{(?:(?P<name>{Template.idpattern})\|(?P<default>[^}}]*))}}",
            cls.flags | re.VERBOSE)

    def __init__(self, template):
        """
        Initializes a new instance of this TemplateEx; parsing the template text
        for placeholders with default values (of the form ${name|default}) to
        record the default values to be applied on substitute when not set.
        """
        self._defaults = { }

        if isinstance(template, str):
            # Find and store the details of any placeholders with defaults
            for mo in self.pattern_for_defaults.finditer(template):
                name = mo.group("name")
                if name is not None and name not in self._defaults:
                    self._defaults[name] = mo.group("default") or ""

            # Update the template to remove custom syntax for defaults; from ${name|def} to S{name}
            template = self.pattern_for_defaults.sub(fr"{Template.delimiter}{{\g<name>}}", template)
        super().__init__(template)

    def substitute(self, mapping = _sentinel_dict, /, **kwds):
        # pylint: disable=dangerous-default-value
        if mapping is _sentinel_dict:
            mapping = self._defaults
        else:
            mapping = _ChainMap(mapping, self._defaults)
        return super().substitute(mapping, **kwds)

    def safe_substitute(self, mapping = _sentinel_dict, /, **kwds):
        # pylint: disable=dangerous-default-value
        if mapping is _sentinel_dict:
            mapping = self._defaults
        else:
            mapping = _ChainMap(mapping, self._defaults)
        return super().safe_substitute(mapping, **kwds)

    def get_identifiers_and_defaults(self) -> Dict[str, any]:
        """
        Gets all the identifiers from this template in a Dict with any associated default values
        """
        ids = TemplateEx.get_template_identifiers(self)
        return { i: self._defaults.get(i, None) for i in ids }

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

# "static" initialization of TemplateEx.pattern_for_defaults.
#  __init_subclass__() is automatically called only for subclasses.
TemplateEx.__init_subclass__()
