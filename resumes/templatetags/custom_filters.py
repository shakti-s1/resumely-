from django import template
from django.forms import BoundField

register = template.Library()


@register.filter
def replace_underscores(value):
    """Replace underscores with spaces in a string."""
    return value.replace('_', ' ')


@register.filter
def addclass(field, css_class):
    """Add a CSS class to a form field."""
    if isinstance(field, BoundField):
        return field.as_widget(attrs={'class': css_class})
    return field
