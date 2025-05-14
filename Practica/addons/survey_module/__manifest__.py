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
    "views/survey_question_answer/form.xml",
    "views/survey_view/survey_view_page_fill.xml",
    "views/root_menu.xml",
],



"depends":["survey","web","base","web_editor"],
"category": "Games",
"installable": True,
"application": True,
"auto_install": False,

'assets': {
    'web.assets_frontend':[
 
        'survey_module/static/src/components/quit_timer.js',
    ]
},





}