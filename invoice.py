# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['InvoiceLine']


class InvoiceLine(metaclass=PoolMeta):
    __name__ = 'account.invoice.line'
    __metaclass__ = PoolMeta

    @property
    def agent_plans_used(self):
        used = super(InvoiceLine, self).agent_plans_used
        if not (self.invoice.agent and self.invoice.agent.manager):
            return used

        manager = self.invoice.agent.manager

        if not manager.agent.plan:
            raise UserError(gettext(
                'commission_manager.manager_without_plan',
                        manager=manager.rec_name))
        used.append((manager.agent, manager.agent.plan))
        return used
