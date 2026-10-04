import math
from typing import Any

CURRENCY_CODE = "INR"
CURRENCY_SYMBOL = "₹"


def format_inr(value: float, decimals: int = 0) -> str:
    """Format a number using standard formatting with currency symbol."""
    try:
        val = float(value)
        if not math.isfinite(val):
            return f"{CURRENCY_SYMBOL}0"
    except (TypeError, ValueError):
        return f"{CURRENCY_SYMBOL}0"
    sign = "-" if val < 0 else ""
    number = abs(val)
    formatted = f"{number:,.{decimals}f}"
    return f"{sign}{CURRENCY_SYMBOL}{formatted}"


def format_compact_inr(value: float) -> str:
    """Compact INR for executive UI labels (e.g. ₹1.2Cr, ₹8.4L, ₹50K)."""
    try:
        val = float(value)
        if not math.isfinite(val):
            return f"{CURRENCY_SYMBOL}0"
    except (TypeError, ValueError):
        return f"{CURRENCY_SYMBOL}0"
    sign = "-" if val < 0 else ""
    n = abs(val)
    if n >= 10_000_000:
        return f"{sign}{CURRENCY_SYMBOL}{n / 10_000_000:.1f}Cr"
    if n >= 100_000:
        return f"{sign}{CURRENCY_SYMBOL}{n / 100_000:.1f}L"
    if n >= 1_000:
        return f"{sign}{CURRENCY_SYMBOL}{n / 1_000:.1f}K"
    return format_inr(val)


def json_safe(value: Any) -> Any:
    """Recursively sanitize non-finite floats (NaN/Inf) for standard JSON serialization."""
    if isinstance(value, float):
        return value if math.isfinite(value) else 0.0
    if isinstance(value, (int, str, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]
    try:
        if hasattr(value, "item"):
            return json_safe(value.item())
    except Exception:
        pass
    return value