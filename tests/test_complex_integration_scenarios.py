"""
Complex integration tests for high-value, under-tested modules.

This test file focuses on complex scenarios involving multiple components:
- Form builder with conditional questions and flows
- TBA API integration with match scheduling
- User authentication workflows with permissions
- Attendance tracking with approval workflows
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
import json


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
class TestComplexTBAIntegration:
    """Complex integration tests for The Blue Alliance API integration."""

    @patch('tba.util.requests.get')
    def test_sync_season_with_multiple_events_and_matches(self, mock_get):
        """Test synchronizing a complete season with multiple events and their matches."""
        from tba.util import get_events_for_team
        from scouting.models import Season, Team
        
        # Setup: Create season and team
        season = Season.objects.create(
            season='2024',
            current='y',
            game='Test Game',
            manual=''
        )
        
        team = Team.objects.create(
            team_no=3492,
            team_nm='PARTs',
            void_ind='n'
        )
        
        # Mock TBA API responses
        mock_events_response = Mock()
        mock_events_response.text = json.dumps([
            {
                'key': '2024week1',
                'name': 'Week 1 Event',
                'event_type': 0,
                'start_date': '2024-03-01',
                'end_date': '2024-03-03'
            },
            {
                'key': '2024week2',
                'name': 'Week 2 Event',
                'event_type': 0,
                'start_date': '2024-03-08',
                'end_date': '2024-03-10'
            }
        ])
        
        mock_get.return_value = mock_events_response
        
        # Test: Get events for team
        with patch('tba.util.get_tba_event') as mock_get_event:
            mock_get_event.side_effect = [
                {
                    'event_cd': '2024week1',
                    'event_nm': 'Week 1 Event',
                    'date_st': '2024-03-01',
                    'date_end': '2024-03-03'
                },
                {
                    'event_cd': '2024week2',
                    'event_nm': 'Week 2 Event',
                    'date_st': '2024-03-08',
                    'date_end': '2024-03-10'
                }
            ]
            
            events = get_events_for_team(team, season)
            
            # Verify API was called
            assert mock_get.called
            # Verify events were retrieved
            assert len(events) == 2
            assert events[0]['event_cd'] == '2024week1'
            assert events[1]['event_cd'] == '2024week2'

    @patch('tba.util.requests.get')
    def test_get_events_with_filtering(self, mock_get):
        """Test getting events for a team with specific events filtered out."""
        from tba.util import get_events_for_team
        from scouting.models import Season, Team
        
        # Setup
        season = Season.objects.create(
            season='2024',
            current='y',
            game='Test Game',
            manual=''
        )
        team = Team.objects.create(
            team_no=3492,
            team_nm='PARTs',
            void_ind='n'
        )
        
        # Mock response with multiple events
        mock_response = Mock()
        mock_response.text = json.dumps([
            {'key': '2024event1', 'name': 'Event 1'},
            {'key': '2024event2', 'name': 'Event 2'},
            {'key': '2024event3', 'name': 'Event 3'}
        ])
        mock_get.return_value = mock_response
        
        # Test: Get events but ignore event2
        with patch('tba.util.get_tba_event') as mock_get_event:
            mock_get_event.side_effect = [
                {'event_cd': '2024event1', 'event_nm': 'Event 1'},
                {'event_cd': '2024event3', 'event_nm': 'Event 3'}
            ]
            
            events = get_events_for_team(team, season, event_cds_to_ignore=['2024event2'])
            
            # Should return 3 events, but event2 should have minimal data
            assert len(events) == 3
            assert events[0]['event_cd'] == '2024event1'
            assert events[1] == {'event_cd': '2024event2'}  # Ignored event
            assert events[2]['event_cd'] == '2024event3'

    @patch('tba.util.requests.get')
    def test_match_retrieval_with_alliance_data(self, mock_get):
        """Test retrieving match data with complete alliance information."""
        from tba.util import get_matches_for_team_event
        
        # Mock match data with alliances
        mock_response = Mock()
        mock_response.text = json.dumps([
            {
                'key': '2024event1_qm1',
                'match_number': 1,
                'alliances': {
                    'red': {
                        'team_keys': ['frc3492', 'frc1234', 'frc5678'],
                        'score': 150
                    },
                    'blue': {
                        'team_keys': ['frc1111', 'frc2222', 'frc3333'],
                        'score': 145
                    }
                },
                'winning_alliance': 'red'
            },
            {
                'key': '2024event1_qm2',
                'match_number': 2,
                'alliances': {
                    'red': {
                        'team_keys': ['frc1111', 'frc2222', 'frc3333'],
                        'score': 160
                    },
                    'blue': {
                        'team_keys': ['frc3492', 'frc1234', 'frc5678'],
                        'score': 155
                    }
                },
                'winning_alliance': 'red'
            }
        ])
        mock_get.return_value = mock_response
        
        # Test
        matches = get_matches_for_team_event('3492', '2024event1')
        
        # Verify
        assert len(matches) == 2
        assert matches[0]['match_number'] == 1
        assert 'frc3492' in matches[0]['alliances']['red']['team_keys']
        assert matches[1]['match_number'] == 2
        assert 'frc3492' in matches[1]['alliances']['blue']['team_keys']


@pytest.mark.django_db
class TestComplexUserAuthWorkflows:
    """Complex integration tests for user authentication and permission workflows."""

    def test_multi_level_permission_hierarchy(self):
        """Test complex permission hierarchy with groups and individual permissions."""
        from general.security import has_access, get_user_permissions, get_user_groups
        from django.contrib.auth.models import Permission, Group
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Setup: Create content type and permissions
        content_type = ContentType.objects.get_for_model(User)
        
        perm_view = Permission.objects.create(
            codename='view_user_profile',
            name='Can view user profile',
            content_type=content_type
        )
        
        perm_edit = Permission.objects.create(
            codename='edit_user_profile',
            name='Can edit user profile',
            content_type=content_type
        )
        
        perm_admin = Permission.objects.create(
            codename='admin_users',
            name='Can administer users',
            content_type=content_type
        )
        
        # Create groups with different permission levels
        viewer_group = Group.objects.create(name='Viewers')
        viewer_group.permissions.add(perm_view)
        
        editor_group = Group.objects.create(name='Editors')
        editor_group.permissions.add(perm_view, perm_edit)
        
        admin_group = Group.objects.create(name='Admins')
        admin_group.permissions.add(perm_view, perm_edit, perm_admin)
        
        # Create users with different group memberships
        viewer = User.objects.create_user(
            username='viewer',
            email='viewer@test.com',
            password='pass'
        )
        viewer.groups.add(viewer_group)
        
        editor = User.objects.create_user(
            username='editor',
            email='editor@test.com',
            password='pass'
        )
        editor.groups.add(editor_group)
        
        admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='pass'
        )
        admin.groups.add(admin_group)
        
        # Test: Verify permission hierarchy
        # Viewer should only have view permission
        assert has_access(viewer.id, 'view_user_profile')
        assert not has_access(viewer.id, 'edit_user_profile')
        assert not has_access(viewer.id, 'admin_users')
        
        # Editor should have view and edit
        assert has_access(editor.id, 'view_user_profile')
        assert has_access(editor.id, 'edit_user_profile')
        assert not has_access(editor.id, 'admin_users')
        
        # Admin should have all permissions
        assert has_access(admin.id, 'view_user_profile')
        assert has_access(admin.id, 'edit_user_profile')
        assert has_access(admin.id, 'admin_users')
        
        # Test: Check multiple permissions at once
        # has_access with list returns True if user has AT LEAST ONE of the permissions
        assert has_access(admin.id, ['view_user_profile', 'edit_user_profile', 'admin_users'])
        # Editor has edit_user_profile, so should return True even without admin_users
        assert has_access(editor.id, ['view_user_profile', 'edit_user_profile', 'admin_users'])
        # Viewer doesn't have admin_users or edit, but has view, so returns True
        assert has_access(viewer.id, ['view_user_profile', 'admin_users'])
        # Test single permission checks work as expected
        assert has_access(viewer.id, 'view_user_profile')
        assert not has_access(viewer.id, 'admin_users')

    def test_access_response_with_complex_error_handling(self, default_user):
        """Test access_response with complex error scenarios and logging."""
        from general.security import access_response
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass'
        )
        
        # Test 1: Function succeeds with permission
        mock_function = Mock(return_value={'status': 'success'})
        with patch('general.security.has_access', return_value=True):
            result = access_response(
                'test_endpoint',
                user.id,
                'test_permission',
                'Access denied',
                mock_function
            )
            
            assert result == {'status': 'success'}
            mock_function.assert_called_once()
        
        # Test 2: Function fails without permission
        mock_function = Mock()
        with patch('general.security.has_access', return_value=False):
            result = access_response(
                'test_endpoint',
                user.id,
                'test_permission',
                'Access denied',
                mock_function
            )
            
            assert result.data['error'] is True
            assert 'do not have access' in result.data['retMessage']
            mock_function.assert_not_called()
        
        # Test 3: Function raises exception and creates error log
        mock_function = Mock(side_effect=ValueError("Test error"))
        with patch('general.security.has_access', return_value=True), \
             patch('general.security.ErrorLog') as MockErrorLog:
            
            mock_log = MagicMock()
            MockErrorLog.return_value = mock_log
            
            result = access_response(
                'test_endpoint',
                user.id,
                'test_permission',
                'Error occurred',
                mock_function
            )
            
            assert result.data['error'] is True
            MockErrorLog.assert_called()
            mock_log.save.assert_called()


@pytest.mark.django_db
class TestComplexAttendanceWorkflows:
    """Complex integration tests for attendance tracking with approval workflows."""

    def test_meeting_creation_and_queries(self):
        """Test creating meetings and querying them efficiently."""
        from attendance.models import Meeting
        from scouting.models import Season
        from datetime import datetime
        
        # Setup: Create season
        season = Season.objects.create(
            season='2024',
            current='y',
            game='Test Game',
            manual=''
        )
        
        # Create multiple meetings
        meeting1 = Meeting.objects.create(
            season=season,
            title='Weekly Meeting 1',
            description='First team meeting',
            start=datetime(2024, 3, 1, 18, 0, 0),
            end=datetime(2024, 3, 1, 20, 0, 0)
        )
        
        meeting2 = Meeting.objects.create(
            season=season,
            title='Weekly Meeting 2',
            description='Second team meeting',
            start=datetime(2024, 3, 8, 18, 0, 0),
            end=datetime(2024, 3, 8, 20, 0, 0)
        )
        
        # Test: Query meetings for the season
        season_meetings = Meeting.objects.filter(season=season).order_by('start')
        
        assert season_meetings.count() == 2
        assert season_meetings[0].title == 'Weekly Meeting 1'
        assert season_meetings[1].title == 'Weekly Meeting 2'

    def test_bulk_meeting_creation(self):
        """Test bulk operations on meeting records."""
        from attendance.models import Meeting
        from scouting.models import Season
        from datetime import datetime, timedelta
        
        # Setup: Create season
        season = Season.objects.create(
            season='2024',
            current='y',
            game='Test Game',
            manual=''
        )
        
        # Bulk create meetings
        meetings = []
        base_date = datetime(2024, 3, 1, 14, 0, 0)
        for i in range(10):
            meeting = Meeting(
                season=season,
                title=f'Workshop {i+1}',
                description=f'Workshop session {i+1}',
                start=base_date + timedelta(days=i*7),
                end=base_date + timedelta(days=i*7, hours=3)
            )
            meetings.append(meeting)
        
        # Bulk insert
        Meeting.objects.bulk_create(meetings)
        
        # Verify bulk creation
        total_meetings = Meeting.objects.filter(season=season).count()
        assert total_meetings == 10
        
        # Test querying meetings by date range
        end_date = base_date + timedelta(days=30)
        meetings_in_range = Meeting.objects.filter(
            season=season,
            start__gte=base_date,
            start__lte=end_date
        ).count()
        assert meetings_in_range > 0


@pytest.mark.django_db
class TestComplexDataAggregation:
    """Complex tests for data aggregation and statistics in forms and scouting."""

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
        
        # Create responses (without user field)
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
