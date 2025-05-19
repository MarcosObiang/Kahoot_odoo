from odoo import http
from odoo.http import request
import json
from odoo.addons.survey.controllers.main import Survey  
import logging

class SurveyControllerInherit(Survey):

        # @http.route('/play',type='json',auth='public' ,methods=['GET'],csrf=False)
        # def play(self,**kwargs):

        #     return http.Response(
        #         json.dumps({
        #             'data':{
        #                 'message': 'Has accedido al controlador de kahoot sourvey, ale al play',
        #             }


        #         }),


        #         content_type='application/json;charset=utf-8',
        #         status=200,

        #     )
        
    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>', type='json', auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        """ Submit a page from the survey.
        Handles validation, conditional branching, scoring and end of survey logic.
        """
        _logger = logging.getLogger(__name__)
        _logger.info("🔁 survey_submit called with survey_token=%s and answer_token=%s", survey_token, answer_token)

        # -----------------------
        # 🔐 Survey Access Control
        # -----------------------
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return {}, {'error': access_data['validity_code']}
        
        survey_sudo = access_data['survey_sudo']
        answer_sudo = access_data['answer_sudo']

        if answer_sudo.state == 'done':
            return {}, {'error': 'unauthorized'}

        questions, page_or_question_id = survey_sudo._get_survey_questions(
            answer=answer_sudo,
            page_id=post.get('page_id'),
            question_id=post.get('question_id')
        )

        if not answer_sudo.test_entry and not survey_sudo._has_attempts_left(answer_sudo.partner_id, answer_sudo.email, answer_sudo.invite_token):
            return {}, {'error': 'unauthorized'}

        # -----------------------
        # ⏱️ Time Limit Enforcement
        # -----------------------
        if answer_sudo.survey_time_limit_reached or answer_sudo.question_time_limit_reached:
            if answer_sudo.question_time_limit_reached:
                time_limit = survey_sudo.session_question_start_time + relativedelta(
                    seconds=survey_sudo.session_question_id.time_limit
                )
                time_limit += timedelta(seconds=3)
            else:
                time_limit = answer_sudo.start_datetime + timedelta(minutes=survey_sudo.time_limit)
                time_limit += timedelta(seconds=10)

            if fields.Datetime.now() > time_limit:
                return {}, {'error': 'unauthorized'}

        # -----------------------
        # ✅ Answer Validation and Saving
        # -----------------------
        errors = {}
        for question in questions:
            inactive_questions = (
                request.env['survey.question']
                if answer_sudo.is_session_answer else
                answer_sudo._get_inactive_conditional_questions()
            )
            if question in inactive_questions:
                continue

            answer, comment = self._extract_comment_from_answers(question, post.get(str(question.id)))
            errors.update(question.validate_question(answer, comment))

            if not errors.get(question.id):
                answer_sudo._save_lines(
                    question, answer, comment,
                    overwrite_existing=survey_sudo.users_can_go_back or
                                    question.save_as_nickname or
                                    question.save_as_email
                )

        if errors and not (answer_sudo.survey_time_limit_reached or answer_sudo.question_time_limit_reached):
            return {}, {'error': 'validation', 'fields': errors}

        if not answer_sudo.is_session_answer:
            answer_sudo._clear_inactive_conditional_answers()

        # -----------------------
        # 🎯 Get Correct Answers (Scoring)
        # -----------------------
        correct_answers = {}
        if survey_sudo.scoring_type == 'scoring_with_answers_after_page':
            scorable_questions = (
                questions - answer_sudo._get_inactive_conditional_questions()
            ).filtered('is_scored_question')
            correct_answers = scorable_questions._get_correct_answers()

        # -----------------------
        # 🧭 Determine Next Page or End
        # -----------------------
        if answer_sudo.survey_time_limit_reached or survey_sudo.questions_layout == 'one_page':
            answer_sudo._mark_done()

        elif 'previous_page_id' in post:
            answer_sudo.last_displayed_page_id = post['previous_page_id']
            return correct_answers, self._prepare_question_html(survey_sudo, answer_sudo, **post)

        elif 'next_skipped_page_or_question' in post:
            answer_sudo.last_displayed_page_id = page_or_question_id
            return correct_answers, self._prepare_question_html(survey_sudo, answer_sudo, next_skipped_page=True)

        else:
            if not answer_sudo.is_session_answer:
                # 🔁 Ramificación condicional por respuesta
                lines = answer_sudo.user_input_line_ids.filtered(
                    lambda l: l.question_id.id == page_or_question_id
                )
                selected_answers = lines.mapped('suggested_answer_id')
                conditional_targets = selected_answers.filtered(
                    lambda a: a.next_question_id
                ).mapped('next_question_id')

                if conditional_targets:
                    next_page = conditional_targets[0]
                    _logger.info("➡️ Conditional branch to question: %s (ID: %s)", next_page.display_name, next_page.id)
                else:
                    next_page = survey_sudo._get_next_page_or_question(answer_sudo, page_or_question_id)
                    if next_page:
                        _logger.info("➡️ Default flow to next question: %s (ID: %s)", next_page.display_name, next_page.id)
                    else:
                        _logger.info("✅ No more questions found; survey will be marked done.")

                if not next_page:
                    if survey_sudo.users_can_go_back and answer_sudo.user_input_line_ids.filtered(
                        lambda a: a.skipped and a.question_id.constr_mandatory
                    ):
                        answer_sudo.write({
                            'last_displayed_page_id': page_or_question_id,
                            'survey_first_submitted': True,
                        })
                        return correct_answers, self._prepare_question_html(survey_sudo, answer_sudo, next_skipped_page=True)
                    else:
                        answer_sudo._mark_done()
                else:
                    answer_sudo.last_displayed_page_id = next_page.id

            answer_sudo.last_displayed_page_id = page_or_question_id

        # -----------------------
        # 📤 Return Next Page HTML and Correct Answers
        # -----------------------
        return correct_answers, self._prepare_question_html(survey_sudo, answer_sudo)



def _prepare_survey_data(self, survey_sudo, answer_sudo, **post):
    """ This method prepares all the data needed for template rendering, in function of the survey user input state.
        :param post:
            - previous_page_id : come from the breadcrumb or the back button and force the next questions to load
                                 to be the previous ones.
            - next_skipped_page : force the display of next skipped question or page if any.
            - question_id : FORZADO manualmente para control de flujo condicional.
    """
    data = {
        'is_html_empty': is_html_empty,
        'survey': survey_sudo,
        'answer': answer_sudo,
        'skipped_questions': answer_sudo._get_skipped_questions(),
        'breadcrumb_pages': [{
            'id': page.id,
            'title': page.title,
        } for page in survey_sudo.page_ids],
        'format_datetime': lambda dt: format_datetime(request.env, dt, dt_format=False),
        'format_date': lambda date: format_date(request.env, date)
    }

    if survey_sudo.questions_layout != 'page_per_question':
        triggering_answers_by_question, triggered_questions_by_answer, selected_answers = answer_sudo._get_conditional_values()
        data.update({
            'triggering_answers_by_question': {
                question.id: triggering_answers.ids
                for question, triggering_answers in triggering_answers_by_question.items() if triggering_answers
            },
            'triggered_questions_by_answer': {
                answer.id: triggered_questions.ids
                for answer, triggered_questions in triggered_questions_by_answer.items()
            },
            'selected_answers': selected_answers.ids
        })

    if not answer_sudo.is_session_answer and survey_sudo.is_time_limited and answer_sudo.start_datetime:
        data.update({
            'server_time': fields.Datetime.now(),
            'timer_start': answer_sudo.start_datetime.isoformat(),
            'time_limit_minutes': survey_sudo.time_limit
        })

    page_or_question_key = 'question' if survey_sudo.questions_layout == 'page_per_question' else 'page'

    # 🔙 Volver a una pregunta/página anterior (breadcrumb o botón atrás)
    if 'previous_page_id' in post:
        previous_page_or_question_id = int(post['previous_page_id'])
        new_previous_id = survey_sudo._get_next_page_or_question(answer_sudo, previous_page_or_question_id, go_back=True).id
        page_or_question = request.env['survey.question'].sudo().browse(previous_page_or_question_id)
        data.update({
            page_or_question_key: page_or_question,
            'previous_page_id': new_previous_id,
            'has_answered': answer_sudo.user_input_line_ids.filtered(lambda line: line.question_id.id == new_previous_id),
            'can_go_back': survey_sudo._can_go_back(answer_sudo, page_or_question),
        })
        return data

    # ✅ 🚨 CONTROL CONDICIONAL MANUAL
    if 'question_id' in post:
        forced_question = request.env['survey.question'].sudo().browse(int(post['question_id']))
        data.update({
            page_or_question_key: forced_question,
            'has_answered': answer_sudo.user_input_line_ids.filtered(lambda line: line.question_id == forced_question),
            'can_go_back': survey_sudo._can_go_back(answer_sudo, forced_question),
        })
        if survey_sudo.questions_layout != 'one_page':
            data.update({
                'previous_page_id': survey_sudo._get_next_page_or_question(answer_sudo, forced_question.id, go_back=True).id
            })
        return data

    # 🚦 Flujo normal
    if answer_sudo.state == 'in_progress':
        next_page_or_question = None
        if answer_sudo.is_session_answer:
            next_page_or_question = survey_sudo.session_question_id
        else:
            if 'next_skipped_page' in post:
                next_page_or_question = answer_sudo._get_next_skipped_page_or_question()
            if not next_page_or_question:
                next_page_or_question = survey_sudo._get_next_page_or_question(
                    answer_sudo,
                    answer_sudo.last_displayed_page_id.id if answer_sudo.last_displayed_page_id else 0)
                if not next_page_or_question:
                    next_page_or_question = answer_sudo._get_next_skipped_page_or_question()

            if next_page_or_question:
                if answer_sudo.survey_first_submitted:
                    survey_last = answer_sudo._is_last_skipped_page_or_question(next_page_or_question)
                else:
                    survey_last = survey_sudo._is_last_page_or_question(answer_sudo, next_page_or_question)
                data.update({'survey_last': survey_last})

        if answer_sudo.is_session_answer and next_page_or_question.is_time_limited:
            data.update({
                'timer_start': survey_sudo.session_question_start_time.isoformat(),
                'time_limit_minutes': next_page_or_question.time_limit / 60
            })

        data.update({
            page_or_question_key: next_page_or_question,
            'has_answered': answer_sudo.user_input_line_ids.filtered(lambda line: line.question_id == next_page_or_question),
            'can_go_back': survey_sudo._can_go_back(answer_sudo, next_page_or_question),
        })
        if survey_sudo.questions_layout != 'one_page':
            data.update({
                'previous_page_id': survey_sudo._get_next_page_or_question(answer_sudo, next_page_or_question.id, go_back=True).id
            })

    elif answer_sudo.state == 'done' or answer_sudo.survey_time_limit_reached:
        return self._prepare_survey_finished_values(survey_sudo, answer_sudo)

    return data
