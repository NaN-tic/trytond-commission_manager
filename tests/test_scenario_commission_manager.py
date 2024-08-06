import unittest
from decimal import Decimal

from proteus import Model
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear,
                                                 get_accounts)
from trytond.modules.account_invoice.tests.tools import (
    create_payment_term, set_fiscalyear_invoice_sequences)
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install product_cost_plan Module
        config = activate_modules('commission_manager')

        # Create company
        _ = create_company()
        company = get_company()

        # Reload the context
        User = Model.get('res.user')
        config._context = User.get_preferences(True, config.context)

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)

        # Create customer
        Party = Model.get('party.party')
        customer = Party(name='Customer')
        customer.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = accounts['expense']
        account_category.account_revenue = accounts['revenue']
        account_category.save()

        # Create commission product
        Uom = Model.get('product.uom')
        Template = Model.get('product.template')
        Product = Model.get('product.product')
        unit, = Uom.find([('name', '=', 'Unit')])
        commission_product = Product()
        template = Template()
        template.name = 'Commission'
        template.default_uom = unit
        template.type = 'service'
        template.list_price = Decimal(0)
        template.cost_price = Decimal(0)
        template.account_category = account_category
        template.save()
        commission_product.template = template
        commission_product.save()

        # Create commission plan
        Plan = Model.get('commission.plan')
        plan = Plan(name='Plan')
        plan.commission_product = commission_product
        plan.commission_method = 'payment'
        line = plan.lines.new()
        line.formula = 'amount * 0.1'
        plan.save()

        # Create payment term
        payment_term = create_payment_term()
        payment_term.save()

        # Create manager
        Agent = Model.get('commission.agent')
        Manager = Model.get('commission.manager')
        party_manager = Party(name='Agent Manager')
        party_manager.supplier_payment_term = payment_term
        party_manager.save()
        agent_manager = Agent(party=party_manager)
        agent_manager.type_ = 'agent'
        agent_manager.plan = plan
        agent_manager.currency = company.currency
        agent_manager.save()
        manager = Manager()
        manager.agent = agent_manager
        manager.save()

        # Create some agents
        agent_party = Party(name='Agent')
        agent_party.supplier_payment_term = payment_term
        agent_party.save()
        agent = Agent(party=agent_party)
        agent.type_ = 'agent'
        agent.plan = plan
        agent.currency = company.currency
        agent.save()
        agent_party2 = Party(name='Agent 2')
        agent_party2.supplier_payment_term = payment_term
        agent_party2.save()
        agent2 = Agent(party=agent_party2)
        agent2.type_ = 'agent'
        agent2.plan = plan
        agent2.currency = company.currency
        agent2.manager = manager
        agent2.save()
        agent_party3 = Party(name='Agent 3')
        agent_party3.supplier_payment_term = payment_term
        agent_party3.save()
        agent3 = Agent(party=agent_party3)
        agent3.type_ = 'agent'
        agent3.plan = plan
        agent3.currency = company.currency
        agent3.manager = manager
        agent3.save()

        # Create principal
        principal_party = Party(name='Principal')
        principal_party.customer_payment_term = payment_term
        principal_party.save()
        principal = Agent(party=principal_party)
        principal.type_ = 'principal'
        principal.plan = plan
        principal.currency = company.currency
        principal.save()

        # Create product sold
        product = Product()
        template = Template()
        template.name = 'Product'
        template.default_uom = unit
        template.type = 'service'
        template.list_price = Decimal(100)
        template.cost_price = Decimal(100)
        template.account_category = account_category
        template.principals.append(principal)
        template.save()
        product.template = template
        product.save()

        # Create agent invoice
        Commission = Model.get('commission')
        Invoice = Model.get('account.invoice')
        invoice = Invoice()
        invoice.party = customer
        invoice.payment_term = payment_term
        invoice.agent = agent
        line = invoice.lines.new()
        line.product = product
        line.quantity = 1
        line.unit_price = Decimal(100)
        invoice.save()
        invoice.click('post')
        line, = invoice.lines
        self.assertEqual(len(line.commissions), 2)
        com1, com2 = line.commissions
        self.assertEqual(com1.agent, agent)
        self.assertEqual(com2.agent, principal)
        coms_manager = Commission.find([('agent', '=', agent_manager.id)])
        self.assertEqual(len(coms_manager), 0)
        invoice = Invoice()
        invoice.party = customer
        invoice.payment_term = payment_term
        invoice.agent = agent2
        line = invoice.lines.new()
        line.product = product
        line.quantity = 1
        line.unit_price = Decimal(100)
        invoice.save()
        invoice.click('post')
        line, = invoice.lines
        self.assertEqual(len(line.commissions), 3)
        com1, com2, com3 = line.commissions
        com_manager, = Commission.find([('agent', '=', agent_manager.id)])
        self.assertEqual(com_manager.amount, Decimal(10.00))
        self.assertEqual(com1.amount, Decimal(10.00))
        invoice = Invoice()
        invoice.party = customer
        invoice.payment_term = payment_term
        invoice.agent = agent2
        line = invoice.lines.new()
        line.product = product
        line.quantity = -1
        line.unit_price = Decimal(100)
        invoice.save()
        invoice.click('post')
        line, = invoice.lines
        self.assertEqual(len(line.commissions), 3)
        com1, com2, com3 = line.commissions
        self.assertEqual(com3.amount, Decimal(-10.00))
        self.assertEqual(com1.amount, Decimal(-10.00))
