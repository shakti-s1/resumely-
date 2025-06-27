from django import template
from django.forms import BoundField
from django.template.defaultfilters import stringfilter
import json

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


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def has_issues(text):
    """Check if text contains issue keywords"""
    if not text:
        return False
    text_lower = text.lower()
    issue_keywords = ['missing', 'issue', 'error', 'problem', 'warning']
    return any(keyword in text_lower for keyword in issue_keywords)


@register.filter
def is_ats_compatible(text):
    """Check if text is ATS compatible"""
    if not text:
        return True
    text_lower = text.lower()
    ats_issues = ['missing', 'issue', 'error', 'problem']
    return not any(issue in text_lower for issue in ats_issues)


@register.filter
def format_feedback(feedback):
    """Format feedback for display"""
    if not feedback:
        return []
    if isinstance(feedback, dict):
        return [feedback]
    return feedback


@register.filter
def safe_boolean(value):
    """Safely convert value to boolean"""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip() != ''
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return bool(value)


@register.filter
def section_icon(section):
    """Get appropriate icon for section"""
    icons = {
        'summary': 'file-text',
        'work_experience': 'briefcase',
        'education': 'mortarboard',
        'skills': 'tools',
        'projects': 'folder',
        'contact': 'person',
        'objective': 'target'
    }
    return icons.get(section.lower(), 'file-text')
