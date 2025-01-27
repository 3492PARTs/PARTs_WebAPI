# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

import django
from django.db import models
from simple_history.models import HistoricalRecords


class QuestionType(models.Model):
    question_typ = models.CharField(primary_key=True, max_length=50)
    question_typ_nm = models.CharField(max_length=255)
    is_list = models.CharField(max_length=1, default="n")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return self.question_typ + " " + self.question_typ_nm


class FormType(models.Model):
    form_typ = models.CharField(primary_key=True, max_length=10)
    form_nm = models.CharField(max_length=255)

    def __str__(self):
        return self.form_typ + " " + self.form_nm


class FormSubType(models.Model):
    form_sub_typ = models.CharField(primary_key=True, max_length=10)
    form_sub_nm = models.CharField(max_length=255)
    form_typ = models.ForeignKey(FormType, models.PROTECT)
    order = models.IntegerField()

    def __str__(self):
        return self.form_sub_typ + " " + self.form_sub_nm


class QuestionFlow(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    single_run = models.BooleanField(default=False)
    form_typ = models.ForeignKey(FormType, models.PROTECT)
    form_sub_typ = models.ForeignKey(FormSubType, models.PROTECT, null=True)
    void_ind = models.CharField(max_length=1, default="n")
    """question = models.ForeignKey(Question, models.PROTECT)
    order = models.IntegerField()
    req_prev_flow = models.ForeignKey("self", models.PROTECT)
    req_prev_flow_value = models.CharField(2000)"""

    def __str__(self):
        return str(self.id) + " " + str(self.name)


class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    form_typ = models.ForeignKey(FormType, models.PROTECT)
    form_sub_typ = models.ForeignKey(FormSubType, models.PROTECT, null=True)
    question_typ = models.ForeignKey(QuestionType, models.PROTECT)
    question = models.CharField(max_length=1000)
    table_col_width = models.CharField(max_length=255)
    order = models.IntegerField()
    required = models.CharField(max_length=1)
    active = models.CharField(max_length=1, default="y")
    question_flow = models.ManyToManyField(QuestionFlow)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.question_id} {self.question}"


class QuestionOption(models.Model):
    question_opt_id = models.AutoField(primary_key=True)
    option = models.CharField(max_length=255)
    question = models.ForeignKey(Question, models.PROTECT)
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.question_opt_id} {self.option}"


class QuestionConditionType(models.Model):
    question_condition_typ = models.CharField(primary_key=True, max_length=10)
    question_condition_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.question_condition_typ} {self.question_condition_nm}"


class QuestionCondition(models.Model):
    question_condition_id = models.AutoField(primary_key=True)
    question_condition_typ = models.ForeignKey(QuestionConditionType, models.PROTECT)
    value = models.CharField(max_length=1000)
    question_from = models.ForeignKey(
        Question, models.PROTECT, related_name="condition_question_from"
    )
    question_to = models.ForeignKey(
        Question, models.PROTECT, related_name="condition_question_to"
    )
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.question_condition_id} : {self.condition}"


class QuestionFlowCondition(models.Model):
    id = models.AutoField(primary_key=True)
    question_flow_from = models.ForeignKey(
        QuestionFlow, models.PROTECT, related_name="condition_question_flow_from"
    )
    question_flow_to = models.ForeignKey(
        QuestionFlow, models.PROTECT, related_name="condition_question_flow_to"
    )
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id}"


class QuestionAggregateType(models.Model):
    question_aggregate_typ = models.CharField(primary_key=True, max_length=10)
    question_aggregate_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return self.question_aggregate_typ + " " + self.question_aggregate_nm


class QuestionAggregate(models.Model):
    question_aggregate_id = models.AutoField(primary_key=True)
    question_aggregate_typ = models.ForeignKey(QuestionAggregateType, models.PROTECT)
    questions = models.ManyToManyField(Question)
    field_name = models.CharField(max_length=1000)
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return str(self.question_aggregate_id) + " " + str(self.question_aggregate_typ)


class Response(models.Model):
    response_id = models.AutoField(primary_key=True)
    form_typ = models.ForeignKey(FormType, models.PROTECT)
    time = models.DateTimeField(default=django.utils.timezone.now)
    archive_ind = models.CharField(max_length=1, default="n")
    void_ind = models.CharField(max_length=1, default="n")
    history = HistoricalRecords()

    def __str__(self):
        return str(self.response_id) + " " + str(self.form_typ)


class QuestionAnswer(models.Model):
    question_answer_id = models.AutoField(primary_key=True)
    response = models.ForeignKey(
        Response, models.PROTECT, null=True, related_name="form_response"
    )
    question = models.ForeignKey(Question, models.PROTECT, null=True)
    question_flow = models.ForeignKey(QuestionFlow, models.PROTECT, null=True)
    answer = models.TextField(blank=True, null=True)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return str(self.question_answer_id) + " " + str(self.answer)


class QuestionFlowAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    question_answer = models.ForeignKey(QuestionAnswer, models.PROTECT, null=True)
    question = models.ForeignKey(Question, models.PROTECT)
    answer = models.TextField(blank=True, null=True)
    answer_time = models.TimeField(blank=True, null=True)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} {self.question}"


class GraphType(models.Model):
    graph_typ = models.CharField(primary_key=True, max_length=10)
    graph_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.graph_typ} {self.graph_nm}"


class Graph(models.Model):
    id = models.AutoField(primary_key=True)
    graph_typ = models.ForeignKey(GraphType, models.PROTECT)
    name = models.CharField(max_length=255)
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} {self.name}"


class GraphQuestionType(models.Model):
    graph_question_typ = models.CharField(primary_key=True, max_length=10)
    graph_question_nm = models.CharField(max_length=255)
    question_typ = models.ManyToManyField(QuestionType)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.graph_question_typ} {self.graph_question_nm}"


class GraphQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    graph = models.ForeignKey(Graph, models.PROTECT)
    question = models.ForeignKey(Question, models.PROTECT)
    graph_question_typ = models.ForeignKey(GraphQuestionType, models.PROTECT)
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.graph} : {self.question}"