from django.urls import path

from .views import SaveAnswers, GetFormInit, QuestionsView, GetResponse, GetResponses, \
    QuestionAggregateView, QuestionAggregateTypeView, QuestionConditionView

urlpatterns = [
    path('question/', QuestionsView.as_view()),
    path('save-answers/', SaveAnswers.as_view()),
    path('form-init/', GetFormInit.as_view()),
    path('get-response/', GetResponse.as_view()),
    path('get-responses/', GetResponses.as_view()),
    path('question-aggregate/', QuestionAggregateView.as_view()),
    path('question-aggregate-types/', QuestionAggregateTypeView.as_view()),
    path('question-condition/', QuestionConditionView.as_view()),
]
