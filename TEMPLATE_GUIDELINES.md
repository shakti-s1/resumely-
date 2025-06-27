# Django Template Guidelines

## Best Practices to Avoid Template Syntax Errors

### 1. Avoid Multi-line If Conditions
❌ Don't do this:
```django
{% if 'missing' in ats|lower or 'issue' in ats|lower or 'error' in ats|lower
or 'problem' in ats|lower %}
```

✅ Do this instead:
```django
{% if ats|has_issues %}
```

### 2. Use Custom Filters for Complex Logic
Create custom filters in `resumes/templatetags/custom_filters.py`:

```python
@register.filter
def has_issues(text):
    if not text:
        return False
    text_lower = text.lower()
    issue_keywords = ['missing', 'issue', 'error', 'problem', 'warning']
    return any(keyword in text_lower for keyword in issue_keywords)
```

### 3. Proper For Loop Structure
❌ Don't use else in for loops:
```django
{% for item in items %}
    {{ item }}
{% else %}
    No items
{% endfor %}
```

✅ Use empty instead:
```django
{% for item in items %}
    {{ item }}
{% empty %}
    No items
{% endfor %}
```

### 4. Consistent Tag Spacing
✅ Good:
```django
{% if condition %}
    content
{% endif %}
```

❌ Bad:
```django
{%if condition%}
    content
{%endif%}
```

### 5. Always Close Tags
Make sure every opening tag has a corresponding closing tag:
- `{% if %}` → `{% endif %}`
- `{% for %}` → `{% endfor %}`
- `{% with %}` → `{% endwith %}`
- `{% block %}` → `{% endblock %}`

### 6. Use Safe Boolean Checks
Use the `safe_boolean` filter for reliable boolean checks:
```django
{% if value|safe_boolean %}
    content
{% endif %}
```

## Running Validation
Run this script to validate all templates:
```bash
python validate_templates.py
```
