"""Shared currency and magnitude formatting for the NovaMart demo."""

CURRENCY_CODE = "INR"
CURRENCY_SYMBOL = "₹"


def format_inr(value: float, decimals: int = 0) -> str:
    """Format a number using Indian grouping (e.g. ₹12,34,567)."""
    sign = "-" if value < 0 else ""
    number = abs(float(value))
    formatted = f"{number:,.{decimals}f}"
    return f"{sign}{CURRENCY_SYMBOL}{formatted}"


def format_compact_inr(value: float) -> str:
    """Compact INR for executive UI labels."""
    value = float(value)
    sign = "-" if value < 0 else ""
    n = abs(value)
    if n >= 10_000_000:
        return f"{sign}{CURRENCY_SYMBOL}{n / 10_000_000:.1f}Cr"
    if n >= 100_000:
        return f"{sign}{CURRENCY_SYMBOL}{n / 100_000:.1f}L"
    if n >= 1_000:
        return f"{sign}{CURRENCY_SYMBOL}{n / 1_000:.1f}K"
    return format_inr(value)
