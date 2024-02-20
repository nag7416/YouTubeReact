from django import template
from django.utils.timesince import timesince
from django.utils.timezone import now
from datetime import timedelta



register = template.Library()

@register.filter(name='format_views_as_K')
def format_views_as_K(value):
    if value >= 10 ** 9:  # 1 Billion and above
        return f'{value / 10 ** 9:.1f}B'
    elif value >= 10 ** 6:  # 1 Million and above
        return f'{value / 10 ** 6:.1f}M'
    elif value >= 10 ** 3:  # 1 Thousand and above
        return f'{value / 10 ** 3:.1f}K'
    else:
        return str(value)
    

@register.filter(name='format_views_as_comma')
def format_views_as_comma(value):
    return "{:,}".format(value)





@register.filter(name='time_ago')
def time_ago(value):
    if not value:
        return ""

    now_utc = now()
    time_difference = now_utc - value

    if time_difference.days > 365:
        return f'{time_difference.days // 365} years ago'
    elif time_difference.days > 30:
        return f'{time_difference.days // 30} months ago'
    elif time_difference.days > 7:
        return f'{time_difference.days // 7} weeks ago'
    elif time_difference.days > 1:
        return f'{time_difference.days} days ago'
    elif time_difference.seconds > 3600:
        return f'{time_difference.seconds // 3600} hours ago'
    elif time_difference.seconds > 60:
        return f'{time_difference.seconds // 60} minutes ago'
    else:
        return f'{time_difference.seconds} seconds ago'
    

@register.filter(name='format_subscribers')
def format_subscribers(subscribers_queryset):
    # Count the number of subscribers
    subscribers_count = subscribers_queryset.count()

    if subscribers_count >= 1_000_000_000:
        return f'{subscribers_count // 1_000_000_000}B'
    elif subscribers_count >= 100_000_000:
        return f'{subscribers_count // 100_000_000}00M'
    elif subscribers_count >= 10_000_000:
        return f'{subscribers_count // 10_000_000}0M'
    elif subscribers_count >= 1_000_000:
        return f'{subscribers_count // 1_000_000}M'
    elif subscribers_count >= 100_000:
        return f'{subscribers_count // 100_000}00K'
    elif subscribers_count >= 10_000:
        return f'{subscribers_count // 10_000}0K'
    elif subscribers_count >= 1_000:
        return f'{subscribers_count // 1_000}K'
    else:
        return subscribers_count