from django import template
import calendar

register = template.Library()

@register.filter
def month_name(value):
    """Return the full month name for a given month number."""
    return calendar.month_name[value] if 1 <= value <= 12 else ''


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()