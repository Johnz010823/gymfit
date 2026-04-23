# yourapp/templatetags/workout_extras.py
#
# Add this file to: yourapp/templatetags/workout_extras.py
# Make sure yourapp/templatetags/__init__.py exists (can be empty).
#
# Usage in templates:  {{ my_dict|get_item:key }}

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Return dictionary[key], or None if the key is missing."""
    if dictionary is None:
        return None
    return dictionary.get(key)