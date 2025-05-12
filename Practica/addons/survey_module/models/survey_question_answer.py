from odoo import fields,models,api

import logging

class SurveyQuestionAnswer(models.Model):
    _inherit = "survey.question.answer"

    next_question_id = fields.Many2one(
    'survey.question',
    string="Siguiente pregunta condicional"
)


   
    @api.model
    def default_get(self, fields_list):
        _logger = logging.getLogger(__name__)


        res = super().default_get(fields_list)

        _logger.info("Valores predeterminados obtenidos del super(): %s", res)



        _logger.info("Contexto completo: %s", self.env.context)

        is_true_or_false = self.env.context.get('answer_true_or_false')
        is_true_value_already_defined=self.env.context.get('is_true_value_already_defined')
        answer_count=self.env.context.get("answer_count")

        _logger.info("Valor del contexto 'question_type_context': %s", str(is_true_or_false))

        if is_true_or_false ==True and answer_count==0:
            res['value'] = "True"
            res["answer_score"]=100


            new_context=dict(self.env.context,is_true_value_already_defined='True')
            self=self.with_context(new_context)
        elif is_true_or_false ==True and answer_count>0:
            res['value'] = "False"
            res["answer_score"]=-100
            _logger.info("Se estableció el valor 'False' porque ya se definió 'True'.")


        return res
    
    @api.model
    def compute_total_score(self):


        self.answer_score=self.environment['survey.user_input_line'].compute_total_score()
