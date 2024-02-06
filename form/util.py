from django.db.models import Q
from django.db.models.functions import Lower

import scouting.models
from form.models import Question, Response, QuestionAnswer, QuestionOption, FormSubType, QuestionType
from form.serializers import QuestionSerializer
from general.security import ret_message
from scouting.models import Season, ScoutField, ScoutPit, Event


def get_questions(form_typ: str, active=''):
    questions = []
    season = Q()
    active_ind = Q()

    if form_typ == 'field' or form_typ == 'pit':
        current_season = Season.objects.get(current='y')
        scout_questions = scouting.models.Question.objects.filter(Q(void_ind='n') & Q(season=current_season))
        season = Q(question_id__in=set(sq.question_id for sq in scout_questions))

    if active != '':
        active_ind = Q(active=active)

    qs = Question.objects.prefetch_related('questionoption_set').filter(
        season &
        Q(form_typ_id=form_typ) &
        active_ind &
        Q(void_ind='n')).order_by('form_sub_typ__order', 'order')

    for q in qs:
        questionoption_set = []
        for qo in q.questionoption_set.all():
            questionoption_set.append({
                'question_opt_id': qo.question_opt_id,
                'question_id': qo.question_id,
                'option': qo.option,
                'active': qo.active
            })

        scout_question = scouting.models.Question.objects.get(Q(void_ind='n') & Q(question_id=q.question_id))

        questions.append({
            'question_id': q.question_id,
            'season_id': q.season_id,
            'question': q.question,
            'order': q.order,
            'required': q.required,
            'active': q.active,
            'question_typ': q.question_typ,
            'form_sub_typ': q.form_sub_typ.form_sub_typ if q.form_sub_typ is not None else None,
            'form_sub_nm': q.form_sub_typ.form_sub_nm if q.form_sub_typ is not None else None,
            'form_typ': q.form_typ.form_typ,
            'questionoption_set': questionoption_set,
            'display_value': ('' if q.active == 'y' else 'Deactivated: ') + 'Order ' + str(q.order) + ': ' +
                             (q.form_sub_typ.form_sub_nm + ': ' if q.form_sub_typ is not None else '') +
                             q.question,
            'scout_question': scout_question
        })

    return questions


def get_question_types():
    question_types = QuestionType.objects.filter(void_ind='n').order_by(Lower('question_typ_nm'))
    return question_types


def get_form_sub_types(form_typ: str):
    sub_types = FormSubType.objects.filter(form_typ=form_typ).order_by('order', Lower('form_sub_nm'))
    return sub_types


def save_question(question):
    required = question.get('required', 'n')
    required = required if required != '' else 'n'

    if question.get('question_id', None) is not None:
        q = Question.objects.get(question_id=question['question_id'])
        q.question = question['question']
        q.question_typ_id = question['question_typ']['question_typ']
        q.form_sub_typ_id = question.get('form_sub_typ', None)
        q.order = question['order']
        q.required = required
        q.active = question['active']
    else:
        q = Question(question_typ_id=question['question_typ']['question_typ'], form_typ_id=question['form_typ'],
                     form_sub_typ_id=question.get('form_sub_typ', None), question=question['question'],
                     order=question['order'], active=question['active'], required=required, void_ind='n')
    q.save()

    if question['form_typ'] in ['pit', 'field']:
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            raise Exception('No season set, see an admin.')
        if question.get('scout_question', None).get('id', None) is not None:
            sq = scouting.models.Question.objects.get(Q(void_ind='n') & Q(question_id=q.question_id))
        else:
            sq = scouting.models.Question(question_id=q.question_id)

        if sq.season is None:
            sq.season = current_season

        sq.scorable = question.get('scout_question', None).get('scorable', False)

        sq.save()

    # If adding a new question we need to make a null answer for it for all questions already answered
    match question['form_typ']:
        case 'pit':
            pit_responses = ScoutPit.objects.filter(Q(void_ind='n') &
                                                    Q(event__in=Event.objects.filter(Q(void_ind='n') &
                                                                                     Q(season=current_season)
                                                                                     )))
            questions_answered = Response.objects.filter(Q(void_ind='n') &
                                                         Q(response_id__in=set(pr.response_id for pr in pit_responses)))
        case 'field':
            field_responses = ScoutField.objects.filter(Q(void_ind='n') &
                                                        Q(event__in=Event.objects.filter(Q(void_ind='n') &
                                                                                         Q(season=current_season)
                                                                                         )))
            questions_answered = Response.objects.filter(Q(void_ind='n') &
                                                         Q(response_id__in=set(fr.response_id for fr in field_responses)))
        case _:
            questions_answered = Response.objects.filter(Q(void_ind='n') & Q(form_typ_id=question['form_typ']))

    for qa in questions_answered:
        QuestionAnswer(response=qa, question=q, answer='!EXIST', void_ind='n').save()

    if question['question_typ']['is_list'] == 'y' and len(question.get('questionoption_set', [])) <= 0:
        raise Exception('Select questions must have options.')

    for op in question.get('questionoption_set', []):
        if op.get('question_opt_id', None) is not None:
            qop = QuestionOption.objects.get(question_opt_id=op['question_opt_id'])
            qop.option = op['option']
            qop.active = op['active']
            qop.save()
        else:
            QuestionOption(option=op['option'], question=q, active=op['active'], void_ind='n').save()


def save_question_answer(answer: str, question: Question, response: Response):
    qa = QuestionAnswer(question=question, answer=answer, response=response, void_ind='n')
    qa.save()
    return qa


def get_response(response_id: int):
    res = Response.objects.get(Q(response_id=response_id) & Q(void_ind='n'))
    questions = get_questions(res.form_typ, 'y')

    for question in questions:
        question['answer'] = QuestionAnswer.objects.get(
            Q(question_id=question.get('question_id')) & Q(response=res) & Q(void_ind='n')).answer

    return questions


def get_responses(form_typ: int):
    responses = []
    resps = Response.objects.filter(Q(form_typ__form_typ=form_typ) & Q(void_ind='n')).order_by('-time')

    for res in resps:
        questions = get_questions(res.form_typ, 'y')

        for question in questions:
            question['answer'] = QuestionAnswer.objects.get(
                Q(question_id=question.get('question_id')) & Q(response=res) & Q(void_ind='n')).answer

        responses.append({
            'response_id': res.response_id,
            'form_typ': res.form_typ.form_typ,
            'time': res.time,
            'questionanswer_set': questions
        })

    return responses
