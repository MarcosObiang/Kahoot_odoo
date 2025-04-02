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
    "views/root_menu.xml",
],

"depends":["survey"],
"category": "Games",
"installable": True,
"application": True,
"auto_install": False,




}