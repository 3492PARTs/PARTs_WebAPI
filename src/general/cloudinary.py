from typing import Any
from cloudinary import uploader, CloudinaryImage


def upload_image(file: Any, img_id: int | None = None) -> dict[str, Any]:
    """
    Upload an image file to Cloudinary.
    
    Args:
        file: The file object to upload (must have content_type attribute)
        img_id: Optional existing image ID to update. If None, creates a new image
        
    Returns:
        Dictionary containing Cloudinary response with public_id and version
        
    Raises:
        Exception: If the file type is not an allowed image format
    """
    if not allowed_file(file.content_type):
        raise Exception("Invalid file type.")

    response = uploader.upload(file, public_id=img_id)
    """
    img_id=response["public_id"],
    img_ver=str(response["version"]),
    """

    return response


def build_image_url(img_id: str | None, img_ver: str | None) -> str | None:
    """
    Build a secure URL for a Cloudinary image.
    
    Args:
        img_id: The public ID of the image in Cloudinary
        img_ver: The version of the image
        
    Returns:
        Secure HTTPS URL for the image, or None if img_id is None
    """
    url = CloudinaryImage(img_id, version=img_ver).build_url(secure=True)
    return url


def allowed_file(filename: str) -> bool:
    """
    Check if a filename's extension indicates it is an allowed image type.
    
    Args:
        filename: The filename or content type to check (e.g., 'image/png')
        
    Returns:
        True if the file extension is in the allowed list (png, jpg, jpeg, gif), False otherwise
    """
    return filename.rsplit("/", 1)[1].lower() in {"png", "jpg", "jpeg", "gif"}
