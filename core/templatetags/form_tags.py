from django import template
register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    return value.as_widget(attrs={**value.field.widget.attrs, 'class': css_class})
