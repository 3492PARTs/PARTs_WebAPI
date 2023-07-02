from django.db.models import Q

from form.models import Question, Response, QuestionAnswer
from scouting.models import Season, ScoutField, ScoutPit


def get_questions(form_typ):
    current_season = Season.objects.get(current='y')

    questions = []
    qs = Question.objects.prefetch_related('questionoption_set').filter(
        Q(form_typ_id=form_typ) & Q(active='y') &
        Q(void_ind='n')).order_by('form_sub_typ_id', 'order')

    if form_typ == 'field' or form_typ == 'pit':
        qs.filter(Q(season=current_season))

    for q in qs:
        questions.append({
            'question_id': q.question_id,
            'season_id': q.season_id,
            'question': q.question,
            'order': q.order,
            'active': q.active,
            'question_typ': q.question_typ.question_typ if q.question_typ is not None else None,
            'question_typ_nm': q.question_typ.question_typ_nm if q.question_typ is not None else None,
            'form_sub_typ': q.form_sub_typ.form_sub_typ if q.form_sub_typ is not None else None,
            'form_sub_nm': q.form_sub_typ.form_sub_nm if q.form_sub_typ is not None else None,
            'form_typ': q.form_typ,
            'questionoptions_set': q.questionoption_set,
            'display_value': ('' if q.active == 'y' else 'Deactivated: ') +
                             (q.form_sub_typ.form_sub_nm + ': ' if q.form_sub_typ is not None else '') +
                             q.question
        })

    return questions


def save_question_answer(answer: str, question: Question, scout_field: ScoutField = None, scout_pit: ScoutPit = None,
                         response: Response = None):
    qa = QuestionAnswer(question=question, answer=answer, scout_field=scout_field, scout_pit=scout_pit,
                        response=response, void_ind='n')
    qa.save()
    return qa
