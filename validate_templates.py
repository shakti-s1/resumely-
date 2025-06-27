#!/usr/bin/env python3
"""
Django Template Validation Script
This script validates Django templates for common syntax issues that cause problems.
"""

import os
import re
import sys
from pathlib import Path


def check_template_syntax(file_path):
    """Check a single template file for syntax issues"""
    issues = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return [f"Error reading file: {e}"]

    # Check for multi-line if conditions
    for i, line in enumerate(lines, 1):
        # Check for if statements that span multiple lines
        if '{% if' in line and (' or ' in line or ' and ' in line):
            # Look for continuation on next lines
            next_line_idx = i
            while next_line_idx < len(lines):
                next_line = lines[next_line_idx]
                if '{% endif %}' in next_line:
                    break
                if ' or ' in next_line or ' and ' in next_line:
                    issues.append(
                        f"Line {i}: Multi-line if condition detected. Consider using custom filters instead.")
                    break
                next_line_idx += 1

    # Check for else tags inside for loops
    for i, line in enumerate(lines, 1):
        if '{% else %}' in line:
            # Check if this else belongs to a for loop
            for_loop_found = False
            if_found = False

            # Look backwards to find the most recent for or if
            for j in range(i-2, -1, -1):
                if j < 0:
                    break
                prev_line = lines[j]
                if '{% for ' in prev_line:
                    for_loop_found = True
                    break
                elif '{% if ' in prev_line:
                    if_found = True
                    break
                elif '{% endif %}' in prev_line:
                    break
                elif '{% endfor %}' in prev_line:
                    break

            if for_loop_found and not if_found:
                issues.append(
                    f"Line {i}: 'else' tag found inside for loop. Use 'empty' instead.")

    # Check for unclosed template tags
    open_tags = []
    for i, line in enumerate(lines, 1):
        # Find opening tags
        for match in re.finditer(r'{%\s*(\w+)\s+', line):
            tag = match.group(1)
            if tag in ['if', 'for', 'with', 'block']:
                open_tags.append((tag, i))

        # Find closing tags
        for match in re.finditer(r'{%\s*end(\w+)\s*%}', line):
            closing_tag = match.group(1)
            if closing_tag in ['if', 'for', 'with', 'block']:
                if open_tags and open_tags[-1][0] == closing_tag:
                    open_tags.pop()
                else:
                    issues.append(
                        f"Line {i}: Mismatched closing tag 'end{closing_tag}'")

    # Check for remaining unclosed tags
    for tag, line_num in open_tags:
        issues.append(f"Line {line_num}: Unclosed '{tag}' tag")

    # Check for proper spacing in template tags
    for i, line in enumerate(lines, 1):
        if '{%' in line and '%}' in line:
            # Check for proper spacing around template tags
            if re.search(r'{%\s*\w+[^%]*%}', line):
                # This is fine
                pass
            else:
                issues.append(f"Line {i}: Improper spacing in template tag")

    return issues


def validate_all_templates():
    """Validate all template files in the project"""
    template_dirs = [
        'resumes/templates',
        'templates'
    ]

    all_issues = {}
    total_files = 0
    files_with_issues = 0

    for template_dir in template_dirs:
        if not os.path.exists(template_dir):
            continue

        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    total_files += 1

                    issues = check_template_syntax(file_path)
                    if issues:
                        all_issues[file_path] = issues
                        files_with_issues += 1

    # Print results
    print(f"Template Validation Results:")
    print(f"Total files checked: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Files without issues: {total_files - files_with_issues}")
    print()

    if all_issues:
        print("Issues found:")
        print("=" * 50)
        for file_path, issues in all_issues.items():
            print(f"\n{file_path}:")
            for issue in issues:
                print(f"  - {issue}")
        return False
    else:
        print("✅ All templates are valid!")
        return True


def create_template_guidelines():
    """Create a template guidelines file"""
    guidelines = """# Django Template Guidelines

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
"""

    with open('TEMPLATE_GUIDELINES.md', 'w', encoding='utf-8') as f:
        f.write(guidelines)

    print("✅ Template guidelines created: TEMPLATE_GUIDELINES.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-guidelines":
        create_template_guidelines()
    else:
        success = validate_all_templates()
        if not success:
            sys.exit(1)
