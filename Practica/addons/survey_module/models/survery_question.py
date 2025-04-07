from odoo import models,api,fields
from odoo.exceptions import ValidationError

import logging

class KahootQuestion(models.Model):
    _inherit="survey.question"
    _description="Kahoot question"
    answer_true_or_false=fields.Boolean("True or false")
    question_type= fields.Selection(selection_add=[('true_or_false','True or false')],ondelete={'true_or_false': 'cascade'} )
    answer_count=fields.Integer("Answers count", default=0)

 

    triggering_answer_ids = fields.Many2many(
        'survey.question.answer', string="Triggering Answers", copy=False, store=True,
        readonly=False, help="Picking any of these answers will trigger this question.\n"
                             "Leave the field empty if the question should always be displayed.",
        domain="""[
            ('question_id.survey_id', '=', survey_id),
            '&', ('question_id.question_type', 'in', ['simple_choice', 'multiple_choice','true_or_false']),
                 '|',
                     ('question_id.sequence', '<', sequence),
                     '&', ('question_id.sequence', '=', sequence), ('question_id.id', '<', id)
        ]"""
    )


    @api.depends('question_type')
    def _compute_question_placeholder(self):
        for question in self:
            if question.question_type in ('simple_choice', 'multiple_choice', 'matrix','true_or_false') \
                    or not question.question_placeholder:  # avoid CacheMiss errors
                question.question_placeholder = False

    @api.onchange("question_type")

    def on_question_type_changed(self):
         
        _logger = logging.getLogger(__name__)
        new_context = dict(self.env.context, question_type=self.question_type)
        self = self.with_context(new_context)
        _logger.info("Este es el contexto tras cambiarlo %s", self.env.context)

        return



    @api.onchange('suggested_answer_ids')
    def _onchange_suggested_answers(self):
        _logger = logging.getLogger(__name__)

        if self.question_type=='true_or_false':

            self.answer_count = len(self.suggested_answer_ids)
            _logger.info(f"Pregunta {self.id} tiene {self.answer_count} respuestas sin guardar.")
        else:
            self.answer_count=0







    @api.constrains('suggested_answer_ids')
    def _check_answer_count(self):
        # Validamos que no haya más de 2 registros en el campo One2many
        for record in self:
            if len(record.suggested_answer_ids) > 2:
                raise ValidationError("No puedes agregar más de dos opciones en este campo de respuestas.")




    def _compute_is_scored_question(self):
        """ Computes whether a question "is scored" or not. Handles following cases:
          - inconsistent Boolean=None edge case that breaks tests => False
          - survey is not scored => False
          - 'date'/'datetime'/'numerical_box' question types w/correct answer => True
            (implied without user having to activate, except for numerical whose correct value is 0.0)
          - 'simple_choice / multiple_choice': set to True if any of suggested answers are marked as correct
          - question_type isn't scoreable (note: choice questions scoring logic handled separately) => False
        """
        for question in self:
            if question.is_scored_question is None or question.scoring_type == 'no_scoring':
                question.is_scored_question = False
            elif question.question_type == 'date':
                question.is_scored_question = bool(question.answer_date)
            elif question.question_type == 'datetime':
                question.is_scored_question = bool(question.answer_datetime)
            elif question.question_type == 'numerical_box' and question.answer_numerical_box:
                question.is_scored_question = True
            elif question.question_type in ['simple_choice', 'multiple_choice',"true_or_false"]:
                question.is_scored_question = any(question.suggested_answer_ids.mapped('is_correct'))
            else:
                question.is_scored_question = False

    def validate_question(self, answer, comment=None):
        """ Validate question, depending on question type and parameters
         for simple choice, text, date and number, answer is simply the answer of the question.
         For other multiple choices questions, answer is a list of answers (the selected choices
         or a list of selected answers per question -for matrix type-):
            - Simple answer : answer = 'example' or 2 or question_answer_id or 2019/10/10
            - Multiple choice : answer = [question_answer_id1, question_answer_id2, question_answer_id3]
            - Matrix: answer = { 'rowId1' : [colId1, colId2,...], 'rowId2' : [colId1, colId3, ...] }

         return dict {question.id (int): error (str)} -> empty dict if no validation error.
         """
        self.ensure_one()
        if isinstance(answer, str):
            answer = answer.strip()
        # Empty answer to mandatory question
        # because in choices question types, comment can count as answer
        if not answer and self.question_type not in ['simple_choice', 'multiple_choice']:
            if self.constr_mandatory and not self.survey_id.users_can_go_back:
                return {self.id: self.constr_error_msg or _('This question requires an answer.')}
        else:
            if self.question_type == 'char_box':
                return self._validate_char_box(answer)
            elif self.question_type == 'numerical_box':
                return self._validate_numerical_box(answer)
            elif self.question_type in ['date', 'datetime']:
                return self._validate_date(answer)
            elif self.question_type in ['simple_choice', 'multiple_choice','true_or_false']:
                return self._validate_choice(answer, comment)
            elif self.question_type == 'matrix':
                return self._validate_matrix(answer)
        return {}
    


    def _prepare_statistics(self, user_input_lines):
        """ Compute statistical data for questions by counting number of vote per choice on basis of filter """
        all_questions_data = []
        for question in self:
            question_data = {'question': question, 'is_page': question.is_page}

            if question.is_page:
                all_questions_data.append(question_data)
                continue

            # fetch answer lines, separate comments from real answers
            all_lines = user_input_lines.filtered(lambda line: line.question_id == question)
            if question.question_type in ['simple_choice', 'multiple_choice', 'matrix','true_or_false']:
                answer_lines = all_lines.filtered(
                    lambda line: line.answer_type == 'suggestion' or (
                        line.skipped and not line.answer_type) or (
                        line.answer_type == 'char_box' and question.comment_count_as_answer)
                    )
                comment_line_ids = all_lines.filtered(lambda line: line.answer_type == 'char_box')
            else:
                answer_lines = all_lines
                comment_line_ids = self.env['survey.user_input.line']
            skipped_lines = answer_lines.filtered(lambda line: line.skipped)
            done_lines = answer_lines - skipped_lines
            question_data.update(
                answer_line_ids=answer_lines,
                answer_line_done_ids=done_lines,
                answer_input_done_ids=done_lines.mapped('user_input_id'),
                answer_input_skipped_ids=skipped_lines.mapped('user_input_id'),
                comment_line_ids=comment_line_ids)
            question_data.update(question._get_stats_summary_data(answer_lines))

            # prepare table and graph data
            table_data, graph_data = question._get_stats_data(answer_lines)
            question_data['table_data'] = table_data
            question_data['graph_data'] = json.dumps(graph_data)

            all_questions_data.append(question_data)
        return all_questions_data

    def _get_stats_data(self, user_input_lines):
        if self.question_type == 'simple_choice'or self.question_type=="true_or_false":
            return self._get_stats_data_answers(user_input_lines)
        elif self.question_type == 'multiple_choice':
            table_data, graph_data = self._get_stats_data_answers(user_input_lines)
            return table_data, [{'key': self.title, 'values': graph_data}]
        elif self.question_type == 'matrix':
            return self._get_stats_graph_data_matrix(user_input_lines)
        return [line for line in user_input_lines], []
    def _get_stats_summary_data(self, user_input_lines):
        stats = {}
        if self.question_type in ['simple_choice', 'multiple_choice','true_or_false']:
            stats.update(self._get_stats_summary_data_choice(user_input_lines))
        elif self.question_type == 'numerical_box':
            stats.update(self._get_stats_summary_data_numerical(user_input_lines))

        if self.question_type in ['numerical_box', 'date', 'datetime']:
            stats.update(self._get_stats_summary_data_scored(user_input_lines))
        return stats
    
    def _get_stats_summary_data_choice(self, user_input_lines):
        right_inputs, partial_inputs = self.env['survey.user_input'], self.env['survey.user_input']
        right_answers = self.suggested_answer_ids.filtered(lambda label: label.is_correct)
        if self.question_type == 'multiple_choice':
            for user_input, lines in tools.groupby(user_input_lines, operator.itemgetter('user_input_id')):
                user_input_answers = self.env['survey.user_input.line'].concat(*lines).filtered(lambda l: l.answer_is_correct).mapped('suggested_answer_id')
                if user_input_answers and user_input_answers < right_answers:
                    partial_inputs += user_input
                elif user_input_answers:
                    right_inputs += user_input
        else:
            right_inputs = user_input_lines.filtered(lambda line: line.answer_is_correct).mapped('user_input_id')
        return {
            'right_answers': right_answers,
            'right_inputs_count': len(right_inputs),
            'partial_inputs_count': len(partial_inputs),
        }
    



    def _get_correct_answers(self):

        """ Return a dictionary linking the scorable question ids to their correct answers.
        The questions without correct answers are not considered.
        """
        correct_answers = {}

        # Simple and multiple choice
        choices_questions = self.filtered(lambda q: q.question_type in ['simple_choice', 'multiple_choice',"true_or_false"])
        if choices_questions:
            suggested_answers_data = self.env['survey.question.answer'].search_read(
                [('question_id', 'in', choices_questions.ids), ('is_correct', '=', True)],
                ['question_id', 'id'],
                load='', # prevent computing display_names
            )
            for data in suggested_answers_data:
                if not data.get('id'):
                    continue
                correct_answers.setdefault(data['question_id'], []).append(data['id'])

        # Numerical box, date, datetime
        for question in self - choices_questions:
            if question.question_type not in ['numerical_box', 'date', 'datetime']:
                continue
            answer = question[f'answer_{question.question_type}']
            if question.question_type == 'date':
                answer = tools.format_date(self.env, answer)
            elif question.question_type == 'datetime':
                answer = tools.format_datetime(self.env, answer, tz='UTC', dt_format=False)
            correct_answers[question.id] = answer

        return correct_answers
    




    @api.depends('survey_id', 'survey_id.question_ids', 'triggering_answer_ids')
    def _compute_allowed_triggering_question_ids(self):
        """Although the question (and possible trigger questions) sequence
        is used here, we do not add these fields to the dependency list to
        avoid cascading rpc calls when reordering questions via the webclient.
        """
        possible_trigger_questions = self.search([
            ('is_page', '=', False),
            ('question_type', 'in', ['simple_choice', 'multiple_choice','true_or_false']),
            ('suggested_answer_ids', '!=', False),
            ('survey_id', 'in', self.survey_id.ids)
        ])
        # Using the sequence stored in db is necessary for existing questions that are passed as
        # NewIds because the sequence provided by the JS client can be incorrect.
        (self | possible_trigger_questions).flush_recordset()
        self.env.cr.execute(
            "SELECT id, sequence FROM survey_question WHERE id =ANY(%s)",
            [self.ids]
        )
        conditional_questions_sequences = dict(self.env.cr.fetchall())  # id: sequence mapping

        for question in self:
            question_id = question._origin.id
            if not question_id:  # New question
                question.allowed_triggering_question_ids = possible_trigger_questions.filtered(
                    lambda q: q.survey_id.id == question.survey_id._origin.id)
                question.is_placed_before_trigger = False
                continue

            question_sequence = conditional_questions_sequences[question_id]

            question.allowed_triggering_question_ids = possible_trigger_questions.filtered(
                lambda q: q.survey_id.id == question.survey_id._origin.id
                and (q.sequence < question_sequence or q.sequence == question_sequence and q.id < question_id)
            )
            question.is_placed_before_trigger = bool(
                set(question.triggering_answer_ids.question_id.ids)
                - set(question.allowed_triggering_question_ids.ids)  # .ids necessary to match ids with newIds
            )
