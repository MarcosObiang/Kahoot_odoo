{
    'name': 'Hola Mundo App',
    'version': '1.0',
    'summary': 'Módulo básico para mostrar Hola Mundo en el frontend con Owl.',
    'description': """
    Este módulo introduce un modelo simple y una página web que muestra "Hola Mundo"
    utilizando el framework Owl de Odoo.
    """,
    'author': 'Tu Nombre',
    'website': 'tu_website.com',
    'license': 'LGPL-3',
    'depends': [],  # <-- Eliminamos la dependencia de 'website'
    'data': [
        'views/templates.xml',
    ],

    'installable': True,
    'application': False,
}