# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from decimal import Decimal
from simpleeval import simple_eval
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.tools import decistmt

__all__ = ['Manager', 'Agent', 'Commission']


class Manager(ModelSQL, ModelView):
    'Commission Manager'
    __name__ = 'commission.manager'
    agent = fields.Many2One('commission.agent', 'Agent', required=True)
    agents = fields.One2Many('commission.agent', 'manager', 'Agents',
        add_remove=[
            ('manager', '=', None),
            ('id', '!=', Eval('agent')),
        ], depends=['agent'])
    company = fields.Many2One('company.company', 'Company', required=True)
    formula = fields.Char('Formula', required=True,
        help=('Python expression that will be evaluated with:\n'
            '- amount: the original amount'))

    @classmethod
    def __setup__(cls):
        super(Manager, cls).__setup__()
        cls._error_messages.update({
                'invalid_formula': ('Invalid formula "%(formula)s" in '
                    'commission manager "%(line)s" with exception '
                    '"%(exception)s".'),
                })

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_formula():
        return 'amount'

    @classmethod
    def validate(cls, lines):
        super(Manager, cls).validate(lines)
        for line in lines:
            line.check_formula()

    def get_context_formula(self, amount, product):
        return {
            'names': {
                'amount': amount,
                },
            }

    def check_formula(self):
        context = self.get_context_formula(Decimal(0), None)

        try:
            if not isinstance(self.get_amount(**context), Decimal):
                raise ValueError
        except ValueError, exception:
            self.raise_user_error('invalid_formula', {
                    'formula': self.formula,
                    'line': self.rec_name,
                    'exception': exception,
                    })

    def get_amount(self, **context):
        'Return amount (as Decimal)'
        context.setdefault('functions', {})['Decimal'] = Decimal
        return simple_eval(decistmt(self.formula), **context)


class Agent:
    __metaclass__ = PoolMeta
    __name__ = 'commission.agent'
    manager = fields.Many2One('commission.manager', 'Manager',
        ondelete='CASCADE', select=True)


class Commission:
    __metaclass__ = PoolMeta
    __name__ = 'commission'

    @classmethod
    def _get_origin(cls):
        origins = super(Commission, cls)._get_origin()
        if not 'commission' in origins:
            origins += ['commission']
        return origins

    def get_commission_manager(self):
        Commission = Pool().get('commission')

        if not self.agent.manager.agent:
            return

        manager = self.agent.manager
        context = manager.get_context_formula(self.amount, self.product)
        amount = manager.get_amount(**context)

        commission = Commission()
        commission.origin = self
        if hasattr(self, 'date'):
            commission.date = self.date
        commission.agent = manager.agent
        commission.product = self.product
        commission.amount = amount if self.amount > 0 else amount
        return commission
