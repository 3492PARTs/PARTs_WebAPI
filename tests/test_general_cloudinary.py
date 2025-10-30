"""
Tests for general.cloudinary module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from general.cloudinary import upload_image, build_image_url, allowed_file


class TestAllowedFile:
    """Tests for allowed_file function."""

    def test_allowed_file_png(self):
        """Test allowed_file with PNG."""
        assert allowed_file("image/png") is True

    def test_allowed_file_jpg(self):
        """Test allowed_file with JPG."""
        assert allowed_file("image/jpg") is True

    def test_allowed_file_jpeg(self):
        """Test allowed_file with JPEG."""
        assert allowed_file("image/jpeg") is True

    def test_allowed_file_gif(self):
        """Test allowed_file with GIF."""
        assert allowed_file("image/gif") is True

    def test_allowed_file_uppercase(self):
        """Test allowed_file with uppercase extension."""
        assert allowed_file("image/PNG") is True

    def test_allowed_file_invalid(self):
        """Test allowed_file with invalid type."""
        assert allowed_file("application/pdf") is False
        assert allowed_file("text/plain") is False


class TestUploadImage:
    """Tests for upload_image function."""

    def test_upload_image_success(self):
        """Test successful image upload."""
        mock_file = MagicMock()
        mock_file.content_type = "image/png"
        
        with patch("cloudinary.uploader.upload") as mock_upload:
            mock_upload.return_value = {
                "public_id": "test_id",
                "version": "12345"
            }
            
            result = upload_image(mock_file)
            
            assert result["public_id"] == "test_id"
            assert result["version"] == "12345"
            mock_upload.assert_called_once_with(mock_file, public_id=None)

    def test_upload_image_with_id(self):
        """Test image upload with existing ID."""
        mock_file = MagicMock()
        mock_file.content_type = "image/jpeg"
        
        with patch("cloudinary.uploader.upload") as mock_upload:
            mock_upload.return_value = {
                "public_id": "existing_id",
                "version": "67890"
            }
            
            result = upload_image(mock_file, img_id="existing_id")
            
            assert result["public_id"] == "existing_id"
            mock_upload.assert_called_once_with(mock_file, public_id="existing_id")

    def test_upload_image_invalid_type(self):
        """Test upload_image with invalid file type."""
        mock_file = MagicMock()
        mock_file.content_type = "application/pdf"
        
        with pytest.raises(Exception, match="Invalid file type"):
            upload_image(mock_file)


class TestBuildImageUrl:
    """Tests for build_image_url function."""

    def test_build_image_url(self):
        """Test building image URL."""
        with patch("cloudinary.CloudinaryImage") as MockCloudinaryImage:
            mock_instance = MagicMock()
            mock_instance.build_url.return_value = "https://res.cloudinary.com/test/image.jpg"
            MockCloudinaryImage.return_value = mock_instance
            
            result = build_image_url("test_id", "12345")
            
            assert result == "https://res.cloudinary.com/test/image.jpg"
            MockCloudinaryImage.assert_called_once_with("test_id", version="12345")
            mock_instance.build_url.assert_called_once_with(secure=True)
