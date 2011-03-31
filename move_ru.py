# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################
'MoveRU'
from trytond.model import ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.pyson import In, If, Get, Eval, Not, Equal, Bool, Or, And

_MOVE_STATES = {
    'readonly': Equal(Eval('state'), 'posted'),
        }
_MOVE_DEPENDS = ['state', 'date_operation']

class MoveRU(ModelSQL, ModelView):
    _name="ekd.account.move"
    _description=__doc__

    project = fields.Many2One('ekd.project', 'Project')
    lines = fields.One2Many('ekd.account.move.line', 'move', 'Account Entry Lines',
            states=_MOVE_STATES, depends=_MOVE_DEPENDS,
            context={'company': Eval('company'), 'date_operation': Eval('date_operation'), 
            'ct_party':Eval('from_party'), 'dt_party':Eval('to_party'), 'amount':Eval('amount'), 'project':Eval('project')})

    def default_project(self):
        return Transaction().context.get('project') or False

MoveRU()
