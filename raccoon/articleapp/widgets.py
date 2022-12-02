from django.forms import ClearableFileInput as BaseClearableFileInput


class ClearableFileInput(BaseClearableFileInput):
    template_name = "articleapp/widgets/profile_image.html"
