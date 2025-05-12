from odoo import http
from odoo.http import request
import json

class SurveyController(http.Controller):

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
    
    @http.riute('/get-question-ime-limit',type='json',auth='public' ,methods=['GET'],csrf=False)
    def get_question_time_limit(self,**kwargs):
        question_id=kwargs.get('question_id')
        question=self.env['survey.question'].browse(question_id)
        time_limit=question.time_limit
        return http.Response(
            json.dumps({
                'data':{
                    'time_limit': time_limit,
                }


            }),


            content_type='application/json;charset=utf-8',
            status=200,

        )
    