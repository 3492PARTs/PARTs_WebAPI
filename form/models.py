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
        return f"{self.question_typ} : {self.question_typ_nm}"


class FormType(models.Model):
    form_typ = models.CharField(primary_key=True, max_length=10)
    form_nm = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.form_typ} : {self.form_nm}"


class FormSubType(models.Model):
    form_sub_typ = models.CharField(primary_key=True, max_length=10)
    form_sub_nm = models.CharField(max_length=255)
    form_typ = models.ForeignKey(FormType, models.PROTECT)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.form_sub_typ} : {self.form_sub_nm}"


class Flow(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    single_run = models.BooleanField(default=False)
    form_typ = models.ForeignKey(FormType, models.PROTECT)
    form_sub_typ = models.ForeignKey(FormSubType, models.PROTECT, null=True)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.name}"


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    form_typ = models.ForeignKey(FormType, models.PROTECT)
    form_sub_typ = models.ForeignKey(FormSubType, models.PROTECT, null=True)
    question_typ = models.ForeignKey(QuestionType, models.PROTECT)
    question = models.CharField(max_length=1000)
    table_col_width = models.CharField(max_length=255)
    order = models.IntegerField()
    svg = models.CharField(max_length=2000, null=True)
    required = models.CharField(max_length=1)
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    width = models.FloatField(null=True)
    height = models.FloatField(null=True)
    icon = models.CharField(max_length=255, null=True)
    icon_only = models.BooleanField(default=False)
    value_multiplier = models.IntegerField(null=True, default=None)
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} {self.question}"


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
        return f"{self.question_condition_id} : {self.value}"


class FlowCondition(models.Model):
    id = models.AutoField(primary_key=True)
    flow_from = models.ForeignKey(
        Flow, models.PROTECT, related_name="condition_flow_from"
    )
    flow_to = models.ForeignKey(
        Flow, models.PROTECT, related_name="condition_flow_to"
    )
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id}"


class FlowQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    flow = models.ForeignKey(
        Flow, models.PROTECT
    )
    question = models.ForeignKey(
        Question, models.PROTECT
    )
    order = models.IntegerField()
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.flow} : {self.question}"


class QuestionAggregateType(models.Model):
    question_aggregate_typ = models.CharField(primary_key=True, max_length=10)
    question_aggregate_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.question_aggregate_typ} : {self.question_aggregate_nm}"


class QuestionAggregate(models.Model):
    id = models.AutoField(primary_key=True)
    question_aggregate_typ = models.ForeignKey(QuestionAggregateType, models.PROTECT)
    questions = models.ManyToManyField(Question)
    field_name = models.CharField(max_length=1000)
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.question_aggregate_typ}"


class Response(models.Model):
    response_id = models.AutoField(primary_key=True)
    form_typ = models.ForeignKey(FormType, models.PROTECT)
    time = models.DateTimeField(default=django.utils.timezone.now)
    archive_ind = models.CharField(max_length=1, default="n")
    void_ind = models.CharField(max_length=1, default="n")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.response_id} : {self.form_typ}"


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    response = models.ForeignKey(
        Response, models.PROTECT, null=True, related_name="form_response"
    )
    question = models.ForeignKey(Question, models.PROTECT, null=True)
    flow = models.ForeignKey(Flow, models.PROTECT, null=True)
    value = models.TextField(blank=True, null=True)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.value}"


class FlowAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    answer = models.ForeignKey(Answer, models.PROTECT, null=True)
    question = models.ForeignKey(Question, models.PROTECT)
    value = models.TextField(blank=True, null=True)
    value_time = models.TimeField(blank=True, null=True)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.value}"


class GraphType(models.Model):
    graph_typ = models.CharField(primary_key=True, max_length=10)
    graph_nm = models.CharField(max_length=255)
    requires_bins = models.BooleanField(default=False)
    requires_categories = models.BooleanField(default=False)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.graph_typ} {self.graph_nm}"


class Graph(models.Model):
    id = models.AutoField(primary_key=True)
    graph_typ = models.ForeignKey(GraphType, models.PROTECT)
    name = models.CharField(max_length=255)
    scale_x = models.IntegerField()
    scale_y = models.IntegerField()
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} {self.name}"


class GraphBin(models.Model):
    id = models.AutoField(primary_key=True)
    graph = models.ForeignKey(Graph, models.PROTECT)
    bin = models.IntegerField()
    width = models.IntegerField()
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.bin} : {self.graph}"


class GraphCategory(models.Model):
    id = models.AutoField(primary_key=True)
    graph = models.ForeignKey(Graph, models.PROTECT)
    category = models.CharField(max_length=2000)
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.category} : {self.graph}"



class GraphCategoryAttribute(models.Model):
    id = models.AutoField(primary_key=True)
    graph_category = models.ForeignKey(GraphCategory, models.PROTECT)
    question = models.ForeignKey(Question, models.PROTECT, null=True)
    question_aggregate = models.ForeignKey(QuestionAggregate, models.PROTECT, null=True)
    question_condition_typ = models.ForeignKey(QuestionConditionType, models.PROTECT)
    value = models.CharField(max_length=1000)
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.graph_category} : {self.value}"


class GraphQuestionType(models.Model):
    graph_question_typ = models.CharField(primary_key=True, max_length=10)
    graph_question_nm = models.CharField(max_length=255)
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.graph_question_typ} {self.graph_question_nm}"


class GraphQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    graph = models.ForeignKey(Graph, models.PROTECT)
    graph_question_typ = models.ForeignKey(GraphQuestionType, models.PROTECT, null=True)
    question = models.ForeignKey(Question, models.PROTECT, null=True)
    question_aggregate = models.ForeignKey(QuestionAggregate, models.PROTECT, null=True)
    active = models.CharField(max_length=1, default="y")
    void_ind = models.CharField(max_length=1, default="n")

    def __str__(self):
        return f"{self.id} : {self.graph} : {self.question}"

