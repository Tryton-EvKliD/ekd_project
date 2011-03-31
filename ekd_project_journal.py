# -*- coding: utf-8 -*-
"Project"
from trytond.model import ModelView, ModelSQL, fields

class ProjectJournal(ModelSQL, ModelView):
    "Project Journals"
    _name = "ekd.project.journal"

    project = fields.Many2One('ekd.project', 'Project')
    name = fields.Char('Name')
    active = fields.Boolean('Active')
    note = fields.Text('Note')
    line = fields.One2Many('ekd.project.journal.line', 'journal', 'Employees on the project')
    recruitment = fields.Function(fields.Integer('Recruitment'),'get_fields')
    distrib_task = fields.Function(fields.Integer('Distrib Tasks'),'get_fields')
    return_task = fields.Function(fields.Integer('Return of Tasks'),'get_fields')
    return_data = fields.Function(fields.Integer('Return of Data'),'get_fields')
    control_data = fields.Function(fields.Integer('Control of Data'),'get_fields')
    error_data = fields.Function(fields.Integer('Error of Data'),'get_fields')
    state = fields.Selection([
            ('draft','Draft'),
            ('open','Opened'),
            ('close','Closed'),
            ], 'State')

    def default_state(self):
        return 'draft'

    def default_active(self):
        return True

    def get_fields(self, ids, field):
        res={}.fromkeys(ids, 0)
        for journal in self.browse(ids):
#            for field in fields:
                if field == 'distrib_task':
                    for line in journal.line:
                        res[journal.id] += line.distrib_task
                elif field == 'return_task':
                    for line in journal.line:
                        res[journal.id] += line.return_task
                elif field == 'return_data':
                    for line in journal.line:
                        res[journal.id] += line.return_data
                elif field == 'control_data':
                    for line in journal.line:
                        res[journal.id] += line.control_data
                elif field == 'error_data':
                    for line in journal.line:
                        res[journal.id] += line.error_data
        return res

ProjectJournal()

class ProjectJournalLine(ModelSQL, ModelView):
    "Project Journal"
    _name = "ekd.project.journal.line"

    journal = fields.Many2One('ekd.project.journal', 'Journal of Psroject')
    employee = fields.Many2One('company.employee', 'Peripatetic')
    plan_date = fields.Date('Plan date', help=u'Планируемая дата выдачи задания')
    distrib_task = fields.Integer('Distrib Tasks')
    return_task = fields.Integer('Return of Tasks')
    return_data = fields.Integer('Return of Data')
    control_data = fields.Integer('Control of Data')
    error_data = fields.Integer('Error of Data')
    note = fields.Text('Note')
    state = fields.Selection([
            ('recruitment','Recruitment'),
            ('distrib_task','Distrib Tasks'),
            ('work','Work'),
            ('return_tasks','Return Task'),
            ('close','Closed'),
            ], 'State')

ProjectJournalLine()
'''
# Набор персонала
class ProjectJournalsRecruitment(ModelSQL, ModelView):
    "Project Journals Recruitment"
    _name = "ekd.project.journals.recruitment"
    _inherits = {'ekd.project.journal': 'journal'}

    journal = fields.Many2One('ekd.project.journal', 'Journal of Project')
    name = fields.Char('Name')
    active = fields.Boolean('Active')
    note = fields.Text('Note')
    state = fields.Selection([
            ('draft','Draft'),
            ('open','Opened'),
            ('close','Closed'),
            ], 'State')

ProjectJournalsRecruitment()

class ProjectJournalsRecruitmentLine(ModelSQL, ModelView):
    "Project Journals Recruitment"
    _name = "ekd.project.journals.recruitment.line"
    _inherits = {'ekd.project.journal.line': 'journal_line'}

    journal_line = fields.Many2One('ekd.project.journal.line', 'Journal of Project line')
    plan_date = fields.Date('Plan date', help='Планируемая дата выдачи задания')
    note = fields.Text('Note')
    state = fields.Selection([
            ('recruitment','Recruitment'),
            ('distrib_task','Distrib Tasks'),
            ('return_tasks','Return Task'),
            ('close','Closed'),
            ], 'State')

ProjectJournalsRecruitment()

# Распределение заданий
class ProjectJournalsDistribTasks(ModelSQL, ModelView):
    "Project Journals distribution of tasks"
    _name = "ekd.project.journals.distrib_tasks"
    _inherits = {'ekd.project.journal': 'journal'}

    journal = fields.Many2One('ekd.project.journal', 'Journal of Project')

ProjectJournalsDistribTasks()

class ProjectJournalsDistribTasksLine(ModelSQL, ModelView):
    "Project Journals distribution of tasks"
    _name = "ekd.project.journals.distrib_tasks.line"
    _inherits = {'ekd.project.journal.line': 'journal_line'}

    journal_line = fields.Many2One('ekd.project.journal.line', 'Journal of Project line')

ProjectJournalsDistribTasks()

# Возврат невыполненых заданий
class ProjectJournalsReturnTasks(ModelSQL, ModelView):
    "Project Journals return of tasks"
    _name = "ekd.project.journals.return_tasks"

    project = fields.Many2One('ekd.project', 'Project Members')

ProjectJournalsReturnTasks()

# Сдача выполненых заданий
class ProjectJournalsReturnData(ModelSQL, ModelView):
    "Project Journals return of data"
    _name = "ekd.project.journals.return_data"
    _inherits = {'ekd.project.journal': 'journal'}

    journal = fields.Many2One('ekd.project.journal', 'Journal of Project')

ProjectJournalsReturnData()

# Ввод данных выполненых заданий
class ProjectJournalsInputData(ModelSQL, ModelView):
    "Project Journals Input data"
    _name = "ekd.project.journals.input_data"
    _inherits = {'ekd.project.journal': 'journal'}

    journal = fields.Many2One('ekd.project.journal', 'Journal of Project')

ProjectJournalsInputData()

# Ввод данных выполненых заданий
class ProjectJournalsControlData(ModelSQL, ModelView):
    "Project Journals Control Input data"
    _name = "ekd.project.journals.control"
    _inherits = {'ekd.project.journal': 'journal'}

    journal = fields.Many2One('ekd.project.journal', 'Journal of Project')

ProjectJournalsControlData()
'''
