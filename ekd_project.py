# -*- coding: utf-8 -*-
"Project"
import datetime
from trytond.model import ModelStorage, ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.wizard import Wizard
from trytond.backend import TableHandler
from trytond.pyson import In, If, Get, Eval, Not, Equal, Bool, Or, And
from decimal import Decimal
import logging

_RUNNING_STATES = {
    'readonly': Equal(Eval('state'), 'open'),
    }

_RUNNING_DEPENDS = ['state']

_LINE_STATES = {
    'readonly': Equal(Eval('state'), 'empty'),
    }

_LINE_DEPENDS = ['state']

class ProjectMain(ModelSQL, ModelView):
    "Project Main"
    _name = "ekd.project"
    _description = __doc__
    _rec_name = "name"

    company = fields.Many2One('company.company', 'Company', select=2)
    type_project = fields.Many2One('ekd.project.type', 'Type Project', select=2)
    code = fields.Char("Project Code", size=30, readonly=True, select=2)
    name = fields.Char("Project Name", size=256, required=True, select=2)
    shortcut = fields.Char("Short Name", size=128, required=True, on_change_with=['name', 'shortcut'], select=1)
    full_name = fields.Function(fields.Char("Full Project Name"), 'get_full_name')
    property = fields.One2Many('ekd.project.property', 'project', 'Property Project', select=2)
    party = fields.Many2One('party.party', 'Customer', select=2)
    contact = fields.Many2One('ekd.party.contact', 'Contact Face', select=2, domain=[('party','=',Eval('party'))], depends=['party'])
    account_revenue = fields.Many2One('ekd.account','Account Revenue', domain=[('company','=',Eval('company'))], depends=['company'])
    account_cost = fields.Many2One('ekd.account','Account Cost', domain=[('company','=',Eval('company'))], depends=['company'])
    balance_revenue = fields.Many2One('ekd.balances.party','Revenue')
    balance_cost = fields.Many2One('ekd.balances.analytic','Cost')
    analytic = fields.Many2One('ekd.account.analytic','Analytic Account', help="Link this project to an analytic account if you need financial management on projects. It enables you to connect projects with budgets, planning, cost and revenue analysis, timesheets on projects, etc.")
    manager = fields.Many2One('company.employee', 'Coordinator', select=2)
    employee = fields.Many2One('company.employee', ' Performer', select=2)
    warn_employee = fields.Boolean('Warn Supervisor')
    priority = fields.Selection([('00','0'),('01','1'),('02','2'),('03','3'),('04','4'),('05','5'),('06','6'),('07','7'),('08','8'),('09','9')],'Priority', select=1)
    active = fields.Boolean('Active', select=2)
    parent = fields.Many2One('ekd.project',  'Parent Project')
    childs = fields.One2Many('ekd.project.subproject', 'parent', 'Chield Project', 
                states=_LINE_STATES, depends=_LINE_DEPENDS)
    budget = fields.Many2One('ekd.account.budget', "Project budget", 
                    context={'code':Eval('code'), 'company':Eval('company'), 'name':Eval('shortcut'), 'party':Eval('party'),
                            'start_date':Eval('start_date'), 'end_date': Eval('end_date'), 'project': True },
                states=_LINE_STATES, depends=_LINE_DEPENDS)
    tasks = fields.One2Many('ekd.project.tasks', 'project', "Project tasks",
                    context={'performer':Eval('employee'), 'party':Eval('party'),
                            'start_date':Eval('start_date'), 'end_date': Eval('end_date'), 'project': True },
                states=_LINE_STATES, depends=_LINE_DEPENDS, select=2)
    works = fields.One2Many('ekd.project.tasks.works', 'project', "Project works",
                states=_RUNNING_STATES, depends=_RUNNING_DEPENDS,select=2)
    events = fields.One2Many('ekd.project.events', 'project', "Project events")
    start_date = fields.Date('Starting Date', select=1)
    end_date = fields.Date('Expected End', select=1)
    total_income = fields.Function(fields.Numeric('Total Income (Fact, Plan)', digits=(16,2)), 'get_fields')
    total_expense = fields.Function(fields.Numeric('Total expense (Fact, Plan)', digits=(16,2)), 'get_fields')
    total_budget_income = fields.Function(fields.Numeric('Total Budget Income', digits=(16,2)), 'get_fields')
    total_budget_expense = fields.Function(fields.Numeric('Total Budget expense', digits=(16,2)), 'get_fields')
