import cloudinary

def upload_image(file):
    """Returns whether a file id and version id for an uploaded file.
    :param file file: A file.
    :return: the uploaded file public id and version id
    :rtype: object"""
    if not allowed_file(file.content_type):
        raise Exception("Invalid file type.")

    cloudinary.uploader.upload(file)

    response = cloudinary.uploader.upload(file)
    """
    img_id=response["public_id"],
    img_ver=str(response["version"]),
    """

    return response


def build_image_url(img_id, img_ver):
    url = cloudinary.CloudinaryImage(img_id, version=img_ver).build_url(secure=True)
    return url


def allowed_file(filename):
    """Returns whether a filename's extension indicates that it is an image.
    :param str filename: A filename.
    :return: Whether the filename has an recognized image file extension
    :rtype: bool"""
    return filename.rsplit("/", 1)[1].lower() in {"png", "jpg", "jpeg", "gif"}