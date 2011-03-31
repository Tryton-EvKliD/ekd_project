# -*- encoding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
"Balances Accounting"
from trytond.model import ModelView, ModelSQL, fields

#
# Остатки по счетам за периоды (Дебиторская и кредиторская задолжность)
#
class BalancePartner(ModelSQL, ModelView):
    _name = "ekd.balances.party"

    project = fields.Many2One('ekd.project', 'Project', select=2)

    def post_balance(self, values=None):
        '''
         Изменение остатка и оборота в учетном регистре счета
            values = {'company': ID учетной организации,
                      'date_operation': Дата операции,
                      'period': Дата операции,
                      'account': ID счета,
                      'analytic': ID аналитического счета,
                      'party': ID организации,
                      'documents_ref': ссылка на документ - (Наименование объекта,ID документа),
                      'project': ID Проекта,
                      'debit': сумма, }
                      'credit': сумма, }
                      'currency': Валюта поля сумма, }
        '''
        if values = None:
            return False

BalancePartner()

#
# Остатки по счетам за периоды (Дополнительная аналитика)
#
class BalanceAnalytic(ModelSQL, ModelView):
    _name = "ekd.balances.analytic"

    project = fields.Many2One('ekd.project', 'Projct', select=2)

    def post_balance(self, values=None):
        '''
         Изменение остатка и оборота в учетном регистре аналитическом счете
            values = {'company': ID учетной организации,
                      'period': Учетный период,
                      'account': ID счета,
                      'project': ID Проекта,
                      'analytic': ID аналитического счета,
                      'product': ID ТМЦ или услуги,
                      'product_uom': ID Ед.измерения ТМЦ или услуги,
                      'quantity': Кол-во,
                      'amount': сумма, }
                      'currency': Валюта поля сумма, }
                      'amount_currency': сумма в дополнительной валюте, }
                      'second_currency': Валюта дополнительного поля суммы, }
        '''
        if values = None:
            return False
        analytic_id = self.search([
                            ('company','=',values.get('company')),
                            ('period','=',values.get('period')),
                            ('account','=',values.get('account')),
                            ('analytic','=',values.get('analytic')),
                            ('currency','=',values.get('currency')),
                            ])
        if analytic_id:
            cr.exec('update "' + self._table + '" set debit +=%s where id=%s', (values.get('amount'), analytic_id))
        else
            cr.exec('insert into "' + self._table + '" (company, period, account, analytic, debit, currency) values(%s,%s,%s,%s,%s,%s)',
                (values.get('company'), values.get('period'), values.get('account'), values.get('analytic'), values.get('debit'), values.get('currency'),))

BalanceAnalytic()
