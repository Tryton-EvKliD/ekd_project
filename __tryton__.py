# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name': 'Project',
    'name_ru_RU': 'Учет проектов',
    'name_de_DE': 'Projekte',
    'name_es_CO': 'Proyectos',
    'name_es_ES': 'Proyecto',
    'name_fr_FR': 'Projet',
    'version': '1.8.0',
    'author': 'Dmitry Klimanov',
    'email': 'k-dmitry2@narod.ru',
    'website': 'http://www.tryton.org/',
    'description': '''Project Module with:
    - Project management
''',
    'description_ru_RU': '''Модуль учета проектов 
''',
    'description_de_DE': '''Projektmodul für:
    - Projektverwaltung
''',
    'description_es_CO': '''Módulo de proyectos con:
    - Gestión de proyectos
''',
    'description_es_ES': '''Módulo de proyecto con:
    - Gestión de proyecto
''',
    'description_fr_FR': '''Module projet avec:
    - Gestion de projet
''',
    'depends': [
        'ir',
        'calendar',
        'calendar_todo',
        'ekd_system',
        'ekd_party',
        'ekd_company',
        'ekd_account',
        'ekd_documents',
        'ekd_budget',
    ],
    'xml': [
        'xml/ekd_project_view.xml',
        'xml/ekd_project_type.xml',
        'xml/ekd_subproject_view.xml',
        'xml/ekd_project_journal.xml',
        'xml/ekd_project_task.xml',
        'xml/ekd_project_task_type.xml',
        'xml/ekd_budget.xml',
        'xml/ekd_project_reports.xml',
        'xml/ekd_system.xml',
        #'xml/move_ru.xml',
        'xml/ekd_company.xml',
        #'xml/work.xml',
    ],
    'translation': [
        'ru_RU.csv',
#        'de_DE.csv',
#        'es_CO.csv',
#        'es_ES.csv',
#        'fr_FR.csv',
    ],
}
