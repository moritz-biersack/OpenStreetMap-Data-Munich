# -*- coding: utf-8 -*-
"""Basic utility functions for OSM data audit."""

def to_unicode(unicode_or_str):
    """Return unicode from a string or unicode."""

    if isinstance(unicode_or_str, str):
        value = unicode_or_str.decode('utf-8')
    else:
        value = unicode_or_str

    return value


def to_str(unicode_or_str):
    """Return string from string or unicode."""

    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('utf-8')
    else:
        value = unicode_or_str

    return value
