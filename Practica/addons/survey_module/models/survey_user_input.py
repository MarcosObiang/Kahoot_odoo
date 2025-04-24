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
