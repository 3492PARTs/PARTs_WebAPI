"""
Extra coverage for general/cloudinary.py line 47.
build_image_url(None, ...) → returns None.
"""
from general.cloudinary import build_image_url


class TestBuildImageUrlNoneId:
    """Line 47: build_image_url returns None when img_id is None."""

    def test_build_image_url_none_returns_none(self):
        result = build_image_url(None, "12345")
        assert result is None

    def test_build_image_url_none_ver_none_id(self):
        result = build_image_url(None, None)
        assert result is None
