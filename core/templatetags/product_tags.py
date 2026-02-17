from django import template

register = template.Library()

@register.filter
def get_image_url(image_field):
    if image_field and hasattr(image_field, 'url'):
        return image_field.url
    return "https://via.placeholder.com/600x400?text=Image+non+disponible"