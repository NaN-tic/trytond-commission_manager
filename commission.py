# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from decimal import Decimal
from simpleeval import simple_eval
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.tools import decistmt
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['Manager', 'Agent']


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

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    def get_rec_name(self, name):
        return self.agent.rec_name


class Agent(metaclass=PoolMeta):
    __name__ = 'commission.agent'
    manager = fields.Many2One('commission.manager', 'Manager',
        ondelete='CASCADE', select=True)
