from odoo import models,api,fields
from odoo.exceptions import ValidationError

import logging

class KahootQuestion(models.Model):
    _inherit="survey.question"
    _description="Kahoot question"
    answer_true_or_false=fields.Boolean("True or false")
    question_type= fields.Selection(selection_add=[('true_or_false','True or false')],ondelete={'true_or_false': 'cascade'} )
    answer_count=fields.Integer("Answers count", default=0)

 

    @api.onchange("question_type")

    def on_question_type_changed(self):
         
        _logger = logging.getLogger(__name__)
        new_context = dict(self.env.context, question_type=self.question_type)
        self = self.with_context(new_context)
        _logger.info("Este es el contexto tras cambiarlo %s", self.env.context)

        return



    @api.onchange('suggested_answer_ids')
    def _onchange_suggested_answers(self):
        _logger = logging.getLogger(__name__)

        if self.question_type=='true_or_false':

            self.answer_count = len(self.suggested_answer_ids)
            _logger.info(f"Pregunta {self.id} tiene {self.answer_count} respuestas sin guardar.")
        else:
            self.answer_count=0







    @api.constrains('suggested_answer_ids')
    def _check_answer_count(self):
        # Validamos que no haya más de 2 registros en el campo One2many
        for record in self:
            if len(record.suggested_answer_ids) > 2:
                raise ValidationError("No puedes agregar más de dos opciones en este campo de respuestas.")
