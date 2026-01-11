import re
import pandas as pd


def _to_number(s):
    try:
        return int(s.replace(',', ''))
    except:
        try:
            return float(s.replace(',', ''))
        except:
            return 0


def parse_holdings(ocr_text):
    """Attempt to extract holdings from OCR text using heuristics.

    Tries to detect table-like rows by splitting on multiple spaces. Returns DataFrame with
    columns `symbol`, `quantity`, `value` (value may be 0 if not found).
    """
    lines = [l.strip() for l in ocr_text.splitlines() if l.strip()]
    rows = []

    for line in lines:
        # split by 2+ spaces which often separate table columns
        parts = re.split(r"\s{2,}", line)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 3:
            # heuristic: first part symbol, last part value, middle quantity
            symbol = re.sub(r"[^A-Za-z0-9\.\-]", "", parts[0]).upper()
            qty = _to_number(re.sub(r"[^0-9,\.]+", "", parts[1]))
            val = _to_number(re.sub(r"[^0-9,\.]+", "", parts[-1]))
            # only accept if symbol has letters and qty>0 or val>0
            if re.search(r"[A-Z]", symbol) and (qty or val):
                rows.append((symbol, qty, val))
                continue

        # fallback: try regex like SYMBOL 100 1,234.56
        m = re.search(r"([A-Za-z\.\-]{1,8})\s+([0-9,]+)\s+([0-9,\.]+)", line)
        if m:
            symbol = m.group(1).upper()
            qty = _to_number(m.group(2))
            val = _to_number(m.group(3))
            rows.append((symbol, qty, val))

    # final fallback: extract any symbol-like token followed by a number
    if not rows:
        for line in lines:
            m = re.search(r"([A-Za-z\.\-]{1,8}).*?([0-9,]+)", line)
            if m:
                symbol = m.group(1).upper()
                qty = _to_number(m.group(2))
                rows.append((symbol, qty, 0.0))

    df = pd.DataFrame(rows, columns=['symbol', 'quantity', 'value'])
    # normalize: remove empty symbol rows
    df = df[df['symbol'].str.len() > 0]
    df = df.reset_index(drop=True)
    return df
