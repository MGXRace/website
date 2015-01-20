from django import template

register = template.Library()


@register.simple_tag
def version_string(shortname):
    if shortname == 'new':
        return "Current version"
    if shortname == 'old':
        return "Old version (1.0)"
    return "Undefined"


@register.assignment_tag
def format_header(column, order):
    """
    Decides how the column's header should be formatted, and what "order" it's href should have.

    :param column: the table header to determine the current title and url for
    :param order: the active table ordering
    :returns: a dictionary with the header title and url
    """
    result = {'title': None, 'url': None}

    col_l = column.lower().replace(' ', '')
    if "-" + col_l == order:
        # if col_l is "points" and order is "-points", the column title should be "Points-"
        result['title'] = column.capitalize() + "-"
        # if col_l is "points" and order is "-points", clicking Points url should order results with "points"
        result['url'] = col_l
    else:
        # if col_l is "points" and current sort is "points", clicking Points url should order results with "-points"
        # or, if col_l is "points" and order is "skill", clicking Points url should default order results with "-points"
        result['url'] = "-" + col_l
        if col_l == order:
            # if col_l is "points" and current sort is "points", the column title should be "Points+"
            result['title'] = column.capitalize() + "+"
        else:
            # if col_l is "points" and current sort is "skill", the column title should be "Points"
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
        raise template.TemplateSyntaxError, "%r tag requires at least one argument" % template_tag
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
        raise template.TemplateSyntaxError, "%r tag requires at least one argument" % template_tag
    return NavSelectedSubNode(args[1:])


class NavSelectedSubNode(template.Node):
    def __init__(self, patterns):
        self.patterns = patterns

    def render(self, context):
        path = unicode(context['request'].path)
        for p in self.patterns:
            try:
                p_value = unicode(template.Variable(p).resolve(context))
            except UnicodeDecodeError:
                continue
            if path.startswith(p_value):
                return "active"
        return ""