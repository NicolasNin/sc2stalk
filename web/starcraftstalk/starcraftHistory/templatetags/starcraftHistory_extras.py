from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import (
    do_static as _do_static, static as _static,
)

register = template.Library()

@register.filter(name='cut')
def cut(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, '')
@register.filter(name='icon',is_safe=True)
def icon(value,icontype):
    txt=""
    if icontype=="league":
        if value!=None:
            txt='<img src="'
            txt+=_static(value+"icon.png")+'">'
        else:
            txt="?"
    if icontype=="race":
        if value!=None:
            txt='<img src="'+_static(value+"icon_small.png")+'">'
        else:
            txt="?"
    return mark_safe(txt)
