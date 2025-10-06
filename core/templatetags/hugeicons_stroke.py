from django import template

register = template.Library()

# Icon mapping for common icons used in the project
ICON_MAP = {
    'diamond-02': '💎',
    'star': '⭐',
    'arrow-down-02': '⬇️',
    'arrow-left-02': '⬅️',
    'arrow-right-02': '➡️',
    'unlink-05': '🔗',
    'favourite': '❤️',
    'eye': '👁️',
    'shopping-cart-02': '🛒',
    'call': '📞',
    'user': '👤',
    'user-multiple': '👥',
    'time-04': '⏰',
    'award-05': '🏆',
    'bubble-chat': '💬',
    'search-01': '🔍',
    'settings-02': '⚙️',
    'cancel-01': '❌',
    'sort-by-down-01': '🔽',
    'remove-02': '➖',
    'add-02': '➕',
    'delete-04': '🗑️',
    'lock-key': '🔐',
    'shield-energy': '🛡️',
}

@register.simple_tag
def hgi_stroke(name, size="24", color="#000000", stroke_width="2"):
    """
    Temporary template tag to handle hgi_stroke functionality.
    Returns Unicode emoji as a fallback until proper icon library is configured.
    """
    return ICON_MAP.get(name, '🔹')  # Default fallback icon
