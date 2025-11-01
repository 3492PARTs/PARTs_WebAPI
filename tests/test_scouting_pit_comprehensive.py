"""
Comprehensive tests for scouting/pit app

Tests all utility functions and view classes in the scouting pit module.
Coverage targets:
- scouting/pit/util.py: 4 functions (get_responses, save_robot_picture, set_default_team_image, get_team_data)
- scouting/pit/views.py: 4 view classes (SavePictureView, ResponsesView, SetDefaultPitImageView, TeamDataView)
- scouting/pit/serializers.py: 6 serializers
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, force_authenticate
from unittest.mock import patch, MagicMock

from scouting.models import Season, Event, Team, PitResponse, PitImage, PitImageType, EventTeamInfo
from scouting.pit import util as pit_util
from scouting.pit.views import SavePictureView, ResponsesView, SetDefaultPitImageView, TeamDataView
from form.models import FormType, FormSubType, Response as FormResponse, QuestionType, Question, Answer, QuestionCondition, QuestionConditionType

User = get_user_model()


@pytest.fixture
def season(db):
    """Create a test season"""
    return Season.objects.create(
        season=2024,
        current='y'
    )


@pytest.fixture
def event(db, season):
    """Create a test event"""
    return Event.objects.create(
        season=season,
        event_nm='Test Event',
        event_cd='test2024',
        date_st='2024-03-01',
        date_end='2024-03-03',
        current='y',
        void_ind='n',
        competition_page_active='y'
    )


@pytest.fixture
def team(db, event):
    """Create a test team"""
    team_obj = Team.objects.create(
        team_no=3492,
        team_nm='PARTs',
        void_ind='n'
    )
    event.teams.add(team_obj)
    return team_obj


@pytest.fixture
def team2(db, event):
    """Create a second test team"""
    team_obj = Team.objects.create(
        team_no=1234,
        team_nm='Test Team',
        void_ind='n'
    )
    event.teams.add(team_obj)
    return team_obj


@pytest.fixture
def test_user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )


@pytest.fixture
def form_type(db):
    """Create a form type for pit scouting"""
    return FormType.objects.create(
        form_typ='pit',
        form_nm='Pit Scouting'
    )


@pytest.fixture
def form_sub_type(db, form_type):
    """Create a form sub type"""
    return FormSubType.objects.create(
        form_sub_typ='pit',
        form_sub_nm='Pit Scouting',
        form_typ=form_type,
        order=1
    )


@pytest.fixture
def question_type(db):
    """Create a question type"""
    return QuestionType.objects.create(
        question_typ='text',
        question_typ_nm='Text'
    )


@pytest.fixture
def question(db, form_type, form_sub_type, question_type):
    """Create a test question"""
    return Question.objects.create(
        form_typ=form_type,
        question='What is the robot weight?',
        order=1,
        form_sub_typ=form_sub_type,
        question_typ=question_type,
        table_col_width='200',
        required='n',
        void_ind='n'
    )


@pytest.fixture
def form_response(db, form_type):
    """Create a form response"""
    return FormResponse.objects.create(
        form_typ=form_type,
        time='2024-03-01 10:00:00',
        void_ind='n'
    )


@pytest.fixture
def pit_response(db, event, team, test_user, form_response):
    """Create a pit response"""
    return PitResponse.objects.create(
        response=form_response,
        event=event,
        team=team,
        user=test_user,
        void_ind='n'
    )


@pytest.fixture
def pit_image_type(db):
    """Create a pit image type"""
    return PitImageType.objects.create(
        pit_image_typ='robot',
        pit_image_nm='Robot Picture'
    )


@pytest.fixture
def pit_image(db, pit_response, pit_image_type):
    """Create a pit image"""
    return PitImage.objects.create(
        pit_response=pit_response,
        pit_image_typ=pit_image_type,
        img_id='test_img_123',
        img_ver='1',
        img_title='Test Robot',
        default=True,
        void_ind='n'
    )


@pytest.fixture
def api_rf():
    """Create API request factory"""
    return APIRequestFactory()


@pytest.mark.django_db
class TestGetResponses:
    """Tests for get_responses utility function"""
    
    def test_get_responses_returns_all_teams(self, event, team, team2, pit_response, question):
        """Test getting responses for all teams"""
        # Create pit response for team2
        form_response2 = FormResponse.objects.create(
            form_typ=pit_response.response.form_typ,
            time='2024-03-01 11:00:00',
            void_ind='n'
        )
        PitResponse.objects.create(
            response=form_response2,
            event=event,
            team=team2,
            user=pit_response.user,
            void_ind='n'
        )
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = pit_util.get_responses()
            
            assert 'teams' in result
            assert len(result['teams']) == 2
            assert 'current_season' in result
            assert 'current_event' in result
    
    def test_get_responses_filter_by_team(self, event, team, team2, pit_response):
        """Test filtering responses by team number"""
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = pit_util.get_responses(team=team.team_no)
            
            assert len(result['teams']) == 1
            assert result['teams'][0]['team_no'] == team.team_no
    
    def test_get_responses_includes_pit_images(self, event, team, pit_response, pit_image):
        """Test that responses include pit images"""
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event, \
             patch('general.cloudinary.build_image_url') as mock_url:
            mock_season.return_value = event.season
            mock_event.return_value = event
            mock_url.return_value = 'http://example.com/image.jpg'
            
            result = pit_util.get_responses()
            
            assert len(result['teams']) == 1
            assert 'pics' in result['teams'][0]
            assert len(result['teams'][0]['pics']) == 1
            assert result['teams'][0]['pics'][0]['img_title'] == 'Test Robot'
            assert result['teams'][0]['pics'][0]['default'] is True
    
    def test_get_responses_includes_answers(self, event, team, pit_response, question):
        """Test that responses include answers"""
        Answer.objects.create(
            response=pit_response.response,
            question=question,
            value='125 lbs',
            void_ind='n'
        )
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = pit_util.get_responses()
            
            assert 'responses' in result['teams'][0]
            # Should have at least the question we added
            answers = [r for r in result['teams'][0]['responses'] if r['question'] == question.question]
            assert len(answers) == 1
            assert answers[0]['answer'] == '125 lbs'
    
    def test_get_responses_includes_rank_from_event_team_info(self, event, team, pit_response):
        """Test that responses include rank from EventTeamInfo"""
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
            
            result = pit_util.get_responses()
            
            rank_responses = [r for r in result['teams'][0]['responses'] if r['question'] == 'Rank']
            assert len(rank_responses) == 1
            assert rank_responses[0]['answer'] == 5
    
    def test_get_responses_excludes_void_responses(self, event, team, pit_response):
        """Test that void responses are excluded"""
        pit_response.void_ind = 'y'
        pit_response.save()
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = pit_util.get_responses()
            
            assert len(result['teams']) == 0
    
    def test_get_responses_excludes_void_images(self, event, team, pit_response, pit_image):
        """Test that void images are excluded"""
        pit_image.void_ind = 'y'
        pit_image.save()
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = pit_util.get_responses()
            
            assert len(result['teams'][0]['pics']) == 0
    
    def test_get_responses_with_conditional_question(self, event, team, pit_response, question_type, form_type, form_sub_type):
        """Test handling of conditional questions"""
        # Create a conditional question condition type
        condition_type = QuestionConditionType.objects.create(
            question_condition_typ='equals',
            question_condition_nm='Equals',
            void_ind='n'
        )
        
        # Create a conditional question
        parent_question = Question.objects.create(
            form_typ=form_type,
            question='Has autonomous?',
            order=1,
            form_sub_typ=form_sub_type,
            question_typ=question_type,
            table_col_width='200',
            required='n',
            void_ind='n'
        )
        
        conditional_question = Question.objects.create(
            form_typ=form_type,
            question='Describe autonomous',
            order=2,
            form_sub_typ=form_sub_type,
            question_typ=question_type,
            table_col_width='200',
            required='n',
            void_ind='n'
        )
        
        # Create the condition relationship
        QuestionCondition.objects.create(
            question_condition_typ=condition_type,
            value='yes',
            question_from=parent_question,
            question_to=conditional_question,
            active='y',
            void_ind='n'
        )
        
        Answer.objects.create(
            response=pit_response.response,
            question=conditional_question,
            value='Shoots from distance',
            void_ind='n'
        )
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event:
            mock_season.return_value = event.season
            mock_event.return_value = event
            
            result = pit_util.get_responses()
            
            # Find the conditional question in responses
            conditional_responses = [r for r in result['teams'][0]['responses'] 
                                     if 'Describe autonomous' in r['question']]
            assert len(conditional_responses) == 1
            # Should be prefixed with " C: "
            assert conditional_responses[0]['question'].startswith(' C: ')


@pytest.mark.django_db
class TestSaveRobotPicture:
    """Tests for save_robot_picture utility function"""
    
    def test_save_robot_picture_success(self, event, team, pit_response, pit_image_type):
        """Test successfully saving a robot picture"""
        file_obj = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        
        with patch('scouting.util.get_current_event') as mock_event, \
             patch('general.cloudinary.upload_image') as mock_upload:
            mock_event.return_value = event
            mock_upload.return_value = {
                'public_id': 'uploaded_img_456',
                'version': 2
            }
            
            result = pit_util.save_robot_picture(
                file_obj,
                team.team_no,
                pit_image_type.pit_image_typ,
                'New Robot Image'
            )
            
            assert 'Saved pit image successfully' in str(result)
            
            # Verify image was created
            pit_images = PitImage.objects.filter(pit_response=pit_response)
            assert pit_images.count() == 1
            assert pit_images.first().img_id == 'uploaded_img_456'
            assert pit_images.first().img_ver == '2'
            assert pit_images.first().img_title == 'New Robot Image'


@pytest.mark.django_db
class TestSetDefaultTeamImage:
    """Tests for set_default_team_image utility function"""
    
    def test_set_default_team_image(self, pit_response, pit_image_type):
        """Test setting a default team image"""
        # Create multiple images
        img1 = PitImage.objects.create(
            pit_response=pit_response,
            pit_image_typ=pit_image_type,
            img_id='img1',
            img_ver='1',
            default=True,
            void_ind='n'
        )
        img2 = PitImage.objects.create(
            pit_response=pit_response,
            pit_image_typ=pit_image_type,
            img_id='img2',
            img_ver='1',
            default=False,
            void_ind='n'
        )
        
        # Set img2 as default
        result = pit_util.set_default_team_image(img2.id)
        
        assert result.id == img2.id
        assert result.default is True
        
        # Verify img1 is no longer default
        img1.refresh_from_db()
        assert img1.default is False
    
    def test_set_default_only_affects_same_image_type(self, pit_response):
        """Test that setting default only affects images of the same type"""
        type1 = PitImageType.objects.create(pit_image_typ='robot', pit_image_nm='Robot')
        type2 = PitImageType.objects.create(pit_image_typ='mechanism', pit_image_nm='Mechanism')
        
        img1_type1 = PitImage.objects.create(
            pit_response=pit_response,
            pit_image_typ=type1,
            img_id='img1',
            img_ver='1',
            default=True,
            void_ind='n'
        )
        img2_type1 = PitImage.objects.create(
            pit_response=pit_response,
            pit_image_typ=type1,
            img_id='img2',
            img_ver='1',
            default=False,
            void_ind='n'
        )
        img_type2 = PitImage.objects.create(
            pit_response=pit_response,
            pit_image_typ=type2,
            img_id='img3',
            img_ver='1',
            default=True,
            void_ind='n'
        )
        
        # Set img2_type1 as default
        pit_util.set_default_team_image(img2_type1.id)
        
        # img_type2 should still be default for its type
        img_type2.refresh_from_db()
        assert img_type2.default is True


@pytest.mark.django_db
class TestGetTeamData:
    """Tests for get_team_data utility function"""
    
    def test_get_team_data_returns_response_and_questions(self, event, team, pit_response, question):
        """Test getting team data with response and questions"""
        Answer.objects.create(
            response=pit_response.response,
            question=question,
            value='130 lbs',
            void_ind='n'
        )
        
        with patch('scouting.util.get_current_event') as mock_event:
            mock_event.return_value = event
            
            result = pit_util.get_team_data(team_no=team.team_no)
            
            assert 'response_id' in result
            assert result['response_id'] == pit_response.response_id
            assert 'questions' in result
            assert len(result['questions']) >= 1
    
    def test_get_team_data_includes_pictures(self, event, team, pit_response, pit_image):
        """Test that team data includes pictures"""
        with patch('scouting.util.get_current_event') as mock_event, \
             patch('general.cloudinary.build_image_url') as mock_url:
            mock_event.return_value = event
            mock_url.return_value = 'http://example.com/robot.jpg'
            
            result = pit_util.get_team_data(team_no=team.team_no)
            
            assert 'pics' in result
            assert len(result['pics']) == 1
            assert result['pics'][0]['img_title'] == 'Test Robot'
            assert result['pics'][0]['default'] is True


# View Tests

@pytest.mark.django_db
class TestSavePictureView:
    """Tests for SavePictureView"""
    
    def test_save_picture_post(self, api_rf, test_user, event, team, pit_response, pit_image_type):
        """Test POST to save picture"""
        file_obj = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        
        request = api_rf.post('/scouting/pit/save-picture/', {
            'file': file_obj,
            'team_no': team.team_no,
            'pit_image_typ': pit_image_type.pit_image_typ,
            'img_title': 'Test Image'
        }, format='multipart')
        force_authenticate(request, user=test_user)
        
        with patch('scouting.util.get_current_event') as mock_event, \
             patch('general.cloudinary.upload_image') as mock_upload, \
             patch('general.security.has_access') as mock_access:
            mock_event.return_value = event
            mock_upload.return_value = {'public_id': 'test123', 'version': 1}
            mock_access.return_value = True
            
            response = SavePictureView.as_view()(request)
            
            assert response.status_code == 200
    
    def test_save_picture_requires_authentication(self, api_rf):
        """Test that save picture requires authentication"""
        request = api_rf.post('/scouting/pit/save-picture/')
        
        response = SavePictureView.as_view()(request)
        
        assert response.status_code == 401


@pytest.mark.django_db
class TestResponsesView:
    """Tests for ResponsesView"""
    
    def test_responses_view_get(self, api_rf, test_user, event, team, pit_response):
        """Test GET responses"""
        request = api_rf.get('/scouting/pit/responses/')
        force_authenticate(request, user=test_user)
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event, \
             patch('general.security.has_access') as mock_access:
            mock_season.return_value = event.season
            mock_event.return_value = event
            mock_access.return_value = True
            
            response = ResponsesView.as_view()(request)
            
            assert response.status_code == 200
            assert 'teams' in response.data
    
    def test_responses_view_filter_by_team(self, api_rf, test_user, event, team, pit_response):
        """Test GET responses filtered by team"""
        request = api_rf.get('/scouting/pit/responses/', {'team': team.team_no})
        force_authenticate(request, user=test_user)
        
        with patch('scouting.util.get_current_season') as mock_season, \
             patch('scouting.util.get_current_event') as mock_event, \
             patch('general.security.has_access') as mock_access:
            mock_season.return_value = event.season
            mock_event.return_value = event
            mock_access.return_value = True
            
            response = ResponsesView.as_view()(request)
            
            assert response.status_code == 200


@pytest.mark.django_db
class TestSetDefaultPitImageView:
    """Tests for SetDefaultPitImageView"""
    
    def test_set_default_pit_image_get(self, api_rf, test_user, pit_image):
        """Test GET to set default pit image"""
        request = api_rf.get('/scouting/pit/set-default-pit-image/', 
                             {'scout_pit_img_id': pit_image.id})
        force_authenticate(request, user=test_user)
        
        with patch('general.security.has_access') as mock_access:
            mock_access.return_value = True
            
            response = SetDefaultPitImageView.as_view()(request)
            
            assert response.status_code == 200


@pytest.mark.django_db
class TestTeamDataView:
    """Tests for TeamDataView"""
    
    def test_team_data_view_get(self, api_rf, test_user, event, team, pit_response, question):
        """Test GET team data"""
        Answer.objects.create(
            response=pit_response.response,
            question=question,
            value='Test answer',
            void_ind='n'
        )
        
        request = api_rf.get('/scouting/pit/team-data/', {'team_num': team.team_no})
        force_authenticate(request, user=test_user)
        
        with patch('scouting.util.get_current_event') as mock_event, \
             patch('general.security.has_access') as mock_access:
            mock_event.return_value = event
            mock_access.return_value = True
            
            response = TeamDataView.as_view()(request)
            
            assert response.status_code == 200
            assert 'response_id' in response.data
            assert 'questions' in response.data
            assert 'pics' in response.data


# Serializer Tests

@pytest.mark.django_db
class TestPitSerializers:
    """Tests for pit serializers"""
    
    def test_pit_response_answer_serializer(self):
        """Test PitResponseAnswerSerializer"""
        from scouting.pit.serializers import PitResponseAnswerSerializer
        
        data = {'question': 'Robot weight?', 'answer': '125 lbs'}
        serializer = PitResponseAnswerSerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['question'] == 'Robot weight?'
        assert serializer.validated_data['answer'] == '125 lbs'
    
    def test_pit_image_type_serializer(self):
        """Test PitImageTypeSerializer"""
        from scouting.pit.serializers import PitImageTypeSerializer
        
        data = {'pit_image_typ': 'robot', 'pit_image_nm': 'Robot Picture'}
        serializer = PitImageTypeSerializer(data=data)
        
        assert serializer.is_valid()
    
    def test_pit_image_serializer(self):
        """Test PitImageSerializer"""
        from scouting.pit.serializers import PitImageSerializer
        
        data = {
            'id': 1,
            'img_url': 'http://example.com/img.jpg',
            'img_title': 'Test',
            'pit_image_typ': {'pit_image_typ': 'robot', 'pit_image_nm': 'Robot'},
            'default': True
        }
        serializer = PitImageSerializer(data=data)
        
        assert serializer.is_valid()
    
    def test_pit_response_serializer(self):
        """Test PitResponseSerializer"""
        from scouting.pit.serializers import PitResponseSerializer
        
        data = {
            'id': 1,
            'team_no': 3492,
            'team_nm': 'PARTs',
            'pics': [],
            'responses': [{'question': 'Test?', 'answer': 'Yes'}]
        }
        serializer = PitResponseSerializer(data=data)
        
        assert serializer.is_valid()
    
    def test_pit_team_data_serializer(self):
        """Test PitTeamDataSerializer"""
        from scouting.pit.serializers import PitTeamDataSerializer
        
        data = {
            'response_id': 123,
            'questions': [],
            'pics': []
        }
        serializer = PitTeamDataSerializer(data=data)
        
        assert serializer.is_valid()
