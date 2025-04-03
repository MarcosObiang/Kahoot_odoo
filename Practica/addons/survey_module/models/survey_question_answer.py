from odoo import fields,models,api

import logging

class SurveyQuestionAnswer(models.Model):
    _inherit = "survey.question.answer"

    @api.model
    def default_get(self, fields_list):
        # Creamos un logger para imprimir mensajes
        _logger = logging.getLogger(__name__)


        # Llamada al super para obtener los valores predeterminados
        res = super().default_get(fields_list)

        # Log para ver el valor de res antes de cualquier modificación
        _logger.info("Valores predeterminados obtenidos del super(): %s", res)



        # Verificando el contexto completo
        _logger.info("Contexto completo: %s", self.env.context)

        # Accediendo al contexto
        q_type = self.env.context.get('question_type')
        is_true_value_already_defined=self.env.context.get('is_true_value_already_defined')
        answer_count=self.env.context.get("answer_count")

        # Log para ver qué valor tiene el contexto
        _logger.info("Valor del contexto 'question_type_context': %s", q_type)

        # Si el tipo de pregunta es 'true_or_false', establece el valor predeterminado
        if q_type == 'true_or_false' and answer_count==0:
            res['value'] = "True"
            new_context=dict(self.env.context,is_true_value_already_defined='True')
            self=self.with_context(new_context)
        elif q_type == 'true_or_false' and answer_count>0:
            res['value'] = "False"
            _logger.info("Se estableció el valor 'False' porque ya se definió 'True'.")


        return res
