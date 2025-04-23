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
    