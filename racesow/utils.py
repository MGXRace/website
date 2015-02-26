# -*- coding: utf-8 -*-
import base64
import hashlib
import re
from django.utils.html import escape

colorcode_regex = re.compile(r'(\^[0-9])')
colors = {
    u'^0': '#000000',
    u'^1': '#ff0000',
    u'^2': '#00ff00',
    u'^3': '#fff000',
    u'^4': '#0000ff',
    u'^5': '#00f0ff',
    u'^6': '#ff00ff',
    u'^7': '#ffffff',
    u'^8': '#ff9900',
    u'^9': '#b4b4b4'
}
DEFAULT_COLOR = u'^7'


def authenticate(u_time, key, token):
    """Returns true if the token was generated from uTime and key"""
    h = hashlib.sha256("{}|{}".format(u_time, key))
    return base64.b64encode(h.digest(), '-_') == token.replace(' ', '+')


def strip_color_tokens(msg):
    result = ""
    i = 0
    while i < len(msg):
        if msg[i] == "^" and i + 1 < len(msg):
            if msg[i + 1].isdigit():
                i += 2
                continue
            elif msg[i + 1] == "^":
                i += 1

        result += msg[i]
        i += 1
    return result


def username_with_html_colors(username):
    """

    :param username: username containing warsow text color codes, i.e.
        u'^1Playe^5r^9!^5?'
    :type username: unicode
    :return: username with html colors, i.e.
        u'<span style="color:#ff0000">Playe</span>
        <span style="color:#00f0ff">r</span>
        <span style="color:#b4b4b4">!</span>
        <span style="color:#00f0ff">?</span>'
    :rtype: unicode
    """
    if not username:
        return u''

    # replace special characters
    username = escape(username)
    username_colored = u''

    # prefix default color code if needed
    if not re.match('^\^[0-9].*', username):
        username = DEFAULT_COLOR + username

    color_split = filter(None, colorcode_regex.split(username))
    # filter(None, p.split('^1Playe^5r^9!^5?'))
    #   ['^1', 'Playe', '^5', 'r', '^9', '!', '^5', '?']
    current_color = None
    for k in color_split:
        if current_color:
            spanstr = u'<span style="color:{rgb}">{chars}</span>'.format(
                rgb=colors[current_color], chars=k)
            username_colored += spanstr
            current_color = None
        else:
            current_color = k
    return username_colored


def weaponstring(weapons):
    """

    :param weapons: bitmask string indicating weapons on a map
        for instance, no weapons:   0000000
                and all weapons:    1111111

    :return: sequence of <div> elements with 'class' corresponding to the waepons on this map
    """

    result = ''
    div = '<div class="weapon {weapon}"></div>'
    if weapons[0] == '1':
        result += div.format(weapon='mg')  # machinegun
    if weapons[1] == '1':
        result += div.format(weapon='rg')  # riotgun
    if weapons[2] == '1':
        result += div.format(weapon='gl')  # grenade launcher
    if weapons[3] == '1':
        result += div.format(weapon='rl')  # rocket launcher
    if weapons[4] == '1':
        result += div.format(weapon='pg')  # plasmagun
    if weapons[5] == '1':
        result += div.format(weapon='lg')  # lasergun
    if weapons[6] == '1':
        result += div.format(weapon='eb')  # electrobolt
    return result


def millis_to_str(milli):
    """Formats milliseconds to HH:MM:SS format

    Omits hours or minutes if they are 00"""
    hours = milli / 3600000
    milli -= hours * 3600000
    mins = milli / 60000
    milli -= mins * 60000
    sec = milli / 1000
    milli -= sec * 1000

    if hours == 0:
        str_hours = ""
    else:
        str_hours = "{:d}:".format(hours)

    if mins == 0:
        if hours == 0:
            str_mins = ""
        else:
            str_mins = "00:"
    else:
        if hours == 0:
            str_mins = "{}:".format(mins).zfill(2)
        else:
            str_mins = "{}:".format(mins).zfill(3)

    if sec == 0:
        if mins == 0:
            str_sec = "0."
        else:
            str_sec = "00."
    else:
        if mins == 0:
            str_sec = "{}.".format(sec).zfill(2)
        else:
            str_sec = "{}.".format(sec).zfill(3)

    str_millis = "{:d}".format(milli).zfill(3)
    return str_hours + str_mins + str_sec + str_millis


def average(l):
    assert len(l) != 0
    return sum(l) / len(l)


def floats_differ(flt1, flt2):
    """Returns True for floats differing 0.000001 or less, otherwise False"""
    return abs(float(flt1) - float(flt2)) > 0.000001