# -*- encoding: utf-8 -*-

from trytond.model import ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.wizard import Wizard
from trytond.backend import TableHandler

class ProjectBudgetTemplate(ModelSQL, ModelView):
    "Project Budget Template"
    _name = "project.budget.template"
    _description = __doc__

    name = fields.Char("Name Template", size=128, required=True)
    type_budget = fields.Char("Type Budget", size=30, required=True)
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')
    active = fields.Boolean('Active')
    parent = fields.Many2One('project.budget.template', 'Parent Line')
    child = fields.One2Many('project.budget.template', 'parent', 'Child Line')
    line = fields.One2Many('project.budget.lines.template', 'budget', 'Budget Lines')
    notes = fields.Text('Notes', help="Internal description of the project.")
#        'state = fields.selection([('template', 'Template'), ('open', 'Running'), ('pending', 'Pending'), ('cancelled', 'Cancelled'), ('done', 'Done')], 'State', required=True, readonly=True)


ProjectBudgetTemplate()

class ProjectBudgetLinesTemplate(ModelSQL, ModelView):
    "Project Budget Lines Template"
    _name = "project.budget.lines.template"
    _description = __doc__

    budget = fields.Many2One('project.budget.template', 'Budget Template')
    name = fields.Char("Name Item", size=128, required=True)
    type_line = fields.Selection([('section', 'Section'), ('item', 'Item'), ('subtotal', 'Subtotal')], 'Type Line', required=True)
    sort = fields.Integer('Sort Line')
    parent = fields.Many2One('project.budget.lines.template', 'Parent Line')
    child = fields.One2Many('project.budget.lines.template', 'parent', 'Child Lines')
    uom = fields.Many2One('product.uom', 'UoM')
    price_unit = fields.Float('Price Unit', digits=(16,2))
    notes = fields.Text('Notes')
#    state = fields.Selection([('template', 'Template'), ('open', 'Running'), ('pending', 'Pending'), ('cancelled', 'Cancelled'), ('done', 'Done')], 'State', required=True, readonly=True)

ProjectBudgetLinesTemplate()

class ProjectBudget(ModelSQL, ModelView):
    "Project Budget Line"
    _name = "project.budget"
    _description = __doc__
    _inherits = {'ekd.account.budget': 'budget'}

    budget = fields.Many2One('ekd.account.budget', 'Budget')
    project = fields.Many2One('ekd.project', 'Project')
#    name = fields.Char("Name Item", size=128, required=True)
#    type_line = fields.Selection([('section', 'Section'), ('item', 'Item'), ('subtotal', 'Subtotal')], 'Type Line', required=True)
#    sort = fields.Integer('Sort Line')
#    parent = fields.Many2One('project.budget', 'Parent Line')
#    child = fields.One2Many('project.budget', 'parent', 'Child Lines')
#    quantity = fields.Float('Quantity', digits=(16,4))
#    uom = fields.One2Many('product.uom', 'UoM')
#    price_unit = fields.Float('Price Unit', digits=(16,2))
#    amount = fields.Float('Total Line', digits=(16,2))
#    notes = fields.Text('Notes')
    lines = fields.One2Many('project.budget.line', 'budget_prj', 'Project')
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('paid', 'Paid'),('cancelled', 'Cancelled'), ('done', 'Done')], 'State', required=True, readonly=True)

    def default_state(self):
        return Transaction().context.get('state') or 'draft'

ProjectBudget()

class ProjectBudgetLine(ModelSQL, ModelView):
    "Project Budget Line"
    _name = "project.budget.line"
    _description = __doc__
    _inherits = {'ekd.account.budget.line': 'budget_line'}

    budget_line = fields.Many2One('ekd.account.budget.line', 'Budget Account')
    budget_prj = fields.Many2One('project.budget', 'Budget Project')
    project = fields.Many2One('ekd.project', 'Project')
#    name = fields.Char("Name Item", size=128, required=True)
#    type_line = fields.Selection([('section', 'Section'), ('item', 'Item'), ('subtotal', 'Subtotal')], 'Type Line', required=True)
#    sort = fields.Integer('Sort Line')
#    parent = fields.Many2One('project.budget', 'Parent Line')
#    child = fields.One2Many('project.budget', 'parent', 'Child Lines')
#    quantity = fields.Float('Quantity', digits=(16,4))
#    uom = fields.One2Many('product.uom', 'UoM')
    price_unit = fields.Float('Price Unit', digits=(16,2))
#    amount = fields.Float('Total Line', digits=(16,2))
#    notes = fields.Text('Notes')
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('paid', 'Paid'),('cancelled', 'Cancelled'), ('done', 'Done')], 'State', required=True, readonly=True)

    def default_state(self):
        return Transaction().context.get('state') or 'draft'

ProjectBudgetLine()
