"""
Comprehensive tests for scouting/field module
Tests utility functions and views for field scouting
"""

import pytest
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from django.db.models import Q

from scouting.field import util as field_util
from scouting.field.views import (
    FormView,
    ResponseColumnsView,
    ResponsesView,
    CheckInView,
    ScoutingResponsesView,
)
from scouting.models import (
    Season,
    Event,
    Team,
    Match,
    FieldResponse,
    FieldSchedule,
    EventTeamInfo,
    UserInfo,
    Question as ScoutingQuestion,
)
from form.models import (
    FormType,
    FormSubType,
    QuestionType,
    Question,
    Response,
    Answer,
    QuestionAggregate,
    QuestionAggregateQuestion,
    QuestionAggregateType,
    Flow,
    FlowAnswer,
    FlowQuestion,
)

User = get_user_model()


# ==================== Fixtures ====================


@pytest.fixture
def test_user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user with all permissions"""
    user = User.objects.create_user(
        username='admin',
        password='admin123',
        email='admin@example.com',
        is_staff=True,
        is_superuser=True
    )
    return user


@pytest.fixture
def season(db):
    """Create a test season"""
    return Season.objects.create(
        season=2024,
        current='y',
        void_ind='n'
    )


@pytest.fixture
def event(db, season):
    """Create a test event"""
    return Event.objects.create(
        event_nm='Test Event',
        event_cd='TEST2024',
        season=season,
        current='y',
        competition_page_active='y',
        void_ind='n',
        timezone='America/New_York',
        date_st=timezone.now().date(),
        date_end=(timezone.now() + timedelta(days=2)).date()
    )


@pytest.fixture
def team(db):
    """Create a test team"""
    return Team.objects.create(
        team_no=3492,
        team_nm='PARTs',
        void_ind='n'
    )


@pytest.fixture
def team_3492(db):
    """Create team 3492 specifically"""
    return Team.objects.create(
        team_no=3492,
        team_nm='PARTs',
        void_ind='n'
    )


@pytest.fixture
def match(db, event, team):
    """Create a test match"""
    return Match.objects.create(
        event=event,
        match_number=1,
        comp_level='qm',
        comp_level_order=1,
        red_one=team,
        void_ind='n'
    )


@pytest.fixture
def field_form_type(db):
    """Create field form type"""
    return FormType.objects.create(
        form_typ='field',
        form_nm='Field Scouting',
        void_ind='n'
    )


@pytest.fixture
def field_sub_type(db, field_form_type):
    """Create field form sub type"""
    return FormSubType.objects.create(
        form_sub_typ='auto',
        form_sub_nm='Autonomous',
        form_typ=field_form_type,
        void_ind='n'
    )


@pytest.fixture
def question_type(db):
    """Create a question type"""
    return QuestionType.objects.create(
        question_typ='text',
        question_typ_nm='Text Input',
        answer_options='',
        void_ind='n'
    )


@pytest.fixture
def field_question(db, field_form_type, field_sub_type, question_type):
    """Create a field scouting question"""
    return Question.objects.create(
        question='Test Question',
        question_typ=question_type,
        form_typ=field_form_type,
        form_sub_typ=field_sub_type,
        order=1,
        active='y',
        void_ind='n',
        table_col_width='100px'
    )


@pytest.fixture
def scouting_question(db, season, field_question):
    """Create a scouting question"""
    return ScoutingQuestion.objects.create(
        season=season,
        question=field_question,
        void_ind='n'
    )


@pytest.fixture
def form_response(db, field_form_type):
    """Create a form response"""
    return Response.objects.create(
        form_typ=field_form_type,
        void_ind='n'
    )


@pytest.fixture
def field_response(db, event, team, match, test_user, form_response):
    """Create a field response"""
    return FieldResponse.objects.create(
        event=event,
        team=team,
        match=match,
        user=test_user,
        response=form_response,
        time=timezone.now(),
        void_ind='n'
    )


@pytest.fixture
def api_rf():
    """API Request Factory"""
    return APIRequestFactory()


# ==================== Utility Function Tests ====================


@pytest.mark.django_db
class TestGetTableColumns:
    """Tests for get_table_columns function"""
    
    def test_basic_table_columns(self, db):
        """Test basic table column generation"""
        columns = field_util.get_table_columns([])
        
        # Should have team_id, rank, match columns at minimum
        assert any(col['PropertyName'] == 'team_id' for col in columns)
        assert any(col['PropertyName'] == 'rank' for col in columns)
        assert any(col['PropertyName'] == 'match' for col in columns)
        # Should have user and time at the end
        assert any(col['PropertyName'] == 'user' for col in columns)
        assert any(col['PropertyName'] == 'time' for col in columns)
    
    @patch('form.util.get_form_questions')
    def test_table_columns_with_questions(self, mock_get_form_questions, field_question, field_sub_type):
        """Test table columns include questions"""
        mock_get_form_questions.return_value = {
            'form_sub_types': [
                {
                    'questions': [
                        {
                            'id': field_question.id,
                            'question': 'Test Q',
                            'order': 1,
                            'table_col_width': '100px',
                            'form_sub_typ': field_sub_type,
                            'conditional_on_questions': []
                        }
                    ],
                    'flows': []
                }
            ]
        }
        
        columns = field_util.get_table_columns([])
        
        # Should have question column
        question_cols = [c for c in columns if c['PropertyName'] == f'ans{field_question.id}']
        assert len(question_cols) == 1
        assert 'Test Q' in question_cols[0]['ColLabel']
    
    def test_table_columns_with_aggregates(self, db):
        """Test table columns include question aggregates"""
        qa_type = QuestionAggregateType.objects.create(
            question_aggregate_typ='sum',
            question_aggregate_nm='Sum',
            void_ind='n'
        )
        qa = QuestionAggregate.objects.create(
            name='Test Aggregate',
            question_aggregate_typ=qa_type,
            horizontal=True,
            active='y',
            void_ind='n'
        )
        
        with patch('form.util.get_form_questions') as mock:
            mock.return_value = {'form_sub_types': []}
            columns = field_util.get_table_columns([qa])
        
        # Should have aggregate column
        agg_cols = [c for c in columns if c['PropertyName'] == f'ans_sqa{qa.id}']
        assert len(agg_cols) == 1
        assert 'Test Aggregate' in agg_cols[0]['ColLabel']


@pytest.mark.django_db
class TestGetResponses:
    """Tests for get_responses function"""
    
    def test_get_responses_basic(self, event, team, test_user, field_response):
        """Test basic response retrieval"""
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = field_util.get_responses()
            
            assert 'scoutAnswers' in result
            assert 'current_season' in result
            assert 'current_event' in result
            assert result['current_season'] == event.season
            assert result['current_event'] == event
    
    def test_get_responses_by_team(self, event, team, test_user, field_response):
        """Test retrieving responses filtered by team"""
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = field_util.get_responses(team=team.team_no)
            
            assert len(result['scoutAnswers']) > 0
            assert result['scoutAnswers'][0]['team_id'] == team.team_no
    
    def test_get_responses_by_user(self, event, team, test_user, field_response):
        """Test retrieving responses filtered by user"""
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = field_util.get_responses(user=test_user.id)
            
            assert len(result['scoutAnswers']) > 0
            assert result['scoutAnswers'][0]['user_id'] == test_user.id
    
    def test_get_responses_pagination(self, event, team, test_user, form_response):
        """Test response pagination"""
        # Create multiple responses
        for i in range(50):
            FieldResponse.objects.create(
                event=event,
                team=team,
                user=test_user,
                response=form_response,
                time=timezone.now(),
                void_ind='n'
            )
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = field_util.get_responses(pg=1)
            
            # Should paginate (40 per page)
            assert len(result['scoutAnswers']) == 40
            assert result['next'] == 2
            assert result['previous'] is None
    
    def test_get_responses_with_answers(self, event, team, test_user, field_response, field_question):
        """Test responses include answer data"""
        # Create an answer
        Answer.objects.create(
            response=field_response.response,
            question=field_question,
            value='Test Answer',
            void_ind='n'
        )
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = field_util.get_responses()
            
            assert len(result['scoutAnswers']) > 0
            response = result['scoutAnswers'][0]
            assert f'ans{field_question.id}' in response
            assert response[f'ans{field_question.id}'] == 'Test Answer'
    
    def test_get_responses_with_rank(self, event, team, test_user, field_response):
        """Test responses include team rank"""
        # Create event team info with rank
        EventTeamInfo.objects.create(
            event=event,
            team=team,
            rank=5,
            void_ind='n'
        )
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = field_util.get_responses()
            
            assert len(result['scoutAnswers']) > 0
            assert result['scoutAnswers'][0]['rank'] == 5
    
    def test_get_responses_excludes_void(self, event, team, test_user, form_response):
        """Test void responses are excluded"""
        # Create void response
        FieldResponse.objects.create(
            event=event,
            team=team,
            user=test_user,
            response=form_response,
            time=timezone.now(),
            void_ind='y'  # Voided
        )
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = field_util.get_responses()
            
            # Should not include void response
            assert len(result['scoutAnswers']) == 0
    
    def test_get_responses_excludes_eliminated_users(self, event, team, test_user, field_response):
        """Test responses from users with eliminate_results=True are excluded"""
        # Create user info with eliminate_results
        UserInfo.objects.create(
            user=test_user,
            eliminate_results=True,
            void_ind='n'
        )
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = field_util.get_responses()
            
            # Should exclude responses from eliminated users
            assert len(result['scoutAnswers']) == 0


@pytest.mark.django_db
class TestGetRemovedResponses:
    """Tests for get_removed_responses function"""
    
    def test_get_removed_responses_basic(self, event, team, test_user, form_response):
        """Test getting void responses"""
        void_response = FieldResponse.objects.create(
            event=event,
            team=team,
            user=test_user,
            response=form_response,
            time=timezone.now(),
            void_ind='y'
        )
        
        removed = field_util.get_removed_responses()
        
        assert void_response in removed
    
    def test_get_removed_responses_with_void_response_object(self, event, team, test_user):
        """Test getting responses with void response objects"""
        void_form_response = Response.objects.create(
            form_typ_id='field',
            void_ind='y'
        )
        field_resp = FieldResponse.objects.create(
            event=event,
            team=team,
            user=test_user,
            response=void_form_response,
            time=timezone.now(),
            void_ind='n'
        )
        
        removed = field_util.get_removed_responses()
        
        assert field_resp in removed
    
    def test_get_removed_responses_before_id(self, event, team, test_user, form_response):
        """Test getting void responses before a specific ID"""
        resp1 = FieldResponse.objects.create(
            event=event,
            team=team,
            user=test_user,
            response=form_response,
            time=timezone.now(),
            void_ind='y'
        )
        resp2 = FieldResponse.objects.create(
            event=event,
            team=team,
            user=test_user,
            response=form_response,
            time=timezone.now(),
            void_ind='y'
        )
        
        removed = field_util.get_removed_responses(before_scout_field_id=resp1.id)
        
        assert resp1 in removed
        assert resp2 not in removed


@pytest.mark.django_db
class TestGetFieldQuestionAggregates:
    """Tests for get_field_question_aggregates function"""
    
    def test_get_field_question_aggregates_basic(
        self, season, field_form_type, field_question, scouting_question
    ):
        """Test getting field question aggregates"""
        qa_type = QuestionAggregateType.objects.create(
            question_aggregate_typ='sum',
            question_aggregate_nm='Sum',
            void_ind='n'
        )
        qa = QuestionAggregate.objects.create(
            name='Test Aggregate',
            question_aggregate_typ=qa_type,
            horizontal=True,
            active='y',
            void_ind='n'
        )
        QuestionAggregateQuestion.objects.create(
            question_aggregate=qa,
            question=field_question,
            active='y',
            void_ind='n'
        )
        
        result = field_util.get_field_question_aggregates(season)
        
        assert qa in result
    
    def test_get_field_question_aggregates_excludes_vertical(
        self, season, field_form_type, field_question, scouting_question
    ):
        """Test vertical aggregates are excluded"""
        qa_type = QuestionAggregateType.objects.create(
            question_aggregate_typ='sum',
            question_aggregate_nm='Sum',
            void_ind='n'
        )
        qa = QuestionAggregate.objects.create(
            name='Vertical Aggregate',
            question_aggregate_typ=qa_type,
            horizontal=False,  # Not horizontal
            active='y',
            void_ind='n'
        )
        
        result = field_util.get_field_question_aggregates(season)
        
        assert qa not in result


@pytest.mark.django_db
class TestCheckInScout:
    """Tests for check_in_scout function"""
    
    def test_check_in_red_one(self, test_user, match):
        """Test checking in red_one scout"""
        sfs = FieldSchedule.objects.create(
            match=match,
            red_one=test_user,
            void_ind='n'
        )
        
        result = field_util.check_in_scout(sfs, test_user.id)
        
        assert result == "Successfully checked in scout for their shift."
        sfs.refresh_from_db()
        assert sfs.red_one_check_in is not None
    
    def test_check_in_blue_three(self, test_user, match):
        """Test checking in blue_three scout"""
        sfs = FieldSchedule.objects.create(
            match=match,
            blue_three=test_user,
            void_ind='n'
        )
        
        result = field_util.check_in_scout(sfs, test_user.id)
        
        assert result == "Successfully checked in scout for their shift."
        sfs.refresh_from_db()
        assert sfs.blue_three_check_in is not None
    
    def test_check_in_already_checked_in(self, test_user, match):
        """Test checking in when already checked in"""
        sfs = FieldSchedule.objects.create(
            match=match,
            red_one=test_user,
            red_one_check_in=timezone.now(),  # Already checked in
            void_ind='n'
        )
        
        result = field_util.check_in_scout(sfs, test_user.id)
        
        assert result == ""
    
    def test_check_in_wrong_user(self, test_user, admin_user, match):
        """Test checking in when user is not assigned"""
        sfs = FieldSchedule.objects.create(
            match=match,
            red_one=admin_user,  # Different user
            void_ind='n'
        )
        
        result = field_util.check_in_scout(sfs, test_user.id)
        
        assert result == ""


@pytest.mark.django_db
class TestGetFieldForm:
    """Tests for get_field_form function"""
    
    @patch('scouting.util.get_field_form')
    @patch('form.util.get_form_questions')
    def test_get_field_form(self, mock_get_questions, mock_get_field_form):
        """Test getting field form"""
        mock_get_field_form.return_value = {'id': 1, 'name': 'Field Form'}
        mock_get_questions.return_value = {
            'form_sub_types': [
                {'id': 1, 'name': 'Auto'}
            ]
        }
        
        result = field_util.get_field_form()
        
        assert 'field_form' in result
        assert 'form_sub_types' in result
        assert result['field_form']['id'] == 1


@pytest.mark.django_db
class TestGetScoutingResponses:
    """Tests for get_scouting_responses function"""
    
    def test_get_scouting_responses(self, event, team, match, test_user, field_response, field_question):
        """Test getting recent scouting responses"""
        # Create an answer
        Answer.objects.create(
            response=field_response.response,
            question=field_question,
            value='Test',
            void_ind='n'
        )
        
        with patch('scouting.util.get_current_event') as mock_event, \
             patch('scouting.util.parse_match') as mock_parse, \
             patch('form.util.get_response_answers') as mock_answers:
            mock_event.return_value = event
            mock_parse.return_value = {'match_number': 1}
            mock_answers.return_value = []
            
            result = field_util.get_scouting_responses()
            
            assert len(result) > 0
            assert result[0]['id'] == field_response.id
            assert 'display_value' in result[0]
    
    def test_get_scouting_responses_limit_10(self, event, team, test_user, form_response):
        """Test response limit of 10"""
        # Create 15 responses
        for i in range(15):
            FieldResponse.objects.create(
                event=event,
                team=team,
                user=test_user,
                response=form_response,
                time=timezone.now(),
                void_ind='n'
            )
        
        with patch('scouting.util.get_current_event') as mock_event, \
             patch('form.util.get_response_answers') as mock_answers:
            mock_event.return_value = event
            mock_answers.return_value = []
            
            result = field_util.get_scouting_responses()
            
            # Should limit to 10
            assert len(result) == 10


# ==================== View Tests ====================


@pytest.mark.django_db
class TestFormView:
    """Tests for FormView"""
    
    def test_form_view_get_success(self, api_rf, admin_user):
        """Test getting field form successfully"""
        request = api_rf.get('/scouting/field/form/')
        force_authenticate(request, user=admin_user)
        
        with patch('general.security.has_access') as mock_access, \
             patch('scouting.field.util.get_field_form') as mock_form:
            mock_access.return_value = True
            mock_form.return_value = {
                'field_form': {'id': 1},
                'form_sub_types': []
            }
            
            response = FormView.as_view()(request)
            
            assert response.status_code == 200
    
    def test_form_view_get_no_access(self, api_rf, test_user):
        """Test getting form without access"""
        request = api_rf.get('/scouting/field/form/')
        force_authenticate(request, user=test_user)
        
        with patch('general.security.has_access') as mock_access:
            mock_access.return_value = False
            
            response = FormView.as_view()(request)
            
            assert response.status_code == 200
            assert 'do not have access' in str(response.data)
    
    def test_form_view_get_exception(self, api_rf, admin_user):
        """Test exception handling in form view"""
        request = api_rf.get('/scouting/field/form/')
        force_authenticate(request, user=admin_user)
        
        with patch('general.security.has_access') as mock_access, \
             patch('scouting.field.util.get_field_form') as mock_form:
            mock_access.return_value = True
            mock_form.side_effect = Exception("Test error")
            
            response = FormView.as_view()(request)
            
            assert response.status_code == 200
            assert 'error occurred' in str(response.data).lower()


@pytest.mark.django_db
class TestResponseColumnsView:
    """Tests for ResponseColumnsView"""
    
    def test_response_columns_view_get_success(self, api_rf, admin_user, season):
        """Test getting response columns successfully"""
        request = api_rf.get('/scouting/field/response-columns/')
        force_authenticate(request, user=admin_user)
        
        with patch('general.security.has_access') as mock_access, \
             patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.field.util.get_table_columns') as mock_cols, \
             patch('scouting.field.util.get_field_question_aggregates') as mock_aggs:
            mock_access.return_value = True
            mock_season.return_value = season
            mock_aggs.return_value = []
            mock_cols.return_value = [
                {'PropertyName': 'team_id', 'ColLabel': 'Team', 'order': '1'}
            ]
            
            response = ResponseColumnsView.as_view()(request)
            
            assert response.status_code == 200
    
    def test_response_columns_view_no_access(self, api_rf, test_user):
        """Test getting columns without access"""
        request = api_rf.get('/scouting/field/response-columns/')
        force_authenticate(request, user=test_user)
        
        with patch('general.security.has_access') as mock_access:
            mock_access.return_value = False
            
            response = ResponseColumnsView.as_view()(request)
            
            assert response.status_code == 200
            assert 'do not have access' in str(response.data)


@pytest.mark.django_db
class TestResponsesView:
    """Tests for ResponsesView"""
    
    def test_responses_view_get_success(self, api_rf, admin_user, event):
        """Test getting responses successfully"""
        request = api_rf.get('/scouting/field/responses/?pg_num=1')
        force_authenticate(request, user=admin_user)
        
        with patch('general.security.has_access') as mock_access, \
             patch('scouting.field.util.get_responses') as mock_resp:
            mock_access.return_value = True
            mock_resp.return_value = {
                'count': 1,
                'previous': None,
                'next': None,
                'scoutAnswers': [],
                'current_season': event.season,
                'current_event': event,
                'removed_responses': []
            }
            
            response = ResponsesView.as_view()(request)
            
            assert response.status_code == 200
    
    def test_responses_view_with_team_filter(self, api_rf, admin_user, event):
        """Test getting responses with team filter"""
        request = api_rf.get('/scouting/field/responses/?team=3492')
        force_authenticate(request, user=admin_user)
        
        with patch('general.security.has_access') as mock_access, \
             patch('scouting.field.util.get_responses') as mock_resp:
            mock_access.return_value = True
            mock_resp.return_value = {
                'count': 1,
                'previous': None,
                'next': None,
                'scoutAnswers': [],
                'current_season': event.season,
                'current_event': event,
                'removed_responses': []
            }
            
            response = ResponsesView.as_view()(request)
            
            assert response.status_code == 200
            # Verify team filter was passed
            mock_resp.assert_called_once()
            args = mock_resp.call_args
            assert args[1]['team'] == '3492'


@pytest.mark.django_db
class TestCheckInView:
    """Tests for CheckInView"""
    
    def test_check_in_view_success(self, api_rf, test_user, match):
        """Test successful scout check-in"""
        sfs = FieldSchedule.objects.create(
            match=match,
            red_one=test_user,
            void_ind='n'
        )
        
        request = api_rf.get(f'/scouting/field/check-in/?scout_field_sch_id={sfs.id}')
        force_authenticate(request, user=test_user)
        
        with patch('general.security.has_access') as mock_access, \
             patch('scouting.util.get_scout_field_schedule') as mock_sfs:
            mock_access.return_value = True
            mock_sfs.return_value = sfs
            
            response = CheckInView.as_view()(request)
            
            assert response.status_code == 200
    
    def test_check_in_view_no_access(self, api_rf, test_user):
        """Test check-in without access"""
        request = api_rf.get('/scouting/field/check-in/')
        force_authenticate(request, user=test_user)
        
        with patch('general.security.has_access') as mock_access:
            mock_access.return_value = False
            
            response = CheckInView.as_view()(request)
            
            assert response.status_code == 200
            assert 'do not have access' in str(response.data)


@pytest.mark.django_db
class TestScoutingResponsesView:
    """Tests for ScoutingResponsesView"""
    
    def test_scouting_responses_view_get_success(self, api_rf, admin_user, field_response):
        """Test getting scouting responses successfully"""
        request = api_rf.get('/scouting/field/scouting-responses/')
        force_authenticate(request, user=admin_user)
        
        with patch('general.security.has_access') as mock_access, \
             patch('scouting.field.util.get_scouting_responses') as mock_resp:
            mock_access.return_value = True
            mock_resp.return_value = [
                {
                    'id': field_response.id,
                    'match': None,
                    'user': field_response.user,
                    'time': field_response.time,
                    'answers': [],
                    'display_value': 'Test'
                }
            ]
            
            response = ScoutingResponsesView.as_view()(request)
            
            assert response.status_code == 200
    
    def test_scouting_responses_view_exception(self, api_rf, admin_user):
        """Test exception handling in scouting responses view"""
        request = api_rf.get('/scouting/field/scouting-responses/')
        force_authenticate(request, user=admin_user)
        
        with patch('general.security.has_access') as mock_access, \
             patch('scouting.field.util.get_scouting_responses') as mock_resp:
            mock_access.return_value = True
            mock_resp.side_effect = Exception("Test error")
            
            response = ScoutingResponsesView.as_view()(request)
            
            assert response.status_code == 200
            assert 'error occurred' in str(response.data).lower()
