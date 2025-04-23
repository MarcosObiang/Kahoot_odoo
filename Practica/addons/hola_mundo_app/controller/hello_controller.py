from odoo import http
from odoo.http import request
import json
class HolaMundoController(http.Controller):
    @http.route('/hola_mundo',auth='public',type="http")
    def hola_mundo_page(self,**kwargs):
        hola_mundo_model= request.env['hola.mundo'].sudo().search([],limit=1)
        mensaje_backend= hola_mundo_model.mensaje if hola_mundo_model else 'Hola desde el controller'
        response = http.Response(
            json.dumps({
                'mensaje': mensaje_backend,
                'mensaje_frontend': 'Hola desde el frontend',
                'mensaje_owl': 'Hola desde Owl',
                'mensaje_owl2': 'Hola desde Owl 2',
            }),
            content_type='application/json;charset=utf-8',
            status=200
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        return response
        