"""
Comprehensive tests for Form model __str__ methods to increase coverage.
"""
import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestFormModelStringMethods:
    """Test __str__ methods for form app models."""
    
    def test_question_type_str(self):
        """Test QuestionType __str__ method."""
        from form.models import QuestionType
        
        q_type = QuestionType.objects.create(
            question_typ="text",
            question_typ_nm="Text Input"
        )
        str_result = str(q_type)
        assert "text" in str_result
        assert "Text Input" in str_result
    
    def test_form_type_str(self):
        """Test FormType __str__ method."""
        from form.models import FormType
        
        form_type = FormType.objects.create(
            form_typ="survey",
            form_nm="Survey Form"
        )
        str_result = str(form_type)
        assert "survey" in str_result
        assert "Survey Form" in str_result
    
    def test_form_sub_type_str(self):
        """Test FormSubType __str__ method."""
        from form.models import FormType, FormSubType
        
        form_type = FormType.objects.create(
            form_typ="quiz",
            form_nm="Quiz Form"
        )
        
        sub_type = FormSubType.objects.create(
            form_sub_typ="multi",
            form_sub_nm="Multiple Choice",
            form_typ=form_type,
            order=1
        )
        str_result = str(sub_type)
        assert "multi" in str_result
        assert "Multiple Choice" in str_result
    
    def test_flow_str(self):
        """Test Flow __str__ method."""
        from form.models import FormType, Flow
        
        form_type = FormType.objects.create(
            form_typ="process",
            form_nm="Process Form"
        )
        
        flow = Flow.objects.create(
            name="Registration Flow",
            form_typ=form_type
        )
        str_result = str(flow)
        assert str(flow.id) in str_result
        assert "Registration Flow" in str_result
    
    def test_question_str(self):
        """Test Question __str__ method."""
        from form.models import FormType, QuestionType, Question
        
        form_type = FormType.objects.create(
            form_typ="feedback",
            form_nm="Feedback Form"
        )
        
        q_type = QuestionType.objects.create(
            question_typ="rating",
            question_typ_nm="Rating Scale"
        )
        
        question = Question.objects.create(
            form_typ=form_type,
            question_typ=q_type,
            question="How would you rate this?",
            table_col_width="100",
            order=1,
            required="y"
        )
        str_result = str(question)
        assert str(question.id) in str_result
        assert "How would you rate this?" in str_result
    
    def test_question_option_str(self):
        """Test QuestionOption __str__ method."""
        from form.models import FormType, QuestionType, Question, QuestionOption
        
        form_type = FormType.objects.create(
            form_typ="select",
            form_nm="Selection Form"
        )
        
        q_type = QuestionType.objects.create(
            question_typ="choice",
            question_typ_nm="Choice"
        )
        
        question = Question.objects.create(
            form_typ=form_type,
            question_typ=q_type,
            question="Pick one",
            table_col_width="100",
            order=1,
            required="y"
        )
        
        option = QuestionOption.objects.create(
            question=question,
            option="Option A"
        )
        str_result = str(option)
        assert str(option.question_opt_id) in str_result
        assert "Option A" in str_result
    
    def test_question_condition_type_str(self):
        """Test QuestionConditionType __str__ method."""
        from form.models import QuestionConditionType
        
        cond_type = QuestionConditionType.objects.create(
            question_condition_typ="eq",
            question_condition_nm="Equals"
        )
        str_result = str(cond_type)
        assert "eq" in str_result
        assert "Equals" in str_result
    
    def test_question_condition_str(self):
        """Test QuestionCondition __str__ method."""
        from form.models import FormType, QuestionType, Question, QuestionCondition, QuestionConditionType
        
        form_type = FormType.objects.create(
            form_typ="cond",
            form_nm="Conditional Form"
        )
        
        q_type = QuestionType.objects.create(
            question_typ="bool",
            question_typ_nm="Boolean"
        )
        
        question1 = Question.objects.create(
            form_typ=form_type,
            question_typ=q_type,
            question="Condition from",
            table_col_width="100",
            order=1,
            required="y"
        )
        
        question2 = Question.objects.create(
            form_typ=form_type,
            question_typ=q_type,
            question="Condition to",
            table_col_width="100",
            order=2,
            required="y"
        )
        
        cond_type = QuestionConditionType.objects.create(
            question_condition_typ="eq",
            question_condition_nm="Equals"
        )
        
        condition = QuestionCondition.objects.create(
            question_from=question1,
            question_to=question2,
            question_condition_typ=cond_type,
            value="yes"
        )
        str_result = str(condition)
        assert str(condition.question_condition_id) in str_result
        assert "yes" in str_result
    
    def test_flow_condition_str(self):
        """Test FlowCondition __str__ method."""
        from form.models import FormType, Flow, FlowCondition
        
        form_type = FormType.objects.create(
            form_typ="flow",
            form_nm="Flow Form"
        )
        
        flow1 = Flow.objects.create(
            name="Flow A",
            form_typ=form_type
        )
        
        flow2 = Flow.objects.create(
            name="Flow B",
            form_typ=form_type
        )
        
        flow_cond = FlowCondition.objects.create(
            flow_from=flow1,
            flow_to=flow2
        )
        str_result = str(flow_cond)
        assert str(flow_cond.id) in str_result
    
    def test_flow_question_str(self):
        """Test FlowQuestion __str__ method."""
        from form.models import FormType, QuestionType, Flow, Question, FlowQuestion
        
        form_type = FormType.objects.create(
            form_typ="fq",
            form_nm="Flow Question Test"
        )
        
        q_type = QuestionType.objects.create(
            question_typ="txt",
            question_typ_nm="Text"
        )
        
        flow = Flow.objects.create(
            name="Test Flow",
            form_typ=form_type
        )
        
        question = Question.objects.create(
            form_typ=form_type,
            question_typ=q_type,
            question="Flow question",
            table_col_width="100",
            order=1,
            required="y"
        )
        
        flow_question = FlowQuestion.objects.create(
            flow=flow,
            question=question,
            order=1
        )
        str_result = str(flow_question)
        assert str(flow_question.id) in str_result
    
    def test_question_aggregate_type_str(self):
        """Test QuestionAggregateType __str__ method."""
        from form.models import QuestionAggregateType
        
        agg_type = QuestionAggregateType.objects.create(
            question_aggregate_typ="sum",
            question_aggregate_nm="Sum"
        )
        str_result = str(agg_type)
        assert "sum" in str_result
        assert "Sum" in str_result
    
    def test_question_aggregate_str(self):
        """Test QuestionAggregate __str__ method."""
        from form.models import QuestionAggregateType, QuestionAggregate
        
        agg_type = QuestionAggregateType.objects.create(
            question_aggregate_typ="avg",
            question_aggregate_nm="Average"
        )
        
        aggregate = QuestionAggregate.objects.create(
            question_aggregate_typ=agg_type,
            name="Average Score"
        )
        str_result = str(aggregate)
        assert str(aggregate.id) in str_result
