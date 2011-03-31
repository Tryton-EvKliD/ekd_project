# -*- encoding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval

class Company(ModelSQL, ModelView):
    _name = 'company.company'

    cal_works = fields.Many2One('calendar.calendar', 'All calendar works ')
    cal_projects = fields.Many2One('calendar.calendar', 'All calendar project')
    project_revenue = fields.Many2One('ekd.account', 'Account Revenue of Project', domain=[('company','=', Eval('company'))])
    project_expense = fields.Many2One('ekd.account', 'Account Expense of Project', domain=[('company','=',Eval('company'))])

Company()
