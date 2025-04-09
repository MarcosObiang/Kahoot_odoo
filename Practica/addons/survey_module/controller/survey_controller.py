from odoo import http
from odoo.http import request


class SurveyController(http.Controller):

    @http.route('/play',type='http',auth='public' website=True)
    def play(self,**kwargs):

        return 'Hello wolrd'
    