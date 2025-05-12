
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import float_round


"""Este modelo almace"""

class SurveySessionRanking(models.Model):
    _name = 'survey.session_ranking'
    _description = 'Survey Session Ranking'

    survey_id = fields.Many2one('survey.survey', required=True)
    user_input_id = fields.Many2one('survey.user_input', required=True)
    partner_id = fields.Many2one('res.partner', string="Usuario", related="user_input_id.partner_id")
    total_score = fields.Float("Total Score")
    rank_position = fields.Integer("Ranking Position")


    """
    Calcula el ranking de los usuarios para una encuesta dada.
    Llama al método `compute_total_score` de cada user_input para obtener su puntuación.
    """
    @api.model
    def compute_ranking(self, survey_id):

        user_inputs = self.env['survey.user_input'].search([('survey_id', '=', survey_id)])

        self.search([('survey_id', '=', survey_id)]).unlink()

        user_scores = []
        for user_input in user_inputs:
            total_score = user_input.compute_total_score() 
            user_scores.append((user_input, total_score))

        user_scores.sort(key=lambda x: x[1], reverse=True)

        rank_position = 1
        for user_input, total_score in user_scores:
            self.create({
                'survey_id': survey_id,
                'user_input_id': user_input.id,
                'partner_id': user_input.partner_id.id,
                'total_score': total_score,
                'rank_position': rank_position
            })
            rank_position += 1