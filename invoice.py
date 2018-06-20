# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta, Pool

__all__ = ['Invoice']


class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'

    @classmethod
    def create_commissions(cls, invoices):
        Commission = Pool().get('commission')

        all_commissions = super(Invoice, cls).create_commissions(invoices)

        commissions_manager = []
        for commission in all_commissions:
            if commission.agent.manager:
                commission_manager = commission.get_commission_manager()
                if commission_manager:
                    commissions_manager.append(commission_manager)

        if commissions_manager:
            Commission.save(commissions_manager)
            all_commissions += commissions_manager

        return all_commissions
