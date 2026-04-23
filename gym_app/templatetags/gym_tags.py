from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    """Return the value of a dict key."""
    try:
        return d.get(key)
    except AttributeError:
        return None