#    total_hour = fields.Function('get_total_amount',  type='numeric', string='Total Income', digits="(16.2)")
    notes = fields.Text('Notes', help="Internal description of the project.", select=2, on_change_with=['type_project', 'notes'])
    state = fields.Selection([
            ('draft', 'Draft'),
            ('empty', 'Empty'),
            ('template', 'Template'),
            ('pending', 'Pending'),
            ('open', 'Running'),
            ('cancelled', 'Cancelled'),
            ('done', 'Done'),
            ('deleted', 'Deleted')
            ], 'State', required=True, readonly=True, select=1)

    def __init__(self):
        super(ProjectMain, self).__init__()

#        self._sql_constraints += [
#                ('code_uniq', 'UNIQUE(code)', 'The code must be unique!'),
#                ]

        self._order.insert(0, ('end_date', 'ASC'))
        self._order.insert(1, ('party', 'ASC'))

        self._rpc.update({
                'button_draft': True,
                'button_pending': True,
                'button_template': True,
                'button_running': True,
                'button_cancelled': True,
                'button_done': True,
                'button_restore': True,
                })

        self._error_messages.update({
            'party_not_find': 'Party not find!',
            'type_proj_not_find': 'Type project not find!',
            })

    def default_company(self):
        return Transaction().context.get('company') or False

    def default_active(self):
        return True

    def default_priority(self):
        return Transaction().context.get('priority') or '05'

    def default_manager(self):
        return Transaction().context.get('employee')

    def default_start_date(self):
        return Transaction().context.get('start_date') or datetime.datetime.now()

    def default_end_date(self):
        return Transaction().context.get('end_date') or False

    def default_state(self):
        return Transaction().context.get('state') or 'empty'

    def default_budget(self):
        return Transaction().context.get('budget') or False

    def default_code(self):
        return Transaction().context.get('code') or '000.000.0000'

    def get_fields(self, ids, names):
        balance_analytic = self.pool.get('ekd.balances.analytic')
        balance_party = self.pool.get('ekd.balances.party')
        company_obj =  self.pool.get('company.company')
        if not ids:
            return
        res={}
        # total_income total_budget total_expense
        for project in self.browse(ids):
            for name in names:
                res.setdefault(name, {})
                res[name].setdefault(project.id, Decimal('0.0'))
                if name == 'total_income' and project.balance_revenue:
                    if project.balance_revenue:
                        res[name][project.id] = project.balance_revenue.debit-project.balance_revenue.credit
                elif name == 'total_budget_income' and project.budget:
                    res[name][project.id] = project.budget.total_income
                elif name == 'total_budget_expense' and project.budget:
                    res[name][project.id] = project.budget.total_budget
                elif name == 'total_expense':
                    balance_ids = balance_analytic.search([
                                    ('account','=',company_obj.browse(project.company.id).project_expense.id),
                                    ('model_ref','=', 'ekd.project,%s'%(project.id))
                                    ])
                    if balance_ids:
                        for balance in balance_analytic.browse(balance_ids):
                            res[name][project.id] += balance.balance_end
        return res

    def get_full_name(self, ids, name):
        if not ids:
            return
        res={}
        for project_obj in self.browse(ids):
            if project_obj.party:
                res[project_obj.id] = "%s - %s (%s) "%(project_obj.code,project_obj.name,project_obj.party.shortname)
            else:
                res[project_obj.id] = "%s - %s "%(project_obj.code,project_obj.name)
        return res

    def on_change_with_shortcut(self, vals):
        if vals.get('shortcut', False):
            return vals.get('shortcut')
        else: 
            return vals.get('name')

#    def on_change_with_code(self, vals):
##        if vals.get('code'):
# #           return vals.get('code')
#        if vals.get('type_project') and vals.get('party'):
#            return "0%s.0%s.0%s"%(vals.get('party'),vals.get('type_project'),str(ids[0]))

    def on_change_with_notes(self, vals):
        if not vals.get('type_project', False):
            return vals.get('notes')
        type_project_obj = self.pool.get('ekd.project.type')
        notes_model = type_project_obj.browse(vals.get('type_project')).notes_model
