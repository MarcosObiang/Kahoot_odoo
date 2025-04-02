from odoo import models,api,fields


class KahootQuestion(models.Model):
    _inherit="survey.question"
    _description="Kahoot question"
    answer_true_or_false=fields.Boolean("True or false")

    question_type= fields.Selection(selection_add=[('true_or_false','True or false')],ondelete={'true_or_false': 'cascade'} )
