"""
Comprehensive tests for form/views.py covering all API endpoints and view classes.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from django.test import RequestFactory


@pytest.mark.django_db
class TestQuestionView:
    """Tests for QuestionView API endpoint."""

    def test_get_questions_success(self, api_rf):
        """Test successful retrieval of questions."""
        from form.views import QuestionView
        
        with patch('form.util.get_questions') as mock_get:
            mock_get.return_value = []
            
            request = api_rf.get('/api/form/question/?form_typ=survey')
            view = QuestionView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            mock_get.assert_called_once()

    def test_get_questions_with_active_filter(self, api_rf):
        """Test retrieval of questions with active filter."""
        from form.views import QuestionView
        
        with patch('form.util.get_questions') as mock_get:
            mock_get.return_value = []
            
            request = api_rf.get('/api/form/question/?form_typ=survey&active=y')
            view = QuestionView.as_view()
            response = view(request)
            
            assert response.status_code == 200

    def test_get_questions_error_handling(self, api_rf):
        """Test error handling in question retrieval."""
        from form.views import QuestionView
        
        with patch('form.util.get_questions') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            request = api_rf.get('/api/form/question/?form_typ=survey')
            view = QuestionView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'error' in response.data

    def test_post_question_unauthorized(self, api_rf):
        """Test posting question without authentication."""
        from form.views import QuestionView
        
        request = api_rf.post('/api/form/question/', {})
        request.user = Mock(id=None)
        view = QuestionView.as_view()
        response = view(request)
        
        assert response.status_code == 401

    def test_post_question_no_access(self, api_rf, test_user):
        """Test posting question without proper permissions."""
        from form.views import QuestionView
        
        with patch('general.security.has_access', return_value=False):
            request = api_rf.post('/api/form/question/', {})
            request.user = test_user
            view = QuestionView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'error' in response.data


@pytest.mark.django_db
class TestFormEditorView:
    """Tests for FormEditorView API endpoint."""

    def test_get_form_editor_no_access(self, api_rf, test_user):
        """Test form editor without proper permissions."""
        from form.views import FormEditorView
        
        with patch('general.security.has_access', return_value=False):
            request = api_rf.get('/api/form/form-editor/?form_typ=survey')
            request.user = test_user
            view = FormEditorView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'error' in response.data

    def test_get_form_editor_success(self, api_rf, admin_user):
        """Test successful form editor initialization."""
        from form.views import FormEditorView
        
        with patch('general.security.has_access', return_value=True), \
             patch('form.util.get_questions', return_value=[]), \
             patch('form.util.get_question_types', return_value=[]), \
             patch('form.util.get_form_sub_types', return_value=[]), \
             patch('form.util.get_flows', return_value=[]):
            
            request = api_rf.get('/api/form/form-editor/?form_typ=survey')
            request.user = admin_user
            view = FormEditorView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'questions' in response.data
            assert 'question_types' in response.data
            assert 'form_sub_types' in response.data
            assert 'flows' in response.data


@pytest.mark.django_db
class TestSaveAnswersView:
    """Tests for SaveAnswersView API endpoint."""

    def test_save_answers_field_unauthorized(self, api_rf):
        """Test saving field answers without authentication."""
        from form.views import SaveAnswersView
        
        request = api_rf.post('/api/form/save-answers/', {
            'form_typ': 'field'
        }, format='json')
        request.user = Mock(id=None)
        view = SaveAnswersView.as_view()
        response = view(request)
        
        assert response.status_code == 401

    def test_save_answers_field_no_access(self, api_rf, test_user):
        """Test saving field answers without proper permissions."""
        from form.views import SaveAnswersView
        
        with patch('general.security.has_access', return_value=False):
            request = api_rf.post('/api/form/save-answers/', {
                'form_typ': 'field'
            }, format='json')
            request.user = test_user
            view = SaveAnswersView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'error' in response.data


@pytest.mark.django_db
class TestResponseView:
    """Tests for ResponseView API endpoint."""

    def test_get_response_no_access(self, api_rf, test_user):
        """Test getting response without admin access."""
        from form.views import ResponseView
        
        with patch('general.security.has_access', return_value=False):
            request = api_rf.get('/api/form/response/?response_id=1')
            request.user = test_user
            view = ResponseView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'error' in response.data

    def test_get_response_success(self, api_rf, admin_user):
        """Test successful response retrieval."""
        from form.views import ResponseView
        
        with patch('general.security.has_access', return_value=True), \
             patch('form.util.get_response', return_value=[]):
            
            request = api_rf.get('/api/form/response/?response_id=1')
            request.user = admin_user
            view = ResponseView.as_view()
            response = view(request)
            
            assert response.status_code == 200

    def test_delete_response_no_access(self, api_rf, test_user):
        """Test deleting response without admin access."""
        from form.views import ResponseView
        
        with patch('general.security.has_access', return_value=False):
            request = api_rf.delete('/api/form/response/?response_id=1')
            request.user = test_user
            view = ResponseView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'error' in response.data

    def test_delete_response_success(self, api_rf, admin_user):
        """Test successful response deletion."""
        from form.views import ResponseView
        
        with patch('general.security.has_access', return_value=True), \
             patch('form.util.delete_response'):
            
            request = api_rf.delete('/api/form/response/?response_id=1')
            request.user = admin_user
            view = ResponseView.as_view()
            response = view(request)
            
            assert response.status_code == 200


@pytest.mark.django_db
class TestResponsesView:
    """Tests for ResponsesView API endpoint."""

    def test_get_responses_no_access(self, api_rf, test_user):
        """Test getting responses without admin access."""
        from form.views import ResponsesView
        
        with patch('general.security.has_access', return_value=False):
            request = api_rf.get('/api/form/responses/?form_typ=survey')
            request.user = test_user
            view = ResponsesView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'error' in response.data

    def test_get_responses_success(self, api_rf, admin_user):
        """Test successful responses retrieval."""
        from form.views import ResponsesView
        
        with patch('general.security.has_access', return_value=True), \
             patch('form.util.get_responses', return_value=[]):
            
            request = api_rf.get('/api/form/responses/?form_typ=survey')
            request.user = admin_user
            view = ResponsesView.as_view()
            response = view(request)
            
            assert response.status_code == 200


@pytest.mark.django_db
class TestQuestionAggregateView:
    """Tests for QuestionAggregateView API endpoint."""

    def test_get_aggregates_no_access(self, api_rf, test_user):
        """Test getting aggregates without proper permissions."""
        from form.views import QuestionAggregateView
        
        with patch('general.security.has_access', return_value=False):
            request = api_rf.get('/api/form/question-aggregate/?form_typ=survey')
            request.user = test_user
            view = QuestionAggregateView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'error' in response.data

    def test_get_aggregates_success(self, api_rf, admin_user):
        """Test successful aggregates retrieval."""
        from form.views import QuestionAggregateView
        
        with patch('general.security.has_access', return_value=True), \
             patch('form.util.get_question_aggregates', return_value=[]):
            
            request = api_rf.get('/api/form/question-aggregate/?form_typ=survey')
            request.user = admin_user
            view = QuestionAggregateView.as_view()
            response = view(request)
            
            assert response.status_code == 200


@pytest.mark.django_db
class TestQuestionAggregateTypeView:
    """Tests for QuestionAggregateTypeView API endpoint."""

    def test_get_aggregate_types_success(self, api_rf, test_user):
        """Test successful aggregate types retrieval."""
        from form.views import QuestionAggregateTypeView
        
        with patch('form.util.get_question_aggregate_types', return_value=[]):
            request = api_rf.get('/api/form/question-aggregate-types/')
            request.user = test_user
            view = QuestionAggregateTypeView.as_view()
            response = view(request)
            
            assert response.status_code == 200


@pytest.mark.django_db
class TestQuestionConditionView:
    """Tests for QuestionConditionView API endpoint."""

    def test_get_conditions_no_access(self, api_rf, test_user):
        """Test getting conditions without proper permissions."""
        from form.views import QuestionConditionView
        
        with patch('general.security.has_access', return_value=False):
            request = api_rf.get('/api/form/question-condition/?form_typ=survey')
            request.user = test_user
            view = QuestionConditionView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'error' in response.data

    def test_get_conditions_success(self, api_rf, admin_user):
        """Test successful conditions retrieval."""
        from form.views import QuestionConditionView
        
        with patch('general.security.has_access', return_value=True), \
             patch('form.util.get_question_conditions', return_value=[]):
            
            request = api_rf.get('/api/form/question-condition/?form_typ=survey')
            request.user = admin_user
            view = QuestionConditionView.as_view()
            response = view(request)
            
            assert response.status_code == 200


@pytest.mark.django_db
class TestFlowView:
    """Tests for FlowView API endpoint."""

    def test_get_flows_success(self, api_rf, test_user):
        """Test successful flows retrieval."""
        from form.views import FlowView
        
        with patch('form.util.get_flows', return_value=[]):
            request = api_rf.get('/api/form/flow/')
            request.user = test_user
            view = FlowView.as_view()
            response = view(request)
            
            assert response.status_code == 200

    def test_get_flow_by_id(self, api_rf, test_user):
        """Test getting specific flow by ID."""
        from form.views import FlowView
        
        mock_flow = Mock()
        with patch('form.util.get_flows', return_value=[mock_flow]):
            request = api_rf.get('/api/form/flow/?id=1')
            request.user = test_user
            view = FlowView.as_view()
            response = view(request)
            
            assert response.status_code == 200


@pytest.mark.django_db
class TestGraphEditorView:
    """Tests for GraphEditorView API endpoint."""

    def test_get_graph_editor_success(self, api_rf, test_user):
        """Test successful graph editor initialization."""
        from form.views import GraphEditorView
        
        with patch('form.util.get_graph_types', return_value=[]), \
             patch('form.util.get_graph_question_types', return_value=[]), \
             patch('form.util.get_graphs', return_value=[]), \
             patch('form.util.get_question_condition_types', return_value=[]):
            
            request = api_rf.get('/api/form/graph-editor/')
            request.user = test_user
            view = GraphEditorView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'graph_types' in response.data
            assert 'graph_question_types' in response.data
            assert 'graphs' in response.data


@pytest.mark.django_db
class TestGraphView:
    """Tests for GraphView API endpoint."""

    def test_get_graphs_success(self, api_rf, test_user):
        """Test successful graphs retrieval."""
        from form.views import GraphView
        
        with patch('form.util.get_graphs', return_value=[]):
            request = api_rf.get('/api/form/graph/')
            request.user = test_user
            view = GraphView.as_view()
            response = view(request)
            
            assert response.status_code == 200

    def test_get_graph_by_id(self, api_rf, test_user):
        """Test getting specific graph by ID."""
        from form.views import GraphView
        
        mock_graph = Mock()
        with patch('form.util.get_graphs', return_value=[mock_graph]):
            request = api_rf.get('/api/form/graph/?graph_id=1')
            request.user = test_user
            view = GraphView.as_view()
            response = view(request)
            
            assert response.status_code == 200


@pytest.mark.django_db
class TestFlowConditionView:
    """Tests for FlowConditionView API endpoint."""

    def test_get_flow_conditions_no_access(self, api_rf, test_user):
        """Test getting flow conditions without proper permissions."""
        from form.views import FlowConditionView
        
        with patch('general.security.has_access', return_value=False):
            request = api_rf.get('/api/form/flow-condition/?form_typ=survey')
            request.user = test_user
            view = FlowConditionView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'error' in response.data

    def test_get_flow_conditions_success(self, api_rf, admin_user):
        """Test successful flow conditions retrieval."""
        from form.views import FlowConditionView
        
        with patch('general.security.has_access', return_value=True), \
             patch('form.util.get_flow_condition', return_value=[]):
            
            request = api_rf.get('/api/form/flow-condition/?form_typ=survey')
            request.user = admin_user
            view = FlowConditionView.as_view()
            response = view(request)
            
            assert response.status_code == 200


@pytest.mark.django_db
class TestQuestionConditionTypesView:
    """Tests for QuestionConditionTypesView API endpoint."""

    def test_get_condition_types_no_access(self, api_rf, test_user):
        """Test getting condition types without proper permissions."""
        from form.views import QuestionConditionTypesView
        
        with patch('general.security.has_access', return_value=False):
            request = api_rf.get('/api/form/question-condition-types/')
            request.user = test_user
            view = QuestionConditionTypesView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'error' in response.data

    def test_get_condition_types_success(self, api_rf, admin_user):
        """Test successful condition types retrieval."""
        from form.views import QuestionConditionTypesView
        
        with patch('general.security.has_access', return_value=True), \
             patch('form.util.get_question_condition_types', return_value=[]):
            
            request = api_rf.get('/api/form/question-condition-types/')
            request.user = admin_user
            view = QuestionConditionTypesView.as_view()
            response = view(request)
            
            assert response.status_code == 200

