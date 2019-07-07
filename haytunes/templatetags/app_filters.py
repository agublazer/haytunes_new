from django import template

register = template.Library()

@register.filter(name='addcss')
def addcss(field, css):
    attrs = {}
    definition = css.split(',')

    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            t, v = d.split(':')
            attrs[t] = v
    return field.as_widget(attrs=attrs)


@register.filter(name='addplaceholder')
def addplaceholder(field, css):
    attrs = {}
    attrs1 = {'class': 'form-control'}
    definition = css.split(',')

    for d in definition:
        if ':' not in d:
            attrs['placeholder'] = d
        else:
            t, v = d.split(':')
            attrs[t] = v
    attrs1.update(attrs)
    return field.as_widget(attrs=attrs1)