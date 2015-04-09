from django import template
from django.utils import timezone
from django.utils.formats import date_format
import pytz
from django.template import defaultfilters
from six import text_type

register = template.Library()

# css color classes for top 3 ranks
RANK_CLASS = {1: 'medal-gold', 2: 'medal-silver', 3: 'medal-bronze'}
RANK_NAME = {1: 'Gold', 2: 'Silver', 3: 'Bronze'}


@register.assignment_tag
def get_timezones():
    return {'timezones': pytz.common_timezones}


@register.simple_tag
def get_time():
    """ Returns the local time for the user

    Makes use of the user's preferred timezone if set.
    """
    return date_format(timezone.localtime(timezone.now()), 'DATE_FORMAT',
                       use_l10n=False)


@register.simple_tag
def version_string(shortname):
    if shortname == 'new':
        return "Current version"
    if shortname == 'old':
        return "Old version (1.0)"
    return "Undefined"


@register.simple_tag
def rank_to_class(rank):
    return RANK_CLASS.get(rank, '')


@register.simple_tag
def rank_to_name(rank):
    return RANK_NAME.get(rank, '')


@register.simple_tag
def time_passed_since(date):
    """ Returns how 'long ago' a certain event happened

    Currently used to print how long ago a player made a new record on a map.
    """
    delta = timezone.now() - date
    if delta.days:
        if delta.days > 30:
            months = float(delta.days) / 30.0
            units = "month" if months < 2.0 else "months"
            return "{} {} ago".format(int(months), units)
        elif delta.days > 7:
            weeks = float(delta.days) / 7.0
            units = "week" if weeks < 2.0 else "weeks"
            return "{} {} ago".format(int(weeks), units)
        else:
            units = "day" if delta.days == 1 else "days"
            return "{} {} ago".format(delta.days, units)

    hours = float(delta.seconds) / 3600.0
    if hours >= 1.0:
        units = "hour" if hours < 2.0 else "hours"
        return "{} {} ago".format(int(hours), units)
    minutes = float(delta.seconds) / 60.0
    if minutes >= 1.0:
        units = "minute" if minutes < 2.0 else "minutes"
        return "{} {} ago".format(int(minutes), units)
    seconds = max(1, delta.seconds)
    units = "second" if seconds == 1 else "seconds"
    return "{} {} ago".format(seconds, units)


@register.assignment_tag
def format_header(column, order):
    """ Decides how the column's header should be formatted, and what "order"
    it's href should have.

    :param column: the table header to determine the current title and url for
    :param order: the active table ordering
    :returns: a dictionary with the header title and url
    """
    result = {'title': None, 'url': None}

    col_l = column.lower().replace(' ', '')
    if "-" + col_l == order:
        # if col_l is "points" and order is "-points", the column title should
        # be "Points-"
        result['title'] = column.capitalize() + \
            " <i class='fa fa-chevron-down'></i>"
        # don't escape the html
        result['title'] = defaultfilters.safe(result['title'])
        # if col_l is "points" and order is "-points", clicking Points url
        # should order results with "points"
        result['url'] = col_l
    else:
        # if col_l is "points" and current sort is "points", clicking Points
        # url should order results with "-points" or, if col_l is "points" and
        # order is "skill", clicking Points url should default order results
        # with "-points"
        result['url'] = "-" + col_l
        if col_l == order:
            # if col_l is "points" and current sort is "points", the column
            # title should be "Points+"
            result['title'] = column.capitalize() + \
                " <i class='fa fa-chevron-up'></i>"
            # don't escape the html
            result['title'] = defaultfilters.safe(result['title'])
        else:
            # if col_l is "points" and current sort is "skill", the column
            # title should be "Points"
            result['title'] = column.capitalize()
    return result


@register.tag
def active(parser, token):
    """
    Color the navigation button if it's page is active
    """
    args = token.split_contents()
    template_tag = args[0]
    if len(args) < 2:
        raise template.TemplateSyntaxError(
            "%r tag requires at least one argument" % template_tag)
    return NavSelectedNode(args[1:])


class NavSelectedNode(template.Node):
    def __init__(self, patterns):
        self.patterns = patterns

    def render(self, context):
        path = context['request'].path
        for p in self.patterns:
            p_value = template.Variable(p).resolve(context)
            if path == p_value:
                return "active"
        return ""


@register.tag
def active_subpage(parser, token):
    """
    Color the navigation button if it's page or a subpage is active
    """
    args = token.split_contents()
    template_tag = args[0]
    if len(args) < 2:
        raise template.TemplateSyntaxError(
            "%r tag requires at least one argument" % template_tag)
    return NavSelectedSubNode(args[1:])


class NavSelectedSubNode(template.Node):
    def __init__(self, patterns):
        self.patterns = patterns

    def render(self, context):
        path = text_type(context['request'].path)
        for p in self.patterns:
            try:
                p_value = text_type(template.Variable(p).resolve(context))
            except UnicodeDecodeError:
                continue
            if path.startswith(p_value):
                return "active"
        return ""