#        notes_dict1 = {}.fromkeys(note_model.split(':'))
#        notes_dict2 = {}.fromkeys(vals.get('notes').split(':'))
#        for notes_line in notes_dict
#            if 
#        return "%s %s"%(vals.get('notes'), note_model)
        if vals.get('notes'):
            return vals.get('notes')
        else:
            return notes_model

    def create(self, vals):
        if self.check_vals(vals):
            new_id = super(ProjectMain, self).create(vals)
            project = self.browse(new_id)
            self.write(new_id, {
                    'code': "0%s.0%s.0%s"%\
                        (project.party.id, project.type_project.id, str(new_id)),
                    })
        return new_id

    def check_vals(self, vals):
        if not vals.get('party'):
            self.raise_user_error('party_not_find')
            return False
        elif not vals.get('type_project'):
            self.raise_user_error('type_proj_not_find')
            return False

        return True

    def write(self, ids, vals):
        if isinstance(ids, (int, long)):
            ids = [ids]
        for project in self.browse(ids):
            if vals.get('party') and vals.get('type_project'):
                vals['code'] = "0%s.0%s.0%s"%(vals.get('party'), vals.get('type_project'), project.id)
            elif vals.get('party'):
                vals['code'] = "0%s.0%s.0%s"%(vals.get('party'), ekd.project.type_project.id, project.id)
            elif vals.get('type_project'):
                vals['code'] = "0%s.0%s.0%s"%(project.party.id, vals.get('type_project'), project.id)

        return super(ProjectMain, self).write(ids, vals)

    def button_pending(self, ids):
        return self.pending(ids)

    def button_template(self, ids):
        return self.template(ids)

    def button_running(self, ids):
        return self.running(ids)

    def button_cancelled(self, ids):
        return self.cancelled(ids)

    def button_draft(self, ids):
        return self.draft(ids)

    def button_done(self, ids):
        return self.done(ids)

    def button_restore(self, ids):
        return self.draft(ids)

    def draft(self, ids):
        for project in self.browse(ids):
            if project.state == 'cancelled':
                balance_analytic = self.pool.get('ekd.balances.analytic')
                balance_party = self.pool.get('ekd.balances.party')
                company_obj = self.pool.get('company.company')

                # Create analytic account in balance_analytic
                for project in self.browse(ids):
                        balance_ids = balance_analytic.search([
                                    ('account','=', company_obj.browse(project.company.id).project_revenue.id),
                                    ('model_ref','=', 'ekd.project,%s'%(project.id))
                                    ])
                        if balance_ids:
                            balance_analytic.write(balance_ids, {
                                            'state': 'draft',
                                            'active':True
                                            })

                        if not project.balance_revenue:
                            self.write(project.id, {
                                'balance_revenue': balance_party.create({
                                            'account': company_obj.browse(project.company.id).project_revenue.id,
                                            'model_ref':"ekd.project,%s"%(project.id),
                                            'state': 'draft',
                                            }),
                                            })
                        else:
                            balance_party.write(project.balance_revenue.id,{
                                            'state': 'draft',
                                            'active':True
                                            })

        return self.write(ids, {
                        'state': 'draft',
                        })

    def done(self, ids):
        balance_analytic = self.pool.get('ekd.balances.analytic')
        balance_party = self.pool.get('ekd.balances.party')
        company_obj = self.pool.get('company.company')
        # Deactivate balance_*
        for project in self.browse(ids):
                balance_ids = balance_analytic.search([
                                    ('account','=', company_obj.browse(project.company).project_revenue.id),
                                    ('model_ref','=', 'ekd.project,%s'%(project.id))])
                if balance_ids:
                    balance_analytic.write(balance_ids, {
                                            'state': 'done',
                                            'active':False
                                            })
                if project.balance_revenue:
                    balance_party.write(project.balance_revenue.id, {
                                            'state': 'done',
                                            'active':False
                                            })
        return self.write(ids, {
                        'state': 'done',
                        })

    def running(self, ids):
        balance_analytic = self.pool.get('ekd.balances.analytic')
        balance_party = self.pool.get('ekd.balances.party')
        company_obj = self.pool.get('company.company')

        # Create analytic account in balance_analytic
        for project in self.browse(ids):
                balance_ids = balance_analytic.search([
                                    ('account','=', company_obj.browse(project.company.id).project_revenue.id),
                                    ('model_ref','=', 'ekd.project,%s'%(project.id))
                                    ])
                if balance_ids:
                    balance_analytic.write(balance_ids, {
                                            'state': 'draft',
                                            'active':True
                                            })

                if not project.balance_revenue:
                    self.write(project.id, {
                                'balance_revenue': balance_party.create({
                                            'account': company_obj.browse(project.company.id).project_revenue.id,
                                            'model_ref':"ekd.project,%s"%(project.id),
                                            'state': 'draft',
                                            }),
                                            })
                else:
                    balance_party.write(project.balance_revenue.id,{
                                            'state': 'draft',
                                            'active':True
                                            })
        return self.write(ids, {
                        'state': 'open',
                        })

    def cancelled(self, ids):
        balance_analytic = self.pool.get('ekd.balances.analytic')
        balance_party = self.pool.get('ekd.balances.party')
        company_obj = self.pool.get('company.company')
        # Deactivate balance_*
        for project in self.browse(ids):
                balance_ids = balance_analytic.search([
                                    ('account','=',company_obj.browse(project.company.id).project_revenue.id),
                                    ('model_ref','=', 'ekd.project,%s'%(project.id))])
                if balance_ids:
                    balance_analytic.write(balance_ids, {
                                            'state': 'done',
                                            'active':False
                                            })
                if project.balance_revenue:
                    balance_party.write(project.balance_revenue.id, {
                                            'state': 'done',
                                            'active':False
                                            })
        return self.write(ids, {
                        'state': 'cancelled',
                        })

    def pending(self, ids):
        return self.write(ids, {
                        'state': 'pending',
                        })

    def template(self, ids):
        return

