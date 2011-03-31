# -*- coding: utf-8 -*-

"Project"
import datetime
from trytond.model import ModelStorage, ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.wizard import Wizard
from trytond.backend import TableHandler
import logging


_MODEL_WORKS = [
    ('ekd.project.member','Member'),
    ('ekd.project.datas','Input Data'),
    ('ekd.project.control','Control Statement'),
    ('ekd.project.salary','Payroll Statement'),
]

class ProjectTasksType(ModelSQL, ModelView):
    "Project Type"
    _name = "ekd.project.tasks.type"
    _description = __doc__

    name = fields.Char("Type Name", size=128, required=True)
    code = fields.Char("Code Type", size=30, required=True)
    shortcut = fields.Char("Shortcut name", size=30, required=True)
    account = fields.Many2One('ekd.account','Account', help="Link this project to an account if you need financial management on projects. It enables you to connect projects with budgets, planning, cost and revenue analysis, timesheets on projects, etc.")
    analytic = fields.Many2One('ekd.account.analytic','Analytic Account', help="Link this project to an analytic account if you need financial management on projects. It enables you to connect projects with budgets, planning, cost and revenue analysis, timesheets on projects, etc.")
    start_date = fields.Date('Starting Date')
    end_date = fields.Date('Expected End')
    parent = fields.Many2One('ekd.project.type', 'Parent Type')
    childs = fields.One2Many('ekd.project.type', 'parent', 'Child Type')
    property = fields.Many2One('ekd.project.type.property','Property Type' )
    active = fields.Boolean('Active')

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

ProjectTasksType()

class ProjectTasksTypeProperty(ModelSQL, ModelView):
    "Project Type"
    _name = "ekd.project.tasks.type.property"
    _description = __doc__

    type = fields.Many2One('ekd.project.type','Type Project' )
    name = fields.Char("Name", size=128, required=True)
    type_value = fields.Selection([('integer','Number'), ('weight','Weight'), ('time','Time'), ('date','Date'), ('text','Note'),],"Type Name", required=True)
    uom = fields.Many2One('product.uom', "UoM")
    active = fields.Boolean('Active')

ProjectTasksTypeProperty()

class ProjectEvents(ModelSQL, ModelView):
    "Project Events"
    _name = "ekd.project.events"
    _description = __doc__
    _rec_name = "name"
    _inherits={'calendar.event':'event'}

    event =  fields.Many2One('calendar.event', 'Calendar Event')
    project =  fields.Many2One('ekd.project', 'Project')
    employee =  fields.Many2One('company.employee', 'Assigned to', required=True)

    def create(self, vals):
        later = {}
        vals = vals.copy()
        company = self.pool.get('ekd.project').browse(vals['project']).company
        employee = self.pool.get('company.employee').browse(vals['employee'])
        if employee.calendar:
            vals['calendar'] = employee.calendar.id
        elif company.cal_projects:
            vals['calendar'] = company.cal_projects.id
        else:
            vals['calendar'] = False

        for field in vals:
                if field in self._columns\
                and hasattr(self._columns[field], 'set'):
                    later[field] = vals[field]
        for field in later:
            del vals[field]
        cursor = Transaction().cursor
        if cursor.nextid(self._table):
            cursor.setnextid(self._table, cursor.currid('ekd_project_events'))

        new_id = super(ProjectEvents, self).create(vals)
        event = self.browse(new_id)
        new_id = event.event.id
        cursor.execute('UPDATE "' + self._table + '" SET id = %s '\
                        'WHERE id = %s', (event.event.id, event.id))
        ModelStorage.delete(self, event.id)
        self.write(new_id, later)
        res = self.browse(new_id)
        return res.id

ProjectEvents()

