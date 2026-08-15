#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main():
    text = INDEX.read_text(encoding="utf-8")

    if "id=\"countyFilter\"" not in text:
        text = text.replace(
            '<select id="stateFilter" class="control"><option value="">All states</option></select>\n  <select id="statusFilter"',
            '<select id="stateFilter" class="control"><option value="">All states</option></select>\n  <select id="countyFilter" class="control"><option value="">All counties / markets</option></select>\n  <select id="statusFilter"',
            1,
        )
        text = text.replace(
            '.toolbar{display:grid;grid-template-columns:2fr 1fr 1fr auto;',
            '.toolbar{display:grid;grid-template-columns:2fr 1fr 1fr 1fr auto;',
            1,
        )

    if "function marketCounty" not in text:
        text = text.replace(
            "function stateName(v){return (v||'').split(' — ')[0]}",
            "function stateName(v){return (v||'').split(' — ')[0]}function marketCounty(v){const p=(v||'').split(' — ');return p.length>1?p.slice(1).join(' — '):''}",
            1,
        )

    old = "const q=document.querySelector('#search').value.toLowerCase(),st=document.querySelector('#stateFilter').value,sf=document.querySelector('#statusFilter').value;const filtered=rows.filter(r=>(!st||stateName(r.state)===st)&&(!sf||r.availability===sf)&&Object.values(r).join(' ').toLowerCase().includes(q));"
    new = "const q=document.querySelector('#search').value.toLowerCase(),st=document.querySelector('#stateFilter').value,ct=document.querySelector('#countyFilter').value,sf=document.querySelector('#statusFilter').value;const filtered=rows.filter(r=>(!st||stateName(r.state)===st)&&(!ct||marketCounty(r.state)===ct)&&(!sf||r.availability===sf)&&Object.values(r).join(' ').toLowerCase().includes(q));"
    if old in text:
        text = text.replace(old, new, 1)

    state_setup = "const states=[...new Set(rows.map(r=>stateName(r.state)))].sort();document.querySelector('#stateFilter').innerHTML='<option value=\"\">All states</option>'+states.map(s=>`<option value=\"${s}\">${s}</option>`).join('');"
    if "function syncCounties" not in text and state_setup in text:
        replacement = state_setup + "\nfunction syncCounties(){const st=document.querySelector('#stateFilter').value,sel=document.querySelector('#countyFilter'),current=sel.value;const counties=[...new Set(rows.filter(r=>!st||stateName(r.state)===st).map(r=>marketCounty(r.state)).filter(Boolean))].sort();sel.innerHTML='<option value=\"\">All counties / markets</option>'+counties.map(c=>`<option value=\"${c}\">${c}</option>`).join('');if(counties.includes(current))sel.value=current}syncCounties();"
        text = text.replace(state_setup, replacement, 1)

    text = text.replace(
        "document.querySelector('#stateFilter').addEventListener('change',render);document.querySelector('#statusFilter').addEventListener('change',render);render();",
        "document.querySelector('#stateFilter').addEventListener('change',()=>{syncCounties();render()});document.querySelector('#countyFilter').addEventListener('change',render);document.querySelector('#statusFilter').addEventListener('change',render);render();",
        1,
    )

    INDEX.write_text(text, encoding="utf-8")
    print("Tax-lien county/market filter ensured")


if __name__ == "__main__":
    main()
