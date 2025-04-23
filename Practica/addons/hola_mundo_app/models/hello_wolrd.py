from odoo import models,fields

class HolaMundo(models.TransientModel):
    _name='hola.mundo'
    _description='Modelo hola mundo'

    mensaje=fields.Char(string='mensajes', default='Hola desde el backend')
    