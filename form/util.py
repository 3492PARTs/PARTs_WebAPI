from django.db.models import Q
from django.db.models.functions import Lower

import scouting.models
from form.models import Question, Response, QuestionAnswer, QuestionOption, FormSubType, QuestionType, \
    QuestionAggregate, QuestionAggregateType, QuestionCondition
from form.serializers import QuestionSerializer
from general.security import ret_message
from scouting.models import Season, ScoutField, ScoutPit, Event


def get_questions(form_typ: str, active: str = '', form_sub_typ: str = ''):
    questions = []
    season = Q()
    active_ind = Q()
    form_sub_typ_q = Q()

    if form_typ == 'field' or form_typ == 'pit':
        current_season = Season.objects.get(current='y')
        scout_questions = scouting.models.Question.objects.filter(Q(void_ind='n') & Q(season=current_season))
        season = Q(question_id__in=set(sq.question_id for sq in scout_questions))

    if active != '':
        active_ind = Q(active=active)

    if form_sub_typ is None:
        form_sub_typ_q = Q(form_sub_typ_id__isnull=True)
    elif form_sub_typ is not '':
        form_sub_typ_q = Q(form_sub_typ_id=form_sub_typ)

    qs = Question.objects.prefetch_related('questionoption_set').filter(
        season &
        Q(form_typ_id=form_typ) &
        form_sub_typ_q &
        active_ind &
        Q(void_ind='n')).order_by('form_sub_typ__order', 'order')

    for q in qs:
        questions.append(format_question_values(q))

    return questions


def format_question_values(q: Question):
    try:
        scout_question = q.scout_question.get(Q(void_ind='n'))
        season = scout_question.season.season_id
    except scouting.models.Question.DoesNotExist as e:
        scout_question = None
        season = None

    questionoption_set = []
    for qo in q.questionoption_set.all():
        questionoption_set.append({
            'question_opt_id': qo.question_opt_id,
            'question_id': qo.question_id,
            'option': qo.option,
            'active': qo.active
        })

    try:
        q.condition_question_to.get(Q(void_ind='n') & Q(active='y'))
        is_condition = 'y'
    except QuestionCondition.DoesNotExist:
        is_condition = 'n'

    return {
            'question_id': q.question_id,
            'season_id': season,
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
            'scout_question': scout_question,
            'is_condition': is_condition
        }


def get_question_types():
    question_types = QuestionType.objects.filter(void_ind='n').order_by(Lower('question_typ_nm'))
    return question_types


def get_form_sub_types(form_typ: str):
    sub_types = FormSubType.objects.filter(form_typ=form_typ).order_by('order', Lower('form_sub_nm'))
    return sub_types


def save_question(question):
    if question['form_typ'] in ['pit', 'field']:
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            raise Exception('No season set, see an admin.')

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
        if question.get('scout_question', None).get('id', None) is not None:
            sq = scouting.models.Question.objects.get(Q(void_ind='n') & Q(question_id=q.question_id))
        else:
            sq = scouting.models.Question(question_id=q.question_id)

        if sq.season is None:
            sq.season = current_season

        sq.scorable = question.get('scout_question', None).get('scorable', False)

        sq.save()

    if question.get('question_id', None) is None:
        # If adding a new question we need to make a null answer for it for all questions already answered
        match question['form_typ']:
            case 'pit':
                pit_responses = ScoutPit.objects.filter(Q(void_ind='n') &
                                                        Q(event__in=Event.objects.filter(Q(void_ind='n') &
                                                                                         Q(season=current_season)
                                                                                         )))
                questions_answered = Response.objects.filter(Q(void_ind='n') &
                                                             Q(response_id__in=set(
                                                                 pr.response_id for pr in pit_responses)))
            case 'field':
                field_responses = ScoutField.objects.filter(Q(void_ind='n') &
                                                            Q(event__in=Event.objects.filter(Q(void_ind='n') &
                                                                                             Q(season=current_season)
                                                                                             )))
                questions_answered = Response.objects.filter(Q(void_ind='n') &
                                                             Q(response_id__in=set(
                                                                 fr.response_id for fr in field_responses)))
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


def get_question_aggregates(form_typ: str):
    question_aggregates = []
    season = Q()

    if form_typ == 'field' or form_typ == 'pit':
        current_season = Season.objects.get(current='y')
        scout_questions = scouting.models.Question.objects.filter(Q(void_ind='n') & Q(season=current_season))
        season = Q(questions__question_id__in=set(sq.question_id for sq in scout_questions))

    qas = QuestionAggregate.objects.filter(Q(void_ind='n') & Q(questions__form_typ=form_typ) & season).distinct()
    for qa in qas:
        question_aggregates.append({
            'question_aggregate_id': qa.question_aggregate_id,
            'field_name': qa.field_name,
            'question_aggregate_typ': qa.question_aggregate_typ,
            'questions': list(format_question_values(q) for q in qa.questions.filter(Q(void_ind='n'))),
            'active': qa.active,
        })

    return question_aggregates


def get_question_aggregate_types():
    return QuestionAggregateType.objects.filter(Q(void_ind='n'))


def save_question_aggregate(data):
    if data.get('question_aggregate_id', None) is not None:
        qa = QuestionAggregate.objects.get(Q(question_aggregate_id=data['question_aggregate_id']))
    else:
        qa = QuestionAggregate()

    qa.field_name = data['field_name']
    qa.active = data['active']
    qa.question_aggregate_typ = QuestionAggregateType.objects.get(Q(void_ind='n') & Q(question_aggregate_typ=data['question_aggregate_typ']['question_aggregate_typ']))
    qa.save()

    questions = Question.objects.filter(question_id__in=set(q['question_id'] for q in data['questions']))

    for q in questions:
        qa.questions.add(q)

    remove = Question.objects.filter(Q(question__in=qa.questions.all()) & ~Q(question__in=questions))
    for r in remove:
        qa.questions.remove(r)

    qa.save()

    return qa


def get_question_condition(form_typ: str):
    question_aggregates = []
    season = Q()

    if form_typ == 'field' or form_typ == 'pit':
        current_season = Season.objects.get(current='y')
        scout_questions = scouting.models.Question.objects.filter(Q(void_ind='n') & Q(season=current_season))
        season = Q(question_from__question_id__in=set(q.question_id for q in scout_questions))

    question_conditions = QuestionCondition.objects.filter(Q(void_ind='n') & Q(question_from__form_typ=form_typ) & season)

    for qc in question_conditions:
        question_aggregates.append({
            'question_condition_id': qc.question_condition_id,
            'condition': qc.condition,
            'question_from': format_question_values(qc.question_from),
            'question_to': format_question_values(qc.question_to),
            'active': qc.active
        })

    return question_aggregates


def save_question_condition(data):
    if data.get('question_condition_id', None) is not None:
        qc = QuestionCondition.objects.get(question_condition_id=data['question_condition_id'])
    else:
        qc = QuestionCondition()

    qc.condition = data['condition']
    qc.active = data['active']

    qc.question_from = Question.objects.get(question_id=data['question_from']['question_id'])
    qc.question_to = Question.objects.get(question_id=data['question_to']['question_id'])

    qc.save()

    return qc


def format_question_condition_values(qc: QuestionCondition):
    return {
        'question_condition_id': qc.question_condition_id,
        'condition': qc.condition,
        'question_from': format_question_values(qc.question_from),
        'question_to': format_question_values(qc.question_to),
        'active': qc.active,
    }


def get_questions_with_conditions(form_typ: str, form_sub_typ: str = ''):
    questions_with_conditions = []
    questions = get_questions(form_typ, 'y', form_sub_typ)

    for q in questions:
        q['conditions'] = []
        is_condition = False
        question = Question.objects.get(question_id=q['question_id'])
        for qc in question.condition_question_from.filter(Q(void_ind='n') & Q(active='y')):
            q['conditions'].append(format_question_condition_values(qc))

        qct = question.condition_question_to.filter(Q(void_ind='n') & Q(active='y'))
        is_condition = len(qct) > 0

        if not is_condition:
            questions_with_conditions.append(q)

    return questions_with_conditions
