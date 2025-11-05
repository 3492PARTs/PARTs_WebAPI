"""
Comprehensive tests for TBA model methods to increase coverage.
"""
import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestTBAModelStringMethods:
    """Test __str__ methods for tba app models."""
    
    def test_message_str_method(self):
        """Test Message __str__ method."""
        from tba.models import Message
        
        message = Message.objects.create(
            message_type="event_update",
            message_data='{"event": "test", "data": "value"}'
        )
        
        str_result = str(message)
        assert str(message.message_id) in str_result
        assert "event_update" in str_result
        assert "data" in str_result or "value" in str_result
    
    def test_message_str_with_null_fields(self):
        """Test Message __str__ method with null fields."""
        from tba.models import Message
        
        message = Message.objects.create()
        
        str_result = str(message)
        # Should still work even with null message_type and message_data
        assert str(message.message_id) in str_result


@pytest.mark.django_db
class TestTBAModelFields:
    """Test TBA model field behaviors."""
    
    def test_message_default_values(self):
        """Test Message default values."""
        from tba.models import Message
        
        message = Message.objects.create(
            message_type="test",
            message_data="test data"
        )
        
        assert message.processed == "n"
        assert message.void_ind == "n"
        assert message.time is not None
    
    def test_message_time_auto_set(self):
        """Test Message time is automatically set."""
        from tba.models import Message
        
        before = timezone.now()
        message = Message.objects.create(
            message_type="time_test",
            message_data="testing time"
        )
        after = timezone.now()
        
        assert message.time is not None
        assert before <= message.time <= after
    
    def test_message_processed_flag(self):
        """Test Message processed flag can be updated."""
        from tba.models import Message
        
        message = Message.objects.create(
            message_type="process_test",
            message_data="testing processing"
        )
        
        assert message.processed == "n"
        
        message.processed = "y"
        message.save()
        
        message.refresh_from_db()
        assert message.processed == "y"
    
    def test_message_void_flag(self):
        """Test Message void_ind flag can be updated."""
        from tba.models import Message
        
        message = Message.objects.create(
            message_type="void_test",
            message_data="testing void"
        )
        
        assert message.void_ind == "n"
        
        message.void_ind = "y"
        message.save()
        
        message.refresh_from_db()
        assert message.void_ind == "y"
    
    def test_message_blank_fields(self):
        """Test Message accepts blank message_type and message_data."""
        from tba.models import Message
        
        message = Message.objects.create(
            message_type="",
            message_data=""
        )
        
        assert message.message_type == ""
        assert message.message_data == ""
        assert message.message_id is not None
    
    def test_message_long_data(self):
        """Test Message can store long data (up to 4000 chars)."""
        from tba.models import Message
        
        long_data = "x" * 3000  # 3000 characters
        message = Message.objects.create(
            message_type="long_test",
            message_data=long_data
        )
        
        assert len(message.message_data) == 3000
        assert message.message_data == long_data
