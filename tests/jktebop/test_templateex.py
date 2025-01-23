""" Unit tests for the TemplateEx class. """
# pylint: disable=protected-access
import unittest
from string import Template

from deblib.jktebop.templateex import TemplateEx

class TestTemplateEx(unittest.TestCase):
    """ Unit tests for the TemplateEx class. """

    #
    # __init__(self, template: str)
    #
    def test_init_valid_template_text(self):
        """ Tests __init__(various valid template str) initializes correctly """
        # Some may not be valid templates but issues don't manifest unless (safe_)substitute called
        for (text,                          exp_ids_and_defs) in [
            ("",                            {}),
            ("text only",                   {}),
            ("$$escapeddollar",             {}),
            ("invalid single --> $",        {}),
            ("$a ${b}ty",                   { "a": None, "b": None }),
            ("${a} ${b}ty",                 { "a": None, "b": None }),
            ("${a}${b}ty",                  { "a": None, "b": None }),
            ("${a}\n${b}ty",                { "a": None, "b": None }),
            ("${a} ${b} invalid--> $\n{c}", { "a": None, "b": None }),
            # TemplateEx specific extended syntax for specifying the default value: ${name|default}
            ("${a|} ${b}ty",                { "a": "", "b": None }),
            ("${a|ha} ${b}ty",              { "a": "ha", "b": None }),
            ("$a ${b|}ty",                  { "a": None, "b": "" }),
            ("$a ${b|mis}ty",               { "a": None, "b": "mis" }),
            ("${a|} ${b|mis}ty",            { "a": "", "b": "mis" }),
            ("$a|not-default ${b}ty",       { "a": None, "b": None }),
        ]:
            template = TemplateEx(text)

            # This asserts the extended functionality of TemplateEx, which will parse the text to
            # capture and consume the ${name|default} syntax to build up the defaults dict.
            ids_defs = template.get_identifiers_and_defaults()
            self.assertDictEqual(exp_ids_and_defs, ids_defs,
                                 f"For template text=={text}' expect " +
                                 f"ids_defs=={exp_ids_and_defs} but is {ids_defs}")

            # This asserts the base Template functionality/pattern to parse the text, with any sign
            # of defaults syntax having been removed by TemplateEx, to list the placeholders found.
            ids = TemplateEx.get_template_identifiers(template)
            self.assertListEqual([*exp_ids_and_defs.keys()], ids)

    def test_init_invalid_template_text(self):
        """ Tests __init__(invalid args) initializes like base Template """
        # The validity of the template text tends not to be tested on __init__()
        for text in [None, "a single $ is bad", "a single $\na over newline is bad too"]:
            self.assertEqual(text, Template(text).template)
            self.assertEqual(text, TemplateEx(text).template)

    #
    # substitute(self, mapping: dict[str, any], /, **kwds) -> str:
    #       and
    # safe_substitute(self, mapping: dict[str, any], /, **kwds) -> str
    #
    # The only difference, is substitute will error if a mapping/kwd is not given for a placeholder
    # whereas safe_substitute() will not (leaving the placeholder in the result)
    #
    def test_both_substitute_valid_mapping_or_kwds_applied(self):
        """ Tests (safe_)substitute(mappings or kwds for all) assert substituted result """
        # There are Mappings/kwds for every placeholder, and potentially some extra which should be
        # ignored, so we expect them to be applied with no use of any template default values.
        # Exclusive use of mapping or kwds expected to be equivalent
        for (text,                  params,                                 exp_result) in [
            ("",                    {},                                     ""),
            ("none",                {},                                     "none"),
            ("still none",          { "a": "ignored" },                     "still none"),
            # Basic subs and order agnostic
            ("${a} ${b}ty",         { "a": 1, "b": "ten" },                 "1 tenty"),
            ("${a} ${b}ty",         { "b": "twen", "a": 2 },                "2 twenty"),
            # Works over multiple lines
            ("\n$a\n${b}ty\n$c\n",  { "a": 3, "b": "thir", "c": "boo" },    "\n3\nthirty\nboo\n"),
            # Ignore mapping/kwds not in template
            (r"$a ${b}ty",          { "a": 4, "b": "for", "c": "ignored" }, "4 forty"),
            # These use the extended syntax for defining default values
            (r"$a ${b|}ty",         { "a": 5, "b": "fif" },                 "5 fifty"),
            (r"$a ${b|mis}ty",      { "a": 6, "b": "six" },                 "6 sixty"),
            (r"$a ${b|}",           { "a": 7, "b": "seven" },               "7 seven"),
            (r"$a ${b|mis}",        { "a": 8, "b": "eight" },               "8 eight"),
        ]:
            template = TemplateEx(text)
            for func in [template.substitute, template.safe_substitute]:
                for ix, result in enumerate([func(params), func(**params)]):
                    func_text = f"{func.__name__}(" + ("" if not ix else "**") + f"{params})"
                    self.assertEqual(exp_result, result,
                                    f"For template text=='{text}', expected " +
                                    f"{func_text}=='{exp_result}' but is '{result}'")

    def test_both_substitute_valid_mappings_and_kwds_applied(self):
        """ Tests (safe_)substitute(mappings and kwds for all) assert subs result & precedent """
        # There are Mappings/kwds for every placeholder, and potentially some extra which should be
        # ignored, so we expect them to be applied with no use of any template default values.
        # Where a param is present in both kwds takes precedent.
        for (text,                  mapping,            kwds,                   exp_result) in [
            (r" none ",             { "a":1 },          { "b":"B" },          " none "),
            (r"$a ${b}",            { "a":1 },          { "b":"B" },            "1 B"),
            (r"${a} ${b}",          { "a":2 },          { "b":"B" },            "2 B"),
            (r"${a} ${b}",          { "a":3, "b":"b" }, { "b":"B" },            "3 B"),
            (r"${a} ${b}",          { "a":4, "c":"c" }, { "b":"B" },            "4 B"),
            (r"${a} ${b}",          { "a":5, "c":"c" }, { "b":"B", "c":"C" },   "5 B"),
            (r"${a} ${b}",          { "a":6 },          { "b":"B", "c":"C" },   "6 B"),

            (r"${a|} ${b|bee}",     { "a":11,"b":"b" }, { "b":"B" },            "11 B"),
            (r"${a|} ${b|bee}",     { "a":12,"c":"c" }, { "b":"B" },            "12 B"),
            (r"${a|} ${b|bee}",     { "a":13 },         { "b":"B", "c":"C" },   "13 B"),
            (r"${a|} ${b|bee}",     { "a":14,"c":"c" }, { "b":"B", "c":"C" },   "14 B"),
        ]:
            template = TemplateEx(text)
            for func in [template.substitute, template.safe_substitute]:
                result = func(mapping, **kwds)
                func_text = f"{func.__name__}({mapping}, **{kwds})"
                self.assertEqual(exp_result, result,
                                f"For template text=='{text}', expected " +
                                f"{func_text}=='{exp_result}' but is '{result}'")

    def test_both_substitute_missing_mappings_with_defaults(self):
        """ Tests substitute(missing mappings where defaults given) assert successful fallback """
        # We expect the mapping to be applied to replace placeholders,
        # with the default value for a placeholder applied when it is not in the mapping.
        for (text,                          params,                     exp_result) in [
            (r"${a} ${b|}ty",               { "a": 1 },                 "1 ty"),
            (r"$a ${b|}ty",                 { "a": 2 },                 "2 ty"),
            (r"$a ${b|mis}ty",              { "a": 3 },                 "3 misty"),
            (r"$a ${b|mis}ty ${c|default}", { "a": 4, "b": "for" },     "4 forty default"),
        ]:
            template = TemplateEx(text)
            for func in [template.substitute, template.safe_substitute]:
                for ix, result in enumerate([func(params), func(**params)]):
                    func_text = f"{func.__name__}(" + ("" if not ix else "**") + f"{params})"
                    self.assertEqual(exp_result, result,
                                    f"For template text=='{text}', expected " +
                                    f"{func_text}=='{exp_result}' but is '{result}'")            

    def test_both_substitute_escaped_delimiter(self):
        """ Tests substitute(valid mappings) assert escaped dollars handled as base Template """
        # We expect escaped dollars $$ to be replaced with $ (base Template functionality)
        for (text,                      params,                     exp_result) in [
            (r"$$ 0 $$ $$$$ nought $$", { },                        "$ 0 $ $$ nought $"),
            (r"$a $$ ${b} $$",          { "a": 1, "b": "one" },     "1 $ one $"),
            (r"$a$$ ${b}$$",            { "a": 2, "b": "two" },     "2$ two$"),
            (r"$$$a $$${b}",            { "a": 3, "b": "three" },   "$3 $three"),
            (r"$a$$dog ${b}$$cat",      { "a": 4, "b": "four" },    "4$dog four$cat"),
        ]:
            template = TemplateEx(text)
            for func in [template.substitute, template.safe_substitute]:
                for ix, result in enumerate([func(params), func(**params)]):
                    func_text = f"{func.__name__}(" + ("" if not ix else "**") + f"{params})"
                    self.assertEqual(exp_result, result,
                                    f"For template text=='{text}', expected " +
                                    f"{func_text}=='{exp_result}' but is '{result}'")    

    #
    #   These tests cover the different behavious of substitute() and safe_substitute()
    #
    def test_substitute_missing_mappings_with_no_default(self):
        """ Tests substitute(missing mapping/kwd) assert KeyError raised """
        # Where there is no default to fallback on, we expect the underlying behaviour of a KeyError
        for (text,                  params,                 exp_missing_key) in [
            (r"$a ${b}ty",          { "a":"a" },            "b"),
            (r"$a ${b}ty",          { "a":"a", "B":"B" },   "b"),
            (r"$a ${b}ty",          { "a":"a", "c":"c" },   "b"),
            (r"$a ${b}ty",          { "b":"b" },            "a"),
        ]:
            func = TemplateEx(text).substitute
            for use_mapping in [True, False]:
                with self.assertRaises(KeyError) as ect:
                    _ = func(params) if use_mapping else func(**params)
                missing_key = ect.exception.args[0]
                func_text = f"{func.__name__}(" + ("" if use_mapping else "**") + f"{params})"
                self.assertEqual(exp_missing_key, missing_key,
                                 f"For template text=='{text}', expected {func_text} to raise " +
                                 f"KeyError for '{exp_missing_key}' but is for '{missing_key}'")

    def test_safe_substitute_missing_mappings_with_no_default(self):
        """ Tests safe_substitute(missing mapping/kwd) no KeyError and placeholder in result """
        # Where there is no default to fallback on, we expect the underlying
        # behaviour of the placeholder being left in the result
        for (text,                  params,                 exp_result) in [
            (r"$a ${b}ty",          { "a":1 },              "1 ${b}ty"),
            (r"$a ${b}ty",          { "a":2, "B":"B" },     "2 ${b}ty"),
            (r"$a ${b}ty",          { "a":3, "c":"c" },     "3 ${b}ty"),
            (r"$a ${b}ty",          { "b":"for" },          "$a forty"),
        ]:
            func = TemplateEx(text).safe_substitute
            for use_mapping in [True, False]:
                result = func(params) if use_mapping else func(**params)
                func_text = f"{func.__name__}(" + ("" if use_mapping else "**") + f"{params})"
                self.assertEqual(exp_result, result,
                                 f"For template text=='{text}', expected " +
                                 f"{func_text}=='{exp_result}' but is '{result}'")    

    def test_substitute_invalid_placeholders(self):
        """ Tests substitute(invalid args) initializes like base Template """
        # substitute() appears less tolerant of single $ than safe_substitute
        for (text,                                      exp_error,      in_error_text) in [
            (None,                                      TypeError,      ""),
            ("a single $ is bad",                       ValueError,     "Invalid placeholder"),
            ("a single $\na over newline is bad too",   ValueError,     "Invalid placeholder")
        ]:
            for template in [Template(text), TemplateEx(text)]:
                for use_mapping in [True, False]:
                    func_text = f"{template.__class__.__name__}.substitute" \
                                        + "({})" if use_mapping else "(**{})"
                    with self.assertRaises(exp_error) as ect:
                        _ = template.substitute({}) if use_mapping else template.substitute(**{})
                    if exp_error is ValueError:
                        error_text = ect.exception.args[0]
                        self.assertIn(in_error_text, error_text,
                                        f"For template text=='{text}', expected {func_text} to " +
                                        f"raise {exp_error.__name__} containing " +
                                        f"'{in_error_text}' but message is '{error_text}'")
