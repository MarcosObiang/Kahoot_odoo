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
        'web.assets_frontend': [
            'survey/static/src/js/survey_preload_image_mixin.js',
            'survey/static/src/js/survey_image_zoomer.js',
            'survey/static/src/js/survey_form.js',
            'survey_module/static/src/js/survey_form_true_false.js',
        ],
    },

"depends":["survey","web","base"],
"category": "Games",
"installable": True,
"application": True,
"auto_install": False,




}