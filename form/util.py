from django.db.models import Q

from form.models import Question, Response, QuestionAnswer, QuestionOption, SubType, QuestionType
from form.serializers import QuestionSerializer
from general.security import ret_message
from scouting.models import Season, ScoutField, ScoutPit, Event


def get_questions(form_typ: str):
    current_season = Season.objects.get(current='y')

    questions = []
    qs = Question.objects.prefetch_related('questionoption_set').filter(
        Q(form_typ_id=form_typ) &
        Q(void_ind='n')).order_by('form_sub_typ_id', 'order')

    if form_typ == 'field' or form_typ == 'pit':
        qs.filter(Q(season=current_season))

    for q in qs:
        questions.append({
            'question_id': q.question_id,
            'season_id': q.season_id,
            'question': q.question,
            'order': q.order,
            'required': q.required,
            'active': q.active,
            'question_typ': q.question_typ.question_typ if q.question_typ is not None else None,
            'question_typ_nm': q.question_typ.question_typ_nm if q.question_typ is not None else None,
            'form_sub_typ': q.form_sub_typ.form_sub_typ if q.form_sub_typ is not None else None,
            'form_sub_nm': q.form_sub_typ.form_sub_nm if q.form_sub_typ is not None else None,
            'form_typ': q.form_typ,
            'questionoption_set': q.questionoption_set,
            'display_value': ('' if q.active == 'y' else 'Deactivated: ') + 'Order ' + str(q.order) + ': ' +
                             (q.form_sub_typ.form_sub_nm + ': ' if q.form_sub_typ is not None else '') +
                             q.question
        })

    return questions


def get_question_types():
    question_types = QuestionType.objects.filter(void_ind='n')
    return question_types


def get_form_sub_types(form_typ: str):
    sub_types = SubType.objects.filter(form_typ=form_typ).order_by('form_sub_nm')
    return sub_types


def save_question(question):
    required = question.get('required', 'n')
    required = required if required != '' else 'n'

    if question.get('question_id', None) is not None:
        q = Question.objects.get(question_id=question['question_id'])
        q.question = question['question']
        q.question_typ_id = question['question_typ']
        q.form_sub_typ_id = question.get('form_sub_typ', None)
        q.order = question['order']
        q.required = required
        q.active = question['active']
    else:
        q = Question(question_typ_id=question['question_typ'], form_typ_id=question['form_typ'],
                     form_sub_typ_id=question.get('form_sub_typ', None), question=question['question'],
                     order=question['order'], active=question['active'], required=required, void_ind='n')

    if question['form_typ'] in ['pit', 'field']:
        if q.season is None:
            try:
                current_season = Season.objects.get(current='y')
                q.season = current_season
            except Exception as e:
                raise Exception('No season set, see an admin.')

    q.save()

    # If adding a new question we need to make a null answer for it for all questions already answered
    match question['form_typ']:
        case 'pit':
            questions_answered = ScoutPit.objects.filter(Q(void_ind='n') &
                                                         Q(event__in=Event.objects.filter(Q(void_ind='n') &
                                                                                          Q(season=current_season)
                                                                                          )))

            for qa in questions_answered:
                QuestionAnswer(scout_pit=qa, question=q, answer='!EXIST', void_ind='n').save()
        case 'field':
            questions_answered = ScoutField.objects.filter(Q(void_ind='n') &
                                                           Q(event__in=Event.objects.filter(Q(void_ind='n') &
                                                                                            Q(season=current_season)
                                                                                            )))

            for qa in questions_answered:
                QuestionAnswer(scout_field=qa, question=q, answer='!EXIST', void_ind='n').save()
        case _:
            questions_answered = Response.objects.filter(Q(void_ind='n') & Q(form_typ_id=question['form_typ']))

            for qa in questions_answered:
                QuestionAnswer(response=qa, question=q, answer='!EXIST', void_ind='n').save()

    if question['question_typ'] == 'select' and len(question.get('questionoption_set', [])) <= 0:
        raise Exception('Select questions must have options.')

    for op in question.get('questionoption_set', []):
        if op.get('question_opt_id', None) is not None:
            qop = QuestionOption.objects.get(question_opt_id=op['question_opt_id'])
            qop.option = op['option']
            qop.active = op['active']
            qop.save()
        else:
            QuestionOption(option=op['option'], question=question, active=op['active'], void_ind='n').save()


def save_question_answer(answer: str, question: Question, scout_field: ScoutField = None, scout_pit: ScoutPit = None,
                         response: Response = None):
    qa = QuestionAnswer(question=question, answer=answer, scout_field=scout_field, scout_pit=scout_pit,
                        response=response, void_ind='n')
    qa.save()
    return qa
