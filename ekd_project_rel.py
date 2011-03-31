# -*- coding: utf-8 -*-
"Project"
from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard
from trytond.backend import TableHandler

class ProjectMain(ModelSQL, ModelView):
    "Project Main"
    _name = "ekd.project"
    members = fields.Many2Many('ekd.project.members', 'project', 'employee', 'Project Members', help="Project's member. Not used in any computation, just for information purpose.")

ProjectMain()

class SubProject(ModelSQL, ModelView):
    "Project Main"
    _name = "ekd.project.subproject"
    _table = "ekd_project"
    members = fields.Many2Many('ekd.project.members', 'project', 'employee', 'Project Members', help="Project's member. Not used in any computation, just for information purpose.")

SubProject()

