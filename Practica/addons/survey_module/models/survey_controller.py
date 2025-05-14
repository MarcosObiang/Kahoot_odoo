from odoo import http
from odoo.http import request
import json
from odoo.addons.survey.controllers.main import Survey  

class SurveyControllerInherit(Survey):

    @http.route('/play',type='json',auth='public' ,methods=['GET'],csrf=False)
    def play(self,**kwargs):

        return http.Response(
            json.dumps({
                'data':{
                    'message': 'Has accedido al controlador de kahoot sourvey, ale al play',
                }


            }),


            content_type='application/json;charset=utf-8',
            status=200,

        )
    



    @http.route('/survey/next_question/<string:survey_token>/<string:answer_token>', type='json', auth='public', website=True)
    def survey_next_question(self, survey_token, answer_token, **post):
        """ Override para manejar navegación condicional basada en respuestas """
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return {}, {'error': access_data['validity_code']}
        
        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']

        if answer_sudo.state == 'new' and answer_sudo.is_session_answer:
            answer_sudo._mark_in_progress()

        # Lógica condicional: buscar si la última pregunta respondida tiene una respuesta con salto
        last_question = answer_sudo.last_question_id or answer_sudo.last_displayed_page_id
        next_question = None
        if last_question:
            lines = answer_sudo.user_input_line_ids.filtered(lambda l: l.question_id == last_question)
            selected_answers = lines.mapped('suggested_answer_id')
            conditional_targets = selected_answers.filtered(lambda a: a.next_question_id).mapped('next_question_id')
            if conditional_targets:
                next_question = conditional_targets[0]
                survey_sudo.session_question_id = next_question  # fuerza mostrar esta pregunta

        # Llamamos a la lógica de renderizado estándar
        return {}, self._prepare_question_html(survey_sudo, answer_sudo, **post)

    