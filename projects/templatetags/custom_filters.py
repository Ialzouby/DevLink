from django import template

register = template.Library()

@register.filter
def star_range(value):
    """Returns a range of numbers for looping in templates"""
    return range(value)

@register.filter
def split(value, delimiter=','):
    """Splits the string by the given delimiter."""
    return value.split(delimiter)

@register.filter
def get_item(dictionary, key):
    """Safely get an item from a dictionary in Django templates."""
    return dictionary.get(key, 0)