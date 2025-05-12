from odoo import fields,api,models


class KahootSurvey(models.Model):
    _description="A cool survey"
    _inherit="survey.survey"




    
    
    def _get_session_next_question(self, go_back):
        self.ensure_one()
        
        if not self.question_ids or not self.env.user.has_group('survey.group_survey_user'):
            return

        most_voted_answers = self._get_session_most_voted_answers()

        for answer in most_voted_answers:
            if answer.next_question_id and answer.next_question_id in self.question_ids:
                return answer.next_question_id

        return self._get_next_page_or_question(
            most_voted_answers,
            self.session_question_id.id if self.session_question_id else 0,
            go_back=go_back
        )
