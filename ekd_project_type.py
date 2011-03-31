# -*- coding: utf-8 -*-
"Project"
import datetime
from trytond.model import ModelStorage, ModelView, ModelSQL, fields
from trytond.wizard import Wizard
from trytond.backend import TableHandler
from decimal import Decimal
import logging

_RUNNING_STATES = {
    'readonly': "state =='open'",
    }

_RUNNING_DEPENDS = ['state']

_LINE_STATES = {
    'readonly': "state == 'empty'",
    }

_LINE_DEPENDS = ['state']

class ProjectType(ModelSQL, ModelView):
    "Project Type"
    _name = "ekd.project.type"
    _description = __doc__
    _rec_name = "name_full"

    name = fields.Char("Type Name", size=128, required=True)
    name_full = fields.Function(fields.Char('Name Full'), 'get_name_full', searcher='search_name')
    code = fields.Char("Code Type", size=30, readonly=True, on_change=['parent'])
    code_full = fields.Function(fields.Char('Code Full'), 'get_code_full', searcher='search_code')
    shortcut = fields.Char("Shortcut name", size=64, required=True)
    account = fields.Many2One('ekd.account','Account', help="Link this project to an account if you need financial management on projects. It enables you to connect projects with budgets, planning, cost and revenue analysis, timesheets on projects, etc.")
    analytic = fields.Many2One('ekd.account.analytic','Analytic Account', help="Link this project to an analytic account if you need financial management on projects. It enables you to connect projects with budgets, planning, cost and revenue analysis, timesheets on projects, etc.")
    start_date = fields.Date('Starting Date')
    end_date = fields.Date('Expected End')
    parent = fields.Many2One('ekd.project.type', 'Parent Type')
    childs = fields.One2Many('ekd.project.type', 'parent', 'Child Type')
    property = fields.One2Many('ekd.project.type.property', 'type', 'Property Type' )
    notes_model = fields.Text("Notes Model")
    metod_selection = fields.Text("Metod")
    active = fields.Boolean('Active')

    def __init__(self):
        super(ProjectType, self).__init__()
#        self._sql_constraints = [
#                ('code_uniq', 'UNIQUE(code)', 'The code of the type project must be unique!'),
#                ('name_uniq', 'UNIQUE(name)', 'The Name of the type project must be unique!'),
#                            ]
        self._order.insert(0, ('code', 'ASC'))
        self._order.insert(0, ('name', 'ASC'))

    def default_start_date(self):
        return datetime.datetime.now()

    def get_rec_name(self, ids, name):
        if not ids:
            return
        res={}
        for ProjectTypeObj in self.browse(ids):
            if ProjectTypeObj.shortcut:
                res[ProjectTypeObj.id] = ProjectTypeObj.shortcut
            else:
                res[ProjectTypeObj.id] = ProjectTypeObj.name
        return res

    def search_rec_name(self, name, args):
        args2 = []
        ids = self.search([
                ('name', args[1], args[2]),
                ])
        if ids:
            return [('id', 'in', ids)]
        return [(self._rec_name,) + clause[1:]]

    def search_name(self, name, args):
        args2 = []
        ids = self.search([
                ('name', args[1], args[2]),
                ])
        if ids:
            return [('id', 'in', ids)]
        return []

    def search_code(self, name, args):
        args2 = []
        i = 0
        while i < len(args):
            ids = self.search([
                ('code', args[i][1], args[i][2]),
                ])
            args2.append(('id', 'in', ids))
            i += 1
        return args2

    def get_name_full(self, ids, name):
        if not ids:
            return {}
        res = {}
        def _name(type_project):
            if type_project.id in res:
                return res[type_project.id]
            elif type_project.parent:
                return '%s-%s'%(_name(type_project.parent), type_project.shortcut)
            elif not type_project.parent:
                return ''
            else:
                return type_project.shortcut

        for type_project in self.browse(ids):
            if type_project.parent:
                res[type_project.id] = _name(type_project)
            else:
                res[type_project.id] = type_project.shortcut
        sorted(res)
        return res

    def get_code_full(self, ids, name):
        if not ids:
            return {}
        res = {}
        def _code(type_project):
            if type_project.id in res:
                return res[type_project.id]
            elif type_project.parent:
                return '%s.%s'%(_code(type_project.parent), type_project.id)
            else:
                return type_project.id

        for type_project in self.browse(ids):
            res[type_project.id] = _code(type_project)
        #raise Exception(str(res))
        return res
#	XX.XXX.XXX.XXX...
#    def on_change_code
#    def on_change_parent

    def create(self, vals):
        new_id = super(ProjectType, self).create(vals)
        type_prj = self.browse(new_id)
        if type_prj.parent:
            self.write(new_id, {'code': type_prj.code_full})
        else:
            self.write(type_prj.id, {'code': str(type_prj.id)})
        return new_id

    def write(self, ids, vals):
        if isinstance(ids, list):
            ids = ids[0]
        type_prj = self.browse(ids)
        vals['code'] = type_prj.code_full
        return super(ProjectType, self).write(ids, vals)
        

ProjectType()

class ProjectTypeProperty(ModelSQL, ModelView):
    "Project Type"
    _name = "ekd.project.type.property"
    _description = __doc__

    type = fields.Many2One('ekd.project.type','Type Project' )
    name = fields.Char("Name", size=128, required=True)
    type_value = fields.Selection([('integer','Number'), ('weight','Weight'), ('time','Time'), ('date','Date'), ('text','Note'),],"Type Name", required=True)
    uom = fields.Many2One('product.uom', "UoM")
    active = fields.Boolean('Active')

ProjectTypeProperty()