#    def on_change_type_project(self, vals):
#        if vals.get('type_project'):
#            return "%s.%s.%s"%(vals.get('party'),vals.get('type_project'),str(ids))
#        return vals.get('code')

#    def on_change_party(self, vals,
#            context=None):
#        if vals.get('type_project'):
#            return "%s.%s.%s"%(vals.get('party'),vals.get('type_project'),str(ids))
#        return vals.get('code')

#    def on_change_with_party(self, vals,
#            context=None):
#        if vals.get('type_project'):
#            return "%s.%s.%s"%(vals.get('party'),vals.get('type_project'),str(ids))
#        return vals.get('code')

#    def on_change_with_code(self, vals,
#            context=None):
#        if vals.get('type_project'):
#            return "%s.%s.%s"%(vals.get('party'),vals.get('type_project'),str(ids))
#        return vals.get('code')

ProjectMain()

class ProjectMainProperty(ModelSQL, ModelView):
    "Project Main Property"
    _name = "ekd.project.property"
    _description = __doc__
    _rec_name = "name"

    project = fields.Many2One('ekd.project', 'Project')
    type_property = fields.Many2One('ekd.project.type.property','Property Type')
    type_value = fields.Selection([('integer','Number'), ('weight','Weight'), ('time','Time'), ('date','Date'), ('text','Note'),],"Type Value", required=True)
    name = fields.Char("Name", size=128, required=True)
    value = fields.Char("Value")
    uom = fields.Many2One('product.uom', "UoM")

ProjectMainProperty()


class SubProject(ModelSQL, ModelView):
    "Project Main"
    _name = "ekd.project.subproject"
    _table = "ekd_project"
    _description = __doc__
#    _inherits = {'ekd.project': 'project'}

    name = fields.Char("SubProject Name", size=256, required=True)
    code = fields.Char("Project Code", size=30, required=True)
    shortcut = fields.Char("SubProject shortcut", size=128, required=True)
    active = fields.Boolean('Active')
    type_project = fields.Many2One('ekd.project.type', 'Type Project')
#    type_user = fields.Many2One('ekd.project.type', 'Type Project')
    account = fields.Many2One('ekd.account','Account', help="Link this project to an account if you need financial management on projects. It enables you to connect projects with budgets, planning, cost and revenue analysis, timesheets on projects, etc.")
    analytic = fields.Many2One('ekd.account.analytic','Analytic Account', help="Link this project to an analytic account if you need financial management on projects. It enables you to connect projects with budgets, planning, cost and revenue analysis, timesheets on projects, etc.")
    priority = fields.Selection([(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5'),(6,'6'),(7,'7'),(8,'8'),(9,'9'),(10,'10')],'Priority')
    manager = fields.Many2One('company.employee', 'Project Manager')
    employee = fields.Many2One('company.employee', 'Supervisor')
    warn_employee = fields.Boolean('Warn Supervisor', help="If you check this field, the project manager will receive a request each time a task is completed by his team.")
#    budget = fields.One2Many('project.budget', 'project', "Project budget")
#    tasks = fields.One2Many('project.task', 'mainproject', "Project tasks")
#    events = fields.One2Many('project.event', 'mainproject', "Project events")
    parent = fields.Many2One('ekd.project', 'Parent Project')
    childs = fields.One2Many('ekd.project.subproject', 'parent', 'Child Project')
    start_date = fields.Date('Starting Date')
    end_date = fields.Date('Expected End')
    notes = fields.Text('Notes', help="Internal description of the project.")
    state = fields.Selection([('template', 'Template'), ('open', 'Running'), ('pending', 'Pending'), ('cancelled', 'Cancelled'), ('done', 'Done')], 'State', required=True, readonly=True)

    def default_active(self):
        return True

    def default_priority(self):
        return 5

    def default_start_date(self):
        return datetime.datetime.now()

    def default_state(self):
        return 'open'

SubProject()

class ProjectMember(ModelSQL, ModelView):
    "Project Member"
    _name = "ekd.project.members"
    _description = __doc__

    project = fields.Many2One('ekd.project', 'Project',
                ondelete='CASCADE', select=1)
    employee = fields.Many2One('company.employee', 'Employees', ondelete='RESTRICT',
                                select=1, required=True)
    hour = fields.Char('Hour')
    note = fields.Text('Notes')

ProjectMember()
