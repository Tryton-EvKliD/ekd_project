# -*- coding: utf-8 -*-
#
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
"Budget"
from trytond.model import ModelView, ModelSQL, fields
from trytond.transaction import Transaction
# Бюджеты
class Budget(ModelSQL, ModelView):
    _name = 'ekd.account.budget'

    project_budget = fields.Boolean('Project')
    project = fields.Function(fields.Many2One('ekd.project','Project'), 
                                'get_project', searcher='search_project')

    def default_project_budget(self):
        return Transaction().context.get('project_budget') or False

    def get_project(self, ids, name):
        #project_obj = self.pool.get('ekd.project')
        #for budget in self.browse
        res={}.fromkeys(ids, False)
        cursor = Transaction().cursor
        cursor.execute('SELECT id, budget '\
                       'FROM ekd_project '\
                       'WHERE budget in ('+','.join(map(str, ids))+')')
        for line in cursor.fetchall():
            res[line[1]] = line[0]
        return res

    def search_project(self, name, clause):
        raise Exception(name, str(clause))
        return []

Budget()

class BudgetLine(ModelSQL, ModelView):
    _name = 'ekd.account.budget.line'

    project = fields.Function(fields.Many2One('ekd.project','Project'), 'get_project')

    def get_project(self, ids, name):
        #project_obj = self.pool.get('ekd.project')
        res={}.fromkeys(ids, False)
        for line in self.browse(ids):
            if line.budget.project:
                res[line.id] = line.budget.project.id
        return res

BudgetLine()
