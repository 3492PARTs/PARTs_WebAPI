from django.urls import path

from .views import SaveAnswersView, FormInitView, ResponseView, ResponsesView, \
    QuestionAggregateView, QuestionAggregateTypeView, QuestionConditionView, QuestionView

urlpatterns = [
    path('question/', QuestionView.as_view()),
    path('save-answers/', SaveAnswersView.as_view()),
    path('form-init/', FormInitView.as_view()),
    path('get-response/', ResponseView.as_view()),
    path('get-responses/', ResponsesView.as_view()),
    path('question-aggregate/', QuestionAggregateView.as_view()),
    path('question-aggregate-types/', QuestionAggregateTypeView.as_view()),
    path('question-condition/', QuestionConditionView.as_view()),
]
