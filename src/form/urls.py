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

app_name = "form"

urlpatterns = [
    path("question/", QuestionView.as_view(), name="question"),
    path("save-answers/", SaveAnswersView.as_view(), name="save-answers"),
    path("form-editor/", FormEditorView.as_view(), name="form-editor"),
    path("response/", ResponseView.as_view(), name="response"),
    path("responses/", ResponsesView.as_view(), name="responses"),
    path("question-aggregate/", QuestionAggregateView.as_view(), name="question-aggregate"),
    path("question-aggregate-types/", QuestionAggregateTypeView.as_view(), name="question-aggregate-types"),
    path("question-condition/", QuestionConditionView.as_view(), name="question-condition"),
    path("question-condition-types/", QuestionConditionTypesView.as_view(), name="question-condition-types"),
    path("flow/", FlowView.as_view(), name="flow"),
    path("question-flow/", QuestionFlowView.as_view(), name="question-flow"),
    path("flow-condition/", FlowConditionView.as_view(), name="flow-condition"),
    path("graph-editor/", GraphEditorView.as_view(), name="graph-editor"),
    path("graph/", GraphView.as_view(), name="graph"),
]
