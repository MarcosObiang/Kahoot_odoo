from odoo import models,api,fields, _





class KahootUserInput(models.Model):
    _inherit = "survey.user_input"

    _description = "Kahoot User Input"
    
    user_total_score = fields.Float(string="User Total Score", default=0)
    leaderboard_position = fields.Integer(string="Leaderboard Position", default=10)

def get_total_user_score(self):
  
    for user_input in self:
        total = 0
        for line in user_input.user_input_line_ids:
            total += line.compute_line_score()
        user_input.user_total_score = total
    return total



def _mark_done(self):
        res = super()._mark_done()

        for user_input in self:
            survey = user_input.survey_id
            # Verificamos si todos los intentos para esta encuesta están completados
            all_inputs = self.env['survey.user_input'].search([('survey_id', '=', survey.id)])
            if all(i.state == 'done' for i in all_inputs):
                # Si todos completaron, calculamos el ranking
                self.env['survey.session_ranking'].compute_ranking(survey.id)

        return res