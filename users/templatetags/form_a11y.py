"""Render field form dengan atribut aksesibilitas yang benar.

    {% load form_a11y %}
    {{ field|a11y }}

- aria-describedby -> teks bantuan (help text) dan error dari server
- aria-invalid     -> "true" kalau server menolak isian, selain itu "false"
- data-error       -> id elemen error sisi-browser (:user-invalid), dipakai campusgo.js
"""
from django import template

register = template.Library()


@register.filter
def a11y(bound_field):
    widget_id = bound_field.id_for_label or bound_field.auto_id
    described = []
    if bound_field.help_text:
        described.append(f"{widget_id}-help")
    if bound_field.errors:
        described.append(f"{widget_id}-server-error")

    attrs = {
        "aria-invalid": "true" if bound_field.errors else "false",
        "data-error": f"{widget_id}-client-error",
    }
    if described:
        attrs["aria-describedby"] = " ".join(described)
    return bound_field.as_widget(attrs=attrs)
