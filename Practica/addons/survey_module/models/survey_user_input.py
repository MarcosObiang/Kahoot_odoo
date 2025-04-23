from odoo import models,api,fields, _


class KahootUserInput(models.Model):
    _inherit="survey.user_input"

    _description = "Kahoot User Input"
    user_total_score=fields.Float(string="User Total Score",default=0)
    leaderboard_position=fields.Integer(string="Leaderboard Position",default=10)



    @api.model
    def get_total_user_score(self):
        """
        This method calculates the total score for the user based on the answers provided.
        It iterates through the user input lines and sums up the scores.
        """
        total_score = 0
        # Iterate through each user input line
        for line in self.user_input_line_ids:
            # Add the answer score to the total score
            total_score += line.answer_score

        # Update the user_total_score field with the calculated total score
        self.user_total_score = total_score



