from django.urls import path

from .views import (
    SaveAnswersView,
    FormEditorView,
    ResponseView,
    ResponsesView,
    QuestionAggregateView,
    QuestionAggregateTypeView,
    QuestionConditionView,
    QuestionView, QuestionFlowView, QuestionConditionTypesView, QuestionFlowConditionView,
)

urlpatterns = [
    path("question/", QuestionView.as_view()),
    path("save-answers/", SaveAnswersView.as_view()),
    path("form-editor/", FormEditorView.as_view()),
    path("response/", ResponseView.as_view()),
    path("responses/", ResponsesView.as_view()),
    path("question-aggregate/", QuestionAggregateView.as_view()),
    path("question-aggregate-types/", QuestionAggregateTypeView.as_view()),
    path("question-condition/", QuestionConditionView.as_view()),
    path("question-condition-types/", QuestionConditionTypesView.as_view()),
    path("question-flow/", QuestionFlowView.as_view()),
    path("question-flow-condition/", QuestionFlowConditionView.as_view()),
]