class ProjectTasks(ModelSQL, ModelView):
    "Project Tasks"
    _name = "ekd.project.tasks"
    _description = __doc__
    _rec_name = "name"
    _inherits={'calendar.todo':'todo'}

    todo =  fields.Many2One('calendar.todo', 'Calendar Todo')
    project =  fields.Many2One('ekd.project', 'Project')
    priority = fields.Selection([
            ('4','Very Low'),
            ('3','Low'),
            ('2','Medium'),
            ('1','Urgent'),
            ('0','Very urgent')], 'Importance', 
            on_change=['priority'], required=True, select=1)
    type =  fields.Many2One('ekd.project.tasks.type', 'Type')
    childs =  fields.One2Many('ekd.project.tasks', 'parent', 'Delegated Tasks')
    planned_hours =  fields.Float('Planned Hours', required=True)
    remaining_hours =  fields.Float('Remaining Hours', digits=(16,4))
    employee =  fields.Many2One('company.employee', 'Assigned to', required=True)
    party =  fields.Many2One('party.party', 'Assigned to Party')
    works =  fields.One2Many('ekd.project.tasks.works', 'task', 'Work done')
    state =  fields.Selection([
                ('draft', 'Draft'),
                ('open', 'In Progress'),
                ('pending', 'Pending'),
                ('cancelled', 'Cancelled'),
                ('done', 'Done')], 'State', required=True )
    active = fields.Boolean('Active')

    def default_get(self, fields, with_rec_name=True):
        context = Transaction().context
        res = super(ProjectTasks, self).default_get(fields, with_rec_name=True)
        #res['performer'] = context.get('performer') or False
        res['state'] = context.get('state') or 'draft'
        res['employee'] = context.get('employee') or False
        #res['start_date'] = context.get('start_date') or datetime.datetime.now()
        res['priority'] = context.get('priority') or '2'
        res['active'] = context.get('active') or True

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
    def on_change_priority(self, vals):
        return vals

    def create(self, vals):
        later = {}
        vals = vals.copy()
        company = self.pool.get('ekd.project').browse(vals['project']).company
        employee = self.pool.get('company.employee').browse(vals['employee'])
        if employee.calendar:
            vals['calendar'] = employee.calendar.id
        elif company.cal_projects:
            vals['calendar'] = company.cal_projects.id
        else:
            vals['calendar'] = False

        for field in vals:
                if field in self._columns\
                and hasattr(self._columns[field], 'set'):
                    later[field] = vals[field]
        for field in later:
            del vals[field]
        cursor = Transaction().cursor
        if cursor.nextid(self._table):
            cursor.setnextid(self._table, cursor.currid('ekd_project_tasks'))
        new_id = super(ProjectTasks, self).create(vals)
        task = self.browse(new_id)
        new_id = task.todo.id
        cursor.execute('UPDATE "' + self._table + '" SET id = %s '\
                        'WHERE id = %s', (task.todo.id, task.id))
        ModelStorage.delete(self, task.id)
        self.write(new_id, later)
        res = self.browse(new_id)
        return res.id

ProjectTasks()

class ProjectWork(ModelSQL, ModelView):
    "Tasks Work"
    _name = "ekd.project.tasks.works"
    _description = __doc__

    name = fields.Char('Work summary', size=128)
    date = fields.DateTime('Date')
    task = fields.Many2One('ekd.project.tasks', 'Task', required=True)
    hours = fields.Float('Time Spent')
    employee = fields.Many2One('company.employee', 'Done by', required=True)
    model_ref = fields.Reference(string='Reference by model', selection=_MODEL_WORKS,  required=True)
    notes = fields.Text('Notes')

#    _order = "date desc"

#    def create(self, vals, *args, **kwargs):
#        if 'hours' in vals and (not vals['hours']):
#            vals['hours'] = 0.00
#        if 'task_id' in vals:
#            cr.execute('update project_task set remaining_hours=remaining_hours - %s where id=%s', (vals.get('hours', Decimal('0.0')), vals['task_id']))
#        return super(project_work,self).create(vals, *args, **kwargs)

#    def write(self, ids,vals,context={}):
#        if 'hours' in vals and (not vals['hours']):
#            vals['hours'] = 0.00
#        if 'hours' in vals:
#            for work in self.browse(ids):
#                cr.execute('update project_task set remaining_hours=remaining_hours - %s + (%s) where id=%s', (vals.get('hours',0.0), work.hours, work.task_i
#        return super(project_work,self).write(ids, vals)

#    def delete(self, ids, *args, **kwargs):
#        for work in self.browse(ids):
#            cr.execute('update project_task set remaining_hours=remaining_hours + %s where id=%s', (work.hours, work.task_id.id))
#        return super(project_work,self).unlink(ids,*args, **kwargs)

ProjectWork()
