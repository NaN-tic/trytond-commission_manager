# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta

__all__ = ['InvoiceLine']


class InvoiceLine:
    __name__ = 'account.invoice.line'
    __metaclass__ = PoolMeta

    @classmethod
    def __setup__(cls):
        super(InvoiceLine, cls).__setup__()

        cls._error_messages.update({
                'manager_without_plan': ('No commission plan assigned '
                    'for manager "%s"'),
            })

    def agent_plans_used(self):
        used = super(InvoiceLine, self).agent_plans_used()
        if not (self.invoice.agent and self.invoice.agent.manager):
            return used

        manager = self.invoice.agent.manager

        if not manager.agent.plan:
            self.raise_user_error('manager_without_plan', {
                        'manager': manager.rec_name,
                        })
        used += [(manager.agent, manager.agent.plan)]
        return used
