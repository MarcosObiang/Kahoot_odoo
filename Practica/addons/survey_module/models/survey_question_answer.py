from odoo import fields,models,api

import logging

class SurveyQuestionAnswer(models.Model):
    _inherit = "survey.question.answer"

    @api.model
    def default_get(self, fields_list):
        _logger = logging.getLogger(__name__)


        res = super().default_get(fields_list)

        _logger.info("Valores predeterminados obtenidos del super(): %s", res)



        _logger.info("Contexto completo: %s", self.env.context)

        q_type = self.env.context.get('question_type')
        is_true_value_already_defined=self.env.context.get('is_true_value_already_defined')
        answer_count=self.env.context.get("answer_count")

        _logger.info("Valor del contexto 'question_type_context': %s", q_type)

        if q_type == 'true_or_false' and answer_count==0:
            res['value'] = "True"
            new_context=dict(self.env.context,is_true_value_already_defined='True')
            self=self.with_context(new_context)
        elif q_type == 'true_or_false' and answer_count>0:
            res['value'] = "False"
            _logger.info("Se estableció el valor 'False' porque ya se definió 'True'.")


        return res
    
