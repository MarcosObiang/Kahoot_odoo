{

"name":"Kahoot_survey",
"version":"0.1",
"author": "yo",
"summary": "Para ser como Kahoot",
"description": """
    Este modulo ofreerá las mismas funciones que kahoot
""",

"data": [
    "security/ir.model.access.csv",
    "views/survey/main_action.xml",
    "views/survey/survey_view.xml",
    "views/survey_question/survey_question_form.xml",
    "views/survey_view/survey_question_view_template.xml",
    "views/root_menu.xml",
],

 'assets': {
        'web.assets_backend': [
            '/survey_module/static/src/js/custom_one2many.js',
        ],
    },

"depends":["survey","web","base"],
"category": "Games",
"installable": True,
"application": True,
"auto_install": False,




}