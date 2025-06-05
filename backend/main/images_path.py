# Created by ahmadibrahim on 25/04/2025 - 7:40 PM
from django.utils.text import slugify

def user_image_path(instance, filename):
    return f'user/image/{slugify(instance)}.jpg'

def country_image_path(instance, filename):
    return f'country/image/{slugify(instance)}.jpg'
