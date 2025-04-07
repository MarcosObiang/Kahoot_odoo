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
            res["answer_score"]=100


            new_context=dict(self.env.context,is_true_value_already_defined='True')
            self=self.with_context(new_context)
        elif q_type == 'true_or_false' and answer_count>0:
            res['value'] = "False"
            res["answer_score"]=-100
            _logger.info("Se estableció el valor 'False' porque ya se definió 'True'.")


        return res
    




    def _get_answer_matching_domain(self, row_id=False):
        self.ensure_one()
        if self.question_type == "matrix":
            return ['&', '&', ('question_id', '=', self.question_id.id), ('matrix_row_id', '=', row_id), ('suggested_answer_id', '=', self.id)]
        elif self.question_type in ('multiple_choice', 'simple_choice','true_or_false'):
            return ['&', ('question_id', '=', self.question_id.id), ('suggested_answer_id', '=', self.id)]
        return []