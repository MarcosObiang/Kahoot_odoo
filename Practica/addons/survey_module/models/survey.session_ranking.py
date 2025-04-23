
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import float_round



class SurveySessionRanking(models.Model):
    _inherits='survey.session'