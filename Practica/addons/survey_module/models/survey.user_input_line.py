
from odoo import models, fields, api


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'
    _description = 'Survey User Input Line'

    # Add a new field to store the answer score
    answer_score = fields.Integer(string='Answer Score', default=0)

    @api.onchange('answer_score')
    def _onchange_answer_score(self):
        # This method will be triggered when the answer_score field changes
        if self.answer_score < 0:
            self.answer_score = 0

    @api.model
    def compute_total_score(self):
        total_score = 0

        question_ids = self.mapped('question_id')

        points=question_ids.mapped('points')
        bonus_per_second=question_ids.mapped('bonus_per_second')
        time_limit=question_ids.mapped('time_limit')
        response_time=question_ids.mapped('response_time')
        total_score=points+bonus_per_second*(time_limit-response_time)
        
        return total_score