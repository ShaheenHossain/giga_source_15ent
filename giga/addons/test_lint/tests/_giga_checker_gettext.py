import os

import astroid
from pylint import checkers, interfaces


class GigaBaseChecker(checkers.BaseChecker):
    __implements__ = interfaces.IAstroidChecker
    name = 'giga'

    msgs = {
        'E8502': (
            'Bad usage of _, _lt function.',
            'gettext-variable',
            'See https://www.gigasource.de/documentation/15.0/developer/misc/i18n/translations.html#variables'
        )
    }

    @checkers.utils.check_messages('gettext-variable')
    def visit_call(self, node):
        if isinstance(node.func, astroid.Name) and node.func.name in ('_', '_lt'):
            first_arg = node.args[0]
            if not (isinstance(first_arg, astroid.Const) and isinstance(first_arg.value, str)):
                self.add_message('gettext-variable', node=node)


def register(linter):
    linter.register_checker(GigaBaseChecker(linter))
