from django.urls import path

from .views import (
    SaveAnswersView,
    FormEditorView,
    ResponseView,
    ResponsesView,
    QuestionAggregateView,
    QuestionAggregateTypeView,
    QuestionConditionView,
    QuestionView, FlowView, QuestionConditionTypesView, FlowConditionView, QuestionFlowView, GraphEditorView, GraphView,
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
    path("flow/", FlowView.as_view()),
    path("question-flow/", QuestionFlowView.as_view()),
    path("flow-condition/", FlowConditionView.as_view()),
    path("graph-editor/", GraphEditorView.as_view()),
    path("graph/", GraphView.as_view()),
]
