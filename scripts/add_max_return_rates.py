from pathlib import Path
import re

PATH = Path("index.html")
text = PATH.read_text(encoding="utf-8")

# Add a dedicated comparison column next to Interest / bidding.
old_col = "['interest','Interest / bidding',true,165],"
new_col = "['maxReturn','Max return rate',true,150],['interest','Interest / bidding',true,165],"
if "['maxReturn','Max return rate'" not in text:
    if old_col not in text:
        raise SystemExit("Could not locate interest column definition")
    text = text.replace(old_col, new_col, 1)

# These labels intentionally preserve the legal return mechanism instead of
# pretending every state pays a directly comparable APR.
RATES = [
    ("Florida", "18%/yr max"),
    ("Arizona", "16%/yr max"),
    ("Colorado", "Variable annual statutory rate"),
    ("Indiana", "15% redemption penalty max (not APR)"),
    ("Iowa", "2%/month (24% nominal/yr)"),
    ("Illinois", "9% per 6 months max bid"),
    ("Maryland", "Up to 20%/yr in listed markets"),
    ("New Jersey", "18%/yr interest max (+ possible penalty)"),
    ("Alabama", "12%/yr"),
    ("Nebraska", "14%/yr"),
    ("Mississippi", "1.5%/month (18%/yr)"),
    ("Kentucky", "12%/yr"),
    ("South Dakota", "10%/yr max bid"),
    ("West Virginia", "12%/yr"),
    ("Wyoming", "15%/yr + 3% penalty"),
    ("Missouri", "10%/yr max"),
    ("District of Columbia", "1.5%/month (18%/yr)"),
    ("Washington, DC", "1.5%/month (18%/yr)"),
    ("DC —", "1.5%/month (18%/yr)"),
    ("Ohio", "18%/yr statutory ceiling"),
    ("Nevada", "1%/month (12%/yr) — special-assessment certificates"),
]

def rate_for(state: str) -> str:
    for prefix, value in RATES:
        if state.startswith(prefix):
            return value
    return "Varies — verify current jurisdiction rules"

# Operate only inside individual row object literals. The row format is kept
# deliberately simple by the guide's state-addition scripts.
row_re = re.compile(r"\{state:'(?P<state>[^']+)'(?P<body>.*?)(?=\},\n|\}\n\];)", re.S)

def patch(match: re.Match) -> str:
    state = match.group('state')
    whole = match.group(0)
    if "maxReturn:" in whole:
        # Refresh an existing generated value so future rule corrections can
        # be published by updating this mapping only.
        value = rate_for(state).replace("'", "\\'")
        return re.sub(r"maxReturn:'[^']*',", f"maxReturn:'{value}',", whole, count=1)
    marker = "interest:"
    pos = whole.find(marker)
    if pos == -1:
        return whole
    value = rate_for(state).replace("'", "\\'")
    return whole[:pos] + f"maxReturn:'{value}'," + whole[pos:]

text = row_re.sub(patch, text)
PATH.write_text(text, encoding="utf-8")
print("Added/refreshed Max return rate for tax-lien market rows")
