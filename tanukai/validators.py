from rest_framework.exceptions import ValidationError


def validate_max_image_size(image):
    file_size = image.size
    max_size = 5242880  # 5 MB
    if file_size > max_size:
        raise ValidationError("Exhausted the maximum file size limit.")
