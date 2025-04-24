
from odoo import models, fields, api


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'
    _description = 'Survey User Input Line'

    # Add a new field to store the answer score
    score = fields.Integer(string='Answer Score', default=0)
    response_time = fields.Integer(string='Response Time', default=0)
    @api.onchange('answer_score')
    def _onchange_answer_score(self):
        # This method will be triggered when the answer_score field changes
        if self.score < 0:
            self.score = 0



def compute_line_score(self):
    self.ensure_one()
    question = self.question_id
    if not question:
        return 0
    base = question.points or 0
    bonus = (question.bonus_per_second or 0) * max(0, (question.time_limit or 0) - (self.response_time or 0))
    score = base + bonus
    self.answer_score = score
    return score
