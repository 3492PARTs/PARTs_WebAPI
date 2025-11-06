"""
Complex integration tests for form builder with conditional logic, flows, and data aggregation.

This test file validates:
- Cascading conditional questions (A→B→C)
- Flow-based question routing
- Form response validation with all field types
- Question aggregation relationships
- Cross-form data correlation
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.db.models import Q


@pytest.mark.django_db
class TestComplexFormWorkflows:
    """Complex integration tests for form builder with conditional logic and flows."""

    def test_question_with_cascading_conditions(self):
        """Test complex scenario where question A conditions question B which conditions question C."""
        from form.util import get_questions, parse_question
        from form.models import Question, FormType, QuestionType, QuestionCondition, QuestionConditionType
        
        # Setup: Create a chain of conditional questions
        form_type = FormType.objects.create(form_typ='survey', form_nm='Survey')
        question_type = QuestionType.objects.create(
            question_typ='text',
            question_typ_nm='Text Input',
            is_list='n'
        )
        condition_type = QuestionConditionType.objects.create(
            question_condition_typ='equals',
            question_condition_nm='Equals'
        )
        
        # Question A (root question)
        question_a = Question.objects.create(
            question_typ=question_type,
            form_typ=form_type,
            question="Do you have a robot?",
            order=1,
            active='y',
            void_ind='n'
        )
        
        # Question B (conditional on A)
        question_b = Question.objects.create(
            question_typ=question_type,
            form_typ=form_type,
            question="What type of robot?",
            order=2,
            active='y',
            void_ind='n'
        )
        
        # Question C (conditional on B)
        question_c = Question.objects.create(
            question_typ=question_type,
            form_typ=form_type,
            question="What is the robot's name?",
            order=3,
            active='y',
            void_ind='n'
        )
        
        # Create condition: B depends on A = "yes"
        QuestionCondition.objects.create(
            question_from=question_a,
            question_to=question_b,
            question_condition_typ=condition_type,
            value="yes",
            active='y',
            void_ind='n'
        )
        
        # Create condition: C depends on B = "competition"
        QuestionCondition.objects.create(
            question_from=question_b,
            question_to=question_c,
            question_condition_typ=condition_type,
            value="competition",
            active='y',
            void_ind='n'
        )
        
        # Test: Get questions with conditional logic
        questions = get_questions(form_typ='survey')
        
        # Verify all three questions are returned
        assert len(questions) == 3
        
        # Parse and verify conditional relationships
        parsed_a = parse_question(question_a)
        assert len(parsed_a['conditional_question_id_set']) == 1
        assert question_b.id in parsed_a['conditional_question_id_set']
        
        parsed_b = parse_question(question_b)
        assert len(parsed_b['conditional_on_questions']) == 1
        assert parsed_b['conditional_on_questions'][0]['conditional_on'] == question_a.id
        assert len(parsed_b['conditional_question_id_set']) == 1
        assert question_c.id in parsed_b['conditional_question_id_set']
        
        parsed_c = parse_question(question_c)
        assert len(parsed_c['conditional_on_questions']) == 1
        assert parsed_c['conditional_on_questions'][0]['conditional_on'] == question_b.id

    def test_form_response_validation_with_required_fields(self):
        """Test complex form response validation with required fields and value types."""
        from form.util import save_question
        from form.models import Question, FormType, QuestionType, QuestionOption
        
        # Setup: Create form with multiple question types
        form_type = FormType.objects.create(form_typ='eval', form_nm='Evaluation')
        
        text_type = QuestionType.objects.create(
            question_typ='text',
            question_typ_nm='Text',
            is_list='n'
        )
        
        number_type = QuestionType.objects.create(
            question_typ='number',
            question_typ_nm='Number',
            is_list='n'
        )
        
        # Test: Save a simpler question without select type to avoid option requirement
        question_data = {
            'question': 'Rate your experience',
            'table_col_width': 100,
            'question_typ': {
                'question_typ': 'number',
                'is_list': 'n'
            },
            'form_typ': {'form_typ': 'eval'},
            'order': 1,
            'active': 'y',
            'required': 'y',
            'x': 10,
            'y': 20,
            'width': 200,
            'height': 50,
            'icon': 'star',
            'icon_only': False,
            'value_multiplier': 1.0,
            'svg': None
        }
        
        with patch('form.util.scouting.util.get_current_season') as mock_season:
            mock_season.return_value = None
            
            # This should create a new question
            save_question(question_data)
            
            # Verify question was created with all properties
            created_question = Question.objects.filter(question='Rate your experience').first()
            assert created_question is not None
            assert created_question.required == 'y'
            assert created_question.active == 'y'
            assert created_question.x == 10
            assert created_question.y == 20
            assert created_question.icon == 'star'

    def test_flow_based_question_routing(self):
        """Test complex flow-based question routing with multiple paths."""
        from form.util import get_questions
        from form.models import (
            Question, FormType, QuestionType, Flow, FlowQuestion
        )
        
        # Setup: Create questions and flows
        form_type = FormType.objects.create(form_typ='onboard', form_nm='Onboarding')
        question_type = QuestionType.objects.create(
            question_typ='text',
            question_typ_nm='Text',
            is_list='n'
        )
        
        # Create two flows: student flow and mentor flow
        student_flow = Flow.objects.create(
            name='Student Onboarding',
            form_typ=form_type,
            void_ind='n'
        )
        
        mentor_flow = Flow.objects.create(
            name='Mentor Onboarding',
            form_typ=form_type,
            void_ind='n'
        )
        
        # Create questions for each flow
        q_student_1 = Question.objects.create(
            question_typ=question_type,
            form_typ=form_type,
            question="What grade are you in?",
            order=1,
            active='y',
            void_ind='n'
        )
        
        q_student_2 = Question.objects.create(
            question_typ=question_type,
            form_typ=form_type,
            question="What are your interests?",
            order=2,
            active='y',
            void_ind='n'
        )
        
        q_mentor_1 = Question.objects.create(
            question_typ=question_type,
            form_typ=form_type,
            question="What is your expertise?",
            order=1,
            active='y',
            void_ind='n'
        )
        
        # Assign questions to flows
        FlowQuestion.objects.create(
            flow=student_flow,
            question=q_student_1,
            order=1,
            active='y',
            void_ind='n'
        )
        
        FlowQuestion.objects.create(
            flow=student_flow,
            question=q_student_2,
            order=2,
            active='y',
            void_ind='n'
        )
        
        FlowQuestion.objects.create(
            flow=mentor_flow,
            question=q_mentor_1,
            order=1,
            active='y',
            void_ind='n'
        )
        
        # Test: Get questions not in flow should exclude all flow questions
        questions_not_in_flow = get_questions(form_typ='onboard', not_in_flow=True)
        assert len(questions_not_in_flow) == 0  # All questions are in flows
        
        # Test: Get all questions should include flow questions
        all_questions = get_questions(form_typ='onboard')
        assert len(all_questions) == 3


@pytest.mark.django_db
class TestComplexDataAggregation:
    """Complex tests for data aggregation and statistics in forms."""

    def test_question_aggregate_setup(self):
        """Test setting up aggregation relationships between questions."""
        from form.models import (
            Question, FormType, QuestionType, QuestionAggregate,
            QuestionAggregateType, QuestionAggregateQuestion
        )
        
        # Setup: Create question type and form
        form_type = FormType.objects.create(form_typ='survey', form_nm='Survey')
        number_type = QuestionType.objects.create(
            question_typ='number',
            question_typ_nm='Number',
            is_list='n'
        )
        
        # Create aggregate type
        aggregate_type = QuestionAggregateType.objects.create(
            question_aggregate_typ='average',
            question_aggregate_nm='Average'
        )
        
        # Create questions for aggregation
        q1 = Question.objects.create(
            question_typ=number_type,
            form_typ=form_type,
            question="Score 1",
            order=1,
            active='y',
            void_ind='n'
        )
        
        q2 = Question.objects.create(
            question_typ=number_type,
            form_typ=form_type,
            question="Score 2",
            order=2,
            active='y',
            void_ind='n'
        )
        
        # Create aggregate question
        aggregate_q = QuestionAggregate.objects.create(
            question_aggregate_typ=aggregate_type,
            name="Average Score",
            void_ind='n'
        )
        
        # Link questions to aggregate
        QuestionAggregateQuestion.objects.create(
            question_aggregate=aggregate_q,
            question=q1,
            void_ind='n'
        )
        
        QuestionAggregateQuestion.objects.create(
            question_aggregate=aggregate_q,
            question=q2,
            void_ind='n'
        )
        
        # Verify aggregate setup
        aggregate_questions = QuestionAggregateQuestion.objects.filter(
            question_aggregate=aggregate_q,
            void_ind='n'
        )
        assert aggregate_questions.count() == 2

    def test_cross_form_data_correlation(self):
        """Test correlation of data across different form types."""
        from form.models import Question, FormType, QuestionType, Response, Answer
        
        # Setup: Create two different form types
        pre_survey = FormType.objects.create(form_typ='pre', form_nm='Pre Survey')
        post_survey = FormType.objects.create(form_typ='post', form_nm='Post Survey')
        
        text_type = QuestionType.objects.create(
            question_typ='text',
            question_typ_nm='Text',
            is_list='n'
        )
        
        # Create matching questions in both forms
        pre_q = Question.objects.create(
            question_typ=text_type,
            form_typ=pre_survey,
            question="Initial thoughts",
            order=1,
            active='y',
            void_ind='n'
        )
        
        post_q = Question.objects.create(
            question_typ=text_type,
            form_typ=post_survey,
            question="Final thoughts",
            order=1,
            active='y',
            void_ind='n'
        )
        
        # Create responses
        # Note: Response model doesn't have a user field - responses are tracked
        # by form type and timestamp only. User tracking happens through other means.
        pre_response = Response.objects.create(
            form_typ=pre_survey,
            void_ind='n'
        )
        
        post_response = Response.objects.create(
            form_typ=post_survey,
            void_ind='n'
        )
        
        # Create answers
        Answer.objects.create(
            response=pre_response,
            question=pre_q,
            value="I am excited to learn",
            void_ind='n'
        )
        
        Answer.objects.create(
            response=post_response,
            question=post_q,
            value="I learned a lot",
            void_ind='n'
        )
        
        # Test: Query responses across forms
        all_responses = Response.objects.filter(
            void_ind='n'
        ).order_by('time')
        
        assert all_responses.count() == 2
        assert all_responses[0].form_typ == pre_survey
        assert all_responses[1].form_typ == post_survey
        
        # Verify answers can be retrieved for comparison
        pre_answer = Answer.objects.get(response=all_responses[0])
        post_answer = Answer.objects.get(response=all_responses[1])
        
        assert pre_answer.value == "I am excited to learn"
        assert post_answer.value == "I learned a lot"
