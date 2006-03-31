#!/usr/bin/env python
"""
cli.py

Support structures for command line interface to tagging, embedding
and lookup.
"""

__id__ = "$Id$"
__version__ = "$Revision$"
__copyright__ = '(c) 2004, Creative Commons, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'

import optparse

def expandFiles(args):
    """Expands any file wildcards contained in args and returns an expanded,
    explicit list.
    """

    return args

class Option (optparse.Option):
    ATTRS = optparse.Option.ATTRS + ['required']

    def _check_required (self):
        if self.required and not self.takes_value():
            raise optparse.OptionError(
                "required flag set for option that doesn't take a value",
                 self)

    # Make sure _check_required() is called from the constructor!
    CHECK_METHODS = optparse.Option.CHECK_METHODS + [_check_required]

    def process (self, opt, value, values, parser):
        optparse.Option.process(self, opt, value, values, parser)
        parser.option_seen[self] = 1

class OptionParser (optparse.OptionParser):

    def _init_parsing_state (self):
        optparse.OptionParser._init_parsing_state(self)
        self.option_seen = {}

    def check_values (self, values, args):
        for option in self.option_list:
            if (isinstance(option, Option) and
                option.required and
                not self.option_seen.has_key(option)):
                self.error("%s not supplied" % option)
        return (values, args)

