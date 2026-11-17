from django import template

register = template.Library()

AVATAR_COLORS = [
    "bg-teal-700", "bg-amber-700", "bg-pink-700",
    "bg-indigo-600", "bg-sky-700", "bg-emerald-700",
]
FILE_CLASS = (
    "block w-full text-sm text-zinc-700 dark:text-zinc-300 "
    "file:mr-3 file:cursor-pointer file:rounded-lg file:border-0 "
    "file:bg-zinc-100 file:px-4 file:py-2.5 file:text-sm file:font-medium "
    "file:text-zinc-900 hover:file:bg-zinc-200 "
    "dark:file:bg-zinc-800 dark:file:text-zinc-100"
)


@register.filter
def avatar_color(name):
    """Stable colour for the initials fallback, based on the username."""
    return AVATAR_COLORS[sum(ord(c) for c in str(name)) % len(AVATAR_COLORS)]


@register.filter
def styled(field):
    """Render a form field with the Circle input styles."""
    widget = field.field.widget
    attrs = {"class": FILE_CLASS if getattr(widget, "input_type", "") == "file" else "input"}
    if field.errors:
        attrs["aria-invalid"] = "true"
    return field.as_widget(attrs=attrs)
