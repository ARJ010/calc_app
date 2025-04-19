from django import template
import calendar

register = template.Library()

@register.filter
def month_name(value):
    """Return the full month name for a given month number."""
    return calendar.month_name[value] if 1 <= value <= 12 else ''
