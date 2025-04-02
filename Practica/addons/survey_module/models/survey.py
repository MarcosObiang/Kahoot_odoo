from odoo import fields,api,models


class KahootSurvey(models.Model):
    _description="A cool survey"
    _inherit="survey.survey"