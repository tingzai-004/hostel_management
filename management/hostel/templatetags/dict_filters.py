from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """从字典安全取值，不存在就返回 0"""
    if not dictionary or not key:
        return "0"
    value = dictionary.get(str(key))
    if value is None or value == "":
        return "0"
    return value