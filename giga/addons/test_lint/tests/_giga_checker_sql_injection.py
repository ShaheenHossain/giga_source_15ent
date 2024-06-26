import os

import astroid
from pylint import checkers, interfaces

DFTL_CURSOR_EXPR = [
    'self.env.cr', 'self._cr',  # new api
    'self.cr',  # controllers and test
    'cr',  # old api
]


class GigaBaseChecker(checkers.BaseChecker):
    __implements__ = interfaces.IAstroidChecker
    name = 'giga'

    msgs = {
        'E8501': (
            'Possible SQL injection risk.',
            'sql-injection',
            'See http://www.bobby-tables.com try using '
            'execute(query, tuple(params))',
        )
    }

    def _get_cursor_name(self, node):
        expr_list = []
        node_expr = node.expr
        while isinstance(node_expr, astroid.Attribute):
            expr_list.insert(0, node_expr.attrname)
            node_expr = node_expr.expr
        if isinstance(node_expr, astroid.Name):
            expr_list.insert(0, node_expr.name)
        cursor_name = '.'.join(expr_list)
        return cursor_name

    def _allowable(self, node):
        """
        :type node: NodeNG
        """
        infered = checkers.utils.safe_infer(node)
        # The package 'psycopg2' must be installed to infer
        # ignore sql.SQL().format
        if infered and infered.pytype().startswith('psycopg2'):
            return True
        if isinstance(node, astroid.Call):
            node = node.func
        # self._thing is OK (mostly self._table), self._thing() also because
        # it's a common pattern of reports (self._select, self._group_by, ...)
        return (isinstance(node, astroid.Attribute)
            and isinstance(node.expr, astroid.Name)
            and node.attrname.startswith('_')
            # cr.execute('SELECT * FROM %s' % 'table') is OK since that is a constant
            or isinstance(node, astroid.Const)
        )

    def _check_concatenation(self, node):
        if isinstance(node, astroid.BinOp) and node.op in ('%', '+'):
            if isinstance(node.right, astroid.Tuple):
                # execute("..." % (self._table, thing))
                if not all(map(self._allowable, node.right.elts)):
                    return True
            elif isinstance(node.right, astroid.Dict):
                # execute("..." % {'table': self._table}
                if not all(self._allowable(v) for _, v in node.right.items):
                    return True
            elif not self._allowable(node.right):
                # execute("..." % self._table)
                return True
            # Consider cr.execute('SELECT ' + operator + ' FROM table' + 'WHERE')"
            # node.repr_tree()
            # BinOp(
            #    op='+',
            #    left=BinOp(
            #       op='+',
            #       left=BinOp(
            #          op='+',
            #          left=Const(value='SELECT '),
            #          right=Name(name='operator')),
            #       right=Const(value=' FROM table')),
            #    right=Const(value='WHERE'))
            # Notice that left node is another BinOp node
            return not self._allowable(node.left) and self._check_concatenation(node.left)

        # check execute("...".format(self._table, table=self._table))
        if isinstance(node, astroid.Call) \
                and isinstance(node.func, astroid.Attribute) \
                and node.func.attrname == 'format':

            if not all(map(self._allowable, node.args or [])):
                return True

            if not all(
                self._allowable(keyword.value)
                for keyword in (node.keywords or [])
            ):
                return True

        return False

    def _check_sql_injection_risky(self, node):
        # Inspired from OCA/pylint-giga project
        # Thanks @moylop260 (Moisés López) & @nilshamerlinck (Nils Hamerlinck)
        current_file_bname = os.path.basename(self.linter.current_file)
        if not (
            # .execute() or .executemany()
            isinstance(node, astroid.Call) and node.args and
            isinstance(node.func, astroid.Attribute) and
            node.func.attrname in ('execute', 'executemany') and
            # cursor expr (see above)
            self._get_cursor_name(node.func) in DFTL_CURSOR_EXPR and
            # cr.execute("select * from %s" % foo, [bar]) -> probably a good reason for string formatting
            len(node.args) <= 1 and
            # ignore in test files, probably not accessible
            not current_file_bname.startswith('test_')
        ):
            return False
        first_arg = node.args[0]
        is_concatenation = self._check_concatenation(first_arg)
        # if first parameter is a variable, check how it was built instead
        if (not is_concatenation and isinstance(first_arg, (astroid.Name, astroid.Subscript))):

            # 1) look for parent scope (where the definition lives)
            current = node
            while (current and not isinstance(current.parent, astroid.FunctionDef)):
                current = current.parent
            if not current:
                return is_concatenation
            parent = current.parent

            # 2) check how was the variable built
            for node_assign in parent.nodes_of_class(astroid.Assign):
                if node_assign.targets[0].as_string() != first_arg.as_string():
                    continue
                is_concatenation = self._check_concatenation(node_assign.value)
                if is_concatenation:
                    break
        return is_concatenation

    @checkers.utils.check_messages('sql-injection')
    def visit_call(self, node):
        if self._check_sql_injection_risky(node):
            self.add_message('sql-injection', node=node)


def register(linter):
    linter.register_checker(GigaBaseChecker(linter))
