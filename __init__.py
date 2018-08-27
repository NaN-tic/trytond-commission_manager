# This file is part commission_manager module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import commission
from . import invoice


def register():
    Pool.register(
        commission.Manager,
        commission.Agent,
        commission.Commission,
        invoice.InvoiceLine,
        module='commission_manager', type_='model')
