"""Spin by OXXO - Customer value & Flip-Out executive dashboard (Streamlit)."""
import base64
import html
import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='Spin | CLTV & Flip-Out dashboard', page_icon=':credit_card:', layout='wide')
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, 'data')
ASSETS = os.path.join(APP_DIR, 'assets')       # logos (copied from Evidence 3/dashboard_inputs/logos)

# Spin by OXXO palette: purple, orange, white, light blue. Text colors come from the Streamlit theme
# (.streamlit/config.toml has a light and a dark theme), so everything below works in both modes.
PURPLE, PURPLE_DARK, ORANGE, LIGHT_BLUE = '#6A2BC4', '#4B1A9E', '#FF7A00', '#5EC4F0'
WHITE, GREY = '#FFFFFF', '#9A93A8'
MUTED, GRID = GREY, 'rgba(128,128,128,0.22)'
FONT = dict(family='system-ui, -apple-system, Segoe UI, sans-serif', size=13)
DAYS_PER_MONTH = 30.4375

st.markdown(f"""
<style>
/* ---------- page width: use the whole screen ---------- */
[data-testid="stMainBlockContainer"], .block-container {{max-width: 100%; padding: 3.6rem 2.2rem 3rem;}}

/* ---------- header ---------- */
.spin-header {{display: flex; align-items: center; gap: 26px;
  background: linear-gradient(120deg, {PURPLE_DARK} 0%, {PURPLE} 65%, #8A55E0 100%);
  border-radius: 14px; padding: 18px 28px; margin-bottom: 14px; color: {WHITE}; border-bottom: 5px solid {ORANGE};}}
.spin-header .hlogo {{flex: 0 0 auto; padding-right: 26px; border-right: 1px solid rgba(255,255,255,.35);
  display: flex; align-items: center;}}
.spin-header .hlogo img {{height: 84px; display: block;}}
.spin-header .htxt {{flex: 1 1 auto; min-width: 0;}}
.spin-header .title {{font-size: 2rem; font-weight: 700; line-height: 1.2; margin: 0 0 8px;}}
.spin-header .sub {{font-size: .88rem; opacity: .92; line-height: 1.45;}}
.logo-alt {{font-weight: 800; letter-spacing: .03em;}}

/* ---------- section titles (fixed height so side-by-side blocks line up) ---------- */
.sec {{display: flex; align-items: baseline; gap: 10px; height: 2.1rem; margin: 18px 0 6px; overflow: hidden;}}
.sec .t {{font-size: 1.22rem; font-weight: 700; white-space: nowrap;}}
.sec .n {{font-size: .85rem; opacity: .65; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0;}}
.note {{font-size: .85rem; opacity: .7; margin: -2px 0 10px;}}
.stTabs [data-baseweb="tab"] {{font-weight: 600;}}

/* ---------- tab guide (one grid row = equal heights) ---------- */
.tguide {{display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin: 6px 0 14px;}}
.tab-card {{border: 1px solid rgba(128,128,128,0.28); border-radius: 10px; padding: 12px 14px;}}
.tab-card .t {{font-weight: 700; margin-bottom: 4px;}}
.tab-card .d {{font-size: .88rem; opacity: .85;}}

/* ---------- KPI tiles: identical size in every tab (always 5 per row) ---------- */
.kpis {{display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; margin: 12px 0 8px;}}
.kpi {{box-sizing: border-box; height: 112px; background: rgba(106,43,196,0.08); border-left: 4px solid {PURPLE};
  border-radius: 10px; padding: 12px 16px; display: flex; flex-direction: column; justify-content: space-between;
  min-width: 0;}}
.kpi .kl {{font-size: .85rem; opacity: .75; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}}
.kpi .ki {{cursor: help; opacity: .6; margin-left: 4px;}}
.kpi .kv {{font-size: 1.75rem; font-weight: 600; line-height: 1.15; white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; font-variant-numeric: tabular-nums;}}
.kpi .kd {{font-size: .8rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-height: 1.1em;}}
.kpi .kd.up {{color: #16a34a;}} .kpi .kd.down {{color: #dc2626;}} .kpi .kd.flat {{opacity: .6;}}

/* ---------- commission assumptions with merchant logos ---------- */
.brandrow {{display: flex; align-items: center; gap: 10px; height: 52px; margin-bottom: 4px;}}
.chip {{display: inline-flex; align-items: center; justify-content: center; height: 44px; padding: 0 12px;
  background: #FFFFFF; border: 1px solid rgba(128,128,128,0.3); border-radius: 9px; box-sizing: border-box;}}
.chip img {{display: block;}}
.chip .logo-alt {{color: #1F1E24; font-size: .9rem;}}
.brandrow .cap {{flex: 1 1 auto; font-size: .9rem; opacity: .8; line-height: 1.2; min-width: 0;}}
.brandrow .rate {{flex: 0 0 auto; height: 44px; box-sizing: border-box; display: inline-flex; align-items: center;
  padding: 0 14px; background: #FFFFFF; border: 1px solid rgba(128,128,128,0.3); border-radius: 9px;
  font-size: 1.6rem; font-weight: 700; color: #000000; font-variant-numeric: tabular-nums;}}

/* ---------- persona cards (one grid row = equal heights) ---------- */
.pcards {{display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin: 6px 0 4px; align-items: stretch;}}
.pcard {{border: 1px solid rgba(128,128,128,0.28); border-radius: 12px; padding: 14px 16px 12px;
  display: flex; flex-direction: column; min-width: 0;}}
.pcard .strip {{height: 6px; border-radius: 3px; margin-bottom: 10px;}}
.pcard .pname {{font-weight: 700; font-size: 1.08rem; line-height: 1.25; height: 2.5em; overflow: hidden;}}
.pcard .pstats {{display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; margin: 6px 0 12px;}}
.pcard .pstats div {{background: rgba(128,128,128,0.09); border-radius: 7px; padding: 6px 8px; min-width: 0;}}
.pcard .pstats b {{display: block; font-size: .98rem; font-variant-numeric: tabular-nums; white-space: nowrap;}}
.pcard .pstats span {{display: block; font-size: .72rem; opacity: .7; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}}
.ptiles {{container-type: inline-size; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;}}
.ptile {{border-radius: 9px; padding: 10px 11px 9px; background: rgba(128,128,128,0.07); min-width: 0;}}
.ptile .ph {{display: flex; align-items: center; gap: 6px; font-size: .76rem; opacity: .78; white-space: nowrap; overflow: hidden;}}
.ptile .ph svg {{flex: 0 0 auto; width: 16px; height: 16px;}}
.ptile .pv {{font-size: 1.3rem; font-size: clamp(1rem, 7.5cqw, 1.5rem); font-weight: 700; line-height: 1.2; margin: 4px 0 6px;
  white-space: nowrap; font-variant-numeric: tabular-nums;}}
.ptile .bar {{height: 7px; border-radius: 4px; background: rgba(128,128,128,0.2); overflow: hidden;}}
.ptile .bar i {{display: block; height: 100%; border-radius: 4px;}}
.ptile .pn {{font-size: .72rem; opacity: .7; margin-top: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}}
.pflip {{display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 12px 0 10px;
  padding: 8px 11px; border-radius: 9px; border: 1px dashed rgba(128,128,128,0.4); font-size: .82rem;}}
.pflip b {{font-size: 1.1rem; color: {ORANGE};}}
.pdesc {{border-top: 1px solid rgba(128,128,128,0.25); padding-top: 8px;}}
.pdesc summary {{cursor: pointer; font-weight: 600; font-size: .9rem; list-style: none; display: flex;
  align-items: center; justify-content: space-between;}}
.pdesc summary::-webkit-details-marker {{display: none;}}
.pdesc summary::after {{content: '\\25BE'; opacity: .6; transition: transform .15s;}}
.pdesc[open] summary::after {{transform: rotate(180deg);}}
.pdesc p {{font-size: .86rem; opacity: .85; margin: 8px 0 2px; line-height: 1.45;}}
@media (max-width: 1100px) {{.kpis {{grid-template-columns: repeat(3, minmax(0, 1fr));}}
  .pcards, .tguide {{grid-template-columns: repeat(2, minmax(0, 1fr));}}}}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load():
    personas = pd.read_csv(os.path.join(DATA, 'personas.csv'))
    targets = pd.read_csv(os.path.join(DATA, 'target_list.csv'))
    by_persona = pd.read_csv(os.path.join(DATA, 'model_by_persona.csv'))
    drivers = pd.read_csv(os.path.join(DATA, 'drivers.csv'))
    with open(os.path.join(DATA, 'model_card.json')) as f:
        card = json.load(f)
    with open(os.path.join(DATA, 'kpis.json')) as f:
        kpis = json.load(f)
    return personas, targets, by_persona, drivers, card, kpis


@st.cache_data
def logo_uri(fname):
    path = os.path.join(ASSETS, fname)
    if not os.path.exists(path):
        return None
    mime = 'image/svg+xml' if fname.endswith('.svg') else 'image/png'
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()


def logo(fname, alt, height=None):
    """<img> of a logo in assets/ (falls back to the brand name if the file is missing)."""
    uri = logo_uri(fname)
    if uri is None:
        return f"<span class='logo-alt'>{alt}</span>"
    size = f" style='height:{height}px'" if height else ''
    return f"<img src='{uri}' alt='{alt}' title='{alt}'{size}>"


personas, targets, by_persona, drivers, card, kpis = load()
COLOR = dict(zip(personas['name'], personas['color']))
ORDER = list(personas['name'])

# ------------------------------------------------------------------ commission assumptions (sliders in Overview)
BASE_OXXO, BASE_OUT = round(kpis['c_oxxo'] * 100, 2), round(kpis['c_out'] * 100, 2)   # 0.5% / 1.0%
c_oxxo = st.session_state.get('c_oxxo_pct', BASE_OXXO) / 100
c_out = st.session_state.get('c_out_pct', BASE_OUT) / 100


def blended(oxxo_share):
    return oxxo_share * c_oxxo + (1 - oxxo_share) * c_out


# CLTV = avg monthly spend x blended commission x lifespan (months), recomputed with the slider commissions
personas['cltv_per_user'] = personas['avg_monthly_spend'] * blended(personas['oxxo_spend_share']) * personas['lifespan_months']
personas['revenue_2025'] = (personas['oxxo_spend_2025'] * c_oxxo
                            + (personas['spend_2025'] - personas['oxxo_spend_2025']) * c_out)
personas['pct_revenue'] = personas['revenue_2025'] / personas['revenue_2025'].sum()
personas['total_cltv'] = personas['cltv_per_user'] * personas['users']
personas['pct_total_cltv'] = personas['total_cltv'] / personas['total_cltv'].sum()
targets['cltv_mxn'] = (targets['avg_monthly_spend'] * blended(targets['oxxo_spend_share'])
                       * targets['account_age_days'] / DAYS_PER_MONTH)
lifespan_all = kpis.get('lifespan_months', kpis['account_age_days'] / DAYS_PER_MONTH)
cltv_user = kpis['avg_monthly_spend'] * blended(kpis['oxxo_spend_share']) * lifespan_all


def style(fig, height=360, legend=True):
    fig.update_layout(height=height, font=FONT, margin=dict(l=10, r=10, t=40, b=10),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=legend,
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0, title=None, traceorder='normal'),
                      hoverlabel=dict(font=FONT))
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    return fig


def money(x, d=0):
    return f'${x:,.{d}f}'


def signed_money(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):,.0f}"


def h(text):
    """Escape text for HTML blocks; '$' as an entity so Streamlit never reads it as LaTeX."""
    return html.escape(str(text), quote=True).replace('$', '&#36;')


def section(title, note=''):
    """Section title with a fixed height, so blocks placed side by side start at the same line."""
    n = f"<span class='n'>{h(note)}</span>" if note else ''
    st.markdown(f"<div class='sec'><span class='t'>{h(title)}</span>{n}</div>", unsafe_allow_html=True)


def kpi(label, value, delta=None, sign=0, help=None):
    return dict(label=label, value=value, delta=delta, sign=sign, help=help)


def kpi_row(items):
    """Row of KPI tiles. Always a 5-column grid, so every tile has the same size in every tab."""
    tiles = []
    for k in items:
        tip = f"<span class='ki' title='{h(k['help'])}'>&#9432;</span>" if k['help'] else ''
        if k['delta']:
            cls, arrow = {1: ('up', '&#9650; '), -1: ('down', '&#9660; ')}.get(k['sign'], ('flat', ''))
            delta = f"<div class='kd {cls}'>{arrow}{h(k['delta'])}</div>"
        else:
            delta = "<div class='kd'></div>"
        tiles.append(f"<div class='kpi'><div class='kl'>{h(k['label'])}{tip}</div>"
                     f"<div class='kv'>{h(k['value'])}</div>{delta}</div>")
    st.markdown(f"<div class='kpis'>{''.join(tiles)}</div>", unsafe_allow_html=True)


def sgn(x, tol=1e-9):
    return 1 if x > tol else -1 if x < -tol else 0


# ------------------------------------------------------------------ header
st.markdown(
    f"<div class='spin-header'><div class='hlogo'>{logo('spin_logo.svg', 'Spin by OXXO')}</div>"
    f"<div class='htxt'><div class='title'>Customer Value &amp; Flip-Out Dashboard</div>"
    f"<div class='sub'>{kpis['users']:,} users, monthly data Jan 2025 - Jul 2026. Personas built on 2025 behaviour; "
    f"Flip-Out scores as of 31-May-2026 ({kpis['eligible_users']:,} eligible users). CLTV = avg monthly spend x blended "
    f"commission ({c_oxxo:.2%} OXXO / {c_out:.2%} outside, adjustable in Overview) x lifespan in months. "
    f"Light / dark theme: menu &#8942; (top right).</div></div></div>",
    unsafe_allow_html=True)

tab_over, tab_pers, tab_target, tab_model = st.tabs(['Overview', 'Personas', 'Target list', 'Model'])

# ------------------------------------------------------------------ OVERVIEW
with tab_over:
    TAB_GUIDE = [
        ('Overview', PURPLE, 'Headline KPIs, how users, revenue and CLTV split across personas, key insights, and '
                             'commission sliders to test how CLTV changes with the OXXO / non-OXXO commission.'),
        ('Personas', ORANGE, 'One card per persona (size, CLTV, spend, OXXO share, account age, profile and Flip-Out '
                             'rate) plus a radar, heatmap or side-by-side view to compare them.'),
        ('Target list', LIGHT_BLUE, 'Users ranked by Flip-Out score. Filter by persona and score decile, set the campaign '
                                    'capacity and see the flip-outs captured by the model vs. random selection; '
                                    'download the contact list.'),
        ('Model', PURPLE_DARK, 'Current Flip-Out model: test metrics (PR-AUC, capture and lift at 10%), top drivers, '
                               'performance by persona and a comparison with the previous model.'),
    ]
    st.markdown("<div class='tguide'>" + ''.join(
        f"<div class='tab-card' style='border-top:4px solid {color}'><div class='t'>{name}</div>"
        f"<div class='d'>{h(desc)}</div></div>" for name, color, desc in TAB_GUIDE) + "</div>", unsafe_allow_html=True)

    changed = abs(cltv_user - kpis['cltv_per_user']) > 0.005
    d_cltv = cltv_user - kpis['cltv_per_user']
    kpi_row([
        kpi('Users', f"{kpis['users']:,}", help='Unique users in the dataset'),
        kpi('OXXO spend share', f"{kpis['oxxo_spend_share']:.1%}",
            help='Share of 2025 spend made at OXXO (estimated as OXXO share of transactions x spend)'),
        kpi('Flip-Out rate', f"{kpis['flipout_rate']:.1%}",
            help='Share of eligible users that moved >= 10 pp of their spend outside OXXO in Jun-Jul 2026'),
        kpi('Avg monthly spend', money(kpis['avg_monthly_spend']), help='Average 2025 monthly spend per user (MXN)'),
        kpi('CLTV per user', money(cltv_user),
            f"{signed_money(d_cltv)} vs {BASE_OXXO:.1f}% / {BASE_OUT:.1f}%" if changed else None, sgn(d_cltv),
            help=f"Commission {c_oxxo:.2%} OXXO / {c_out:.2%} outside; average account age "
                 f"{kpis['account_age_days']:,.0f} days used as lifespan"),
    ])

    left, right = st.columns([3, 2], gap='large')
    with left:
        section('Users by persona vs. where the value is')
        rows = {'Users': 'pct_users', 'Revenue 2025': 'pct_revenue', 'Total CLTV': 'pct_total_cltv'}
        fig = go.Figure()
        for _, p in personas.iterrows():
            fig.add_bar(y=list(rows), x=[p[v] for v in rows.values()], name=p['name'], orientation='h',
                        marker=dict(color=p['color'], line=dict(width=0)),
                        text=[f"{p[v]:.0%}" if p[v] >= 0.05 else '' for v in rows.values()],
                        textposition='inside', insidetextanchor='middle',
                        customdata=[[int(p['users'])]] * 3,
                        hovertemplate=f"<b>{p['name']}</b><br>%{{y}}: %{{x:.1%}}<br>Users: %{{customdata[0]:,}}<extra></extra>")
        fig.update_layout(barmode='stack', bargap=0.35, xaxis=dict(tickformat='.0%', range=[0, 1]), yaxis=dict(autorange='reversed'))
        st.plotly_chart(style(fig, 340), width='stretch')
    with right:
        section('CLTV per user by persona', 'MXN')
        p = personas.sort_values('cltv_per_user')
        fig = go.Figure(go.Bar(x=p['cltv_per_user'], y=p['name'], orientation='h', marker_color=list(p['color']),
                               text=[money(v) for v in p['cltv_per_user']], textposition='outside', cliponaxis=False,
                               hovertemplate='<b>%{y}</b><br>CLTV per user: $%{x:,.0f}<extra></extra>'))
        fig.update_xaxes(range=[0, p['cltv_per_user'].max() * 1.4], tickprefix='$')
        st.plotly_chart(style(fig, 340, legend=False), width='stretch')

    with st.container(border=True):
        section('CLTV commission assumptions')
        st.markdown("<div class='note'>Team assumption; Spin does not publish its rates. "
                    "The sliders update CLTV and revenue in every tab.</div>", unsafe_allow_html=True)
        s1, s2 = st.columns(2, gap='large')
        with s1:
            st.markdown(f"<div class='brandrow'><span class='chip'>{logo('oxxo.svg', 'OXXO', 30)}</span>"
                        f"<span class='cap'>Spend at OXXO</span>"
                        f"<span class='rate'>{c_oxxo * 100:.2f}%</span></div>", unsafe_allow_html=True)
            st.slider('Commission on OXXO spend', 0.25, 2.0, BASE_OXXO, step=0.05, format='%.2f%%', key='c_oxxo_pct')
        with s2:
            chips = ''.join(f"<span class='chip'>{logo(f, alt, ht)}</span>" for f, alt, ht in
                            [('walmart.svg', 'Walmart', 22), ('heb.png', 'H-E-B', 28), ('soriana.svg', 'Soriana', 26)])
            st.markdown(f"<div class='brandrow'>{chips}<span class='cap'>Spend outside OXXO</span>"
                        f"<span class='rate'>{c_out * 100:.2f}%</span></div>", unsafe_allow_html=True)
            st.slider('Commission on spend outside OXXO', 0.25, 2.0, BASE_OUT, step=0.05, format='%.2f%%', key='c_out_pct')

    pw = personas.set_index('name')
    top = pw['pct_revenue'].idxmax()
    oxxo = pw['oxxo_spend_share'].idxmax()
    pool = by_persona.sort_values('pct_in_top10', ascending=False).iloc[0]
    section('Key insights')
    st.markdown(
        f"- **{top}** is {pw.loc[top, 'pct_users']:.0%} of users but **{pw.loc[top, 'pct_revenue']:.0%} of 2025 revenue**; "
        f"its CLTV ({money(pw.loc[top, 'cltv_per_user'])}) is {pw.loc[top, 'cltv_per_user'] / cltv_user:.1f}x the average. Retaining it is priority #1.\n"
        f"- **{oxxo}** spends **{pw.loc[oxxo, 'oxxo_spend_share']:.0%} at OXXO**, where Spin earns {c_oxxo:.2%} vs. "
        f"{c_out:.2%} outside: each peso moved outside OXXO earns {c_out / c_oxxo:.1f}x the commission.\n"
        f"- **{pool['persona']}** concentrates the model's targets: {pool['pct_in_top10']:.0%} of its eligible users are in "
        f"the top 10% of Flip-Out scores (flip-out rate {pool['flipout_rate']:.0%}).\n"
        f"- Account age is similar across personas (~{kpis['account_age_days'] / DAYS_PER_MONTH:.0f} months), so CLTV differences "
        f"come from **spend level and OXXO share**, not tenure.")

# ------------------------------------------------------------------ PERSONAS
ICON = {   # 24x24 line icons, drawn with the text color
    'cltv': "<circle cx='12' cy='12' r='9'/><path d='M15 9.2c-.5-.9-1.6-1.4-3-1.4-1.7 0-3 .8-3 2s1.3 1.7 3 2 3 .8 3 2-1.3 2-3 2"
            "c-1.4 0-2.5-.5-3-1.4M12 6v12'/>",
    'spend': "<path d='M3 4h2l2.4 10.2a1 1 0 0 0 1 .8h8.8a1 1 0 0 0 1-.8L20 8H6.2'/><circle cx='9' cy='19' r='1.4'/>"
             "<circle cx='17' cy='19' r='1.4'/>",
    'oxxo': "<path d='M4 10v10h16V10M3 10l2-6h14l2 6zM10 20v-5h4v5'/>",
    'age': "<rect x='4' y='5' width='16' height='15' rx='2'/><path d='M4 10h16M8 3v4M16 3v4'/>",
}


def icon(name):
    return (f"<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.8' stroke-linecap='round' "
            f"stroke-linejoin='round'>{ICON[name]}</svg>")


def persona_card(p):
    color = p['color']
    tiles = [   # (icon, label, value, bar fill 0-1, note)
        ('cltv', 'CLTV / user', money(p['cltv_per_user']), p['cltv_per_user'] / personas['cltv_per_user'].max(),
         f"{p['cltv_per_user'] / cltv_user:.1f}x the average user"),
        ('spend', 'Monthly spend', money(p['avg_monthly_spend']),
         p['avg_monthly_spend'] / personas['avg_monthly_spend'].max(),
         f"{p['avg_monthly_spend'] / kpis['avg_monthly_spend']:.1f}x the average user"),
        ('oxxo', 'OXXO share', f"{p['oxxo_spend_share']:.1%}", p['oxxo_spend_share'],
         f"average user {kpis['oxxo_spend_share']:.1%}"),
        ('age', 'Account age', f"{p['account_age_days']:,.0f} d", p['account_age_days'] / personas['account_age_days'].max(),
         f"about {p['account_age_days'] / DAYS_PER_MONTH:.0f} months"),
    ]
    tiles_html = ''.join(
        f"<div class='ptile'><div class='ph'>{icon(ic)}<span>{lab}</span></div><div class='pv'>{h(val)}</div>"
        f"<div class='bar'><i style='width:{max(min(fill, 1), 0.02) * 100:.1f}%;background:{color}'></i></div>"
        f"<div class='pn'>{h(note)}</div></div>" for ic, lab, val, fill, note in tiles)
    stats = [(f"{int(p['users']):,}", 'users'), (f"{p['pct_users']:.1%}", 'of base'), (f"{p['pct_revenue']:.1%}", 'of revenue')]
    return (f"<div class='pcard'><div class='strip' style='background:{color}'></div>"
            f"<div class='pname'>{h(p['name'])}</div>"
            f"<div class='pstats'>{''.join(f'<div><b>{v}</b><span>{l}</span></div>' for v, l in stats)}</div>"
            f"<div class='ptiles'>{tiles_html}</div>"
            f"<div class='pflip'><span>Flip-Out rate<br><span style='opacity:.7'>of {int(p['eligible_users']):,} "
            f"eligible users</span></span><b>{p['flipout_rate']:.0%}</b></div>"
            f"<details class='pdesc'><summary>Profile</summary><p>{h(p['profile'])}</p></details></div>")


with tab_pers:
    section('Persona cards', 'click "Profile" on a card to read its description')
    st.markdown("<div class='pcards'>" + ''.join(persona_card(p) for _, p in personas.iterrows()) + "</div>",
                unsafe_allow_html=True)
    st.caption('Bars: CLTV, monthly spend and account age are scaled to the highest persona; '
               'OXXO share is shown on a 0-100% scale.')

    section('Compare personas')
    METRICS = {'cltv_per_user': ('CLTV per user', lambda v: money(v)),
               'avg_monthly_spend': ('Avg monthly spend', lambda v: money(v)),
               'oxxo_spend_share': ('OXXO spend share', lambda v: f'{v:.1%}'),
               'account_age_days': ('Account age (days)', lambda v: f'{v:,.0f}'),
               'tx_per_month': ('Purchases / month', lambda v: f'{v:.1f}'),
               'active_months_pct': ('Active months', lambda v: f'{v:.0%}'),
               'merchant_entropy': ('Merchant diversity', lambda v: f'{v:.2f}'),
               'ecommerce_ratio': ('E-commerce share', lambda v: f'{v:.0%}'),
               'app_onboarded': ('Onboarded in app', lambda v: f'{v:.0%}'),
               'flipout_rate': ('Flip-Out rate', lambda v: f'{v:.0%}')}
    view = st.radio('View', ['Radar', 'Heatmap', 'Side by side'], horizontal=True, label_visibility='collapsed')
    chosen = st.multiselect('Personas to compare', ORDER, default=ORDER)
    sub = personas[personas['name'].isin(chosen)]
    if sub.empty:
        st.warning('Select at least one persona.')
    elif view == 'Radar':
        keys = list(METRICS)
        scale = personas[keys].max()                       # 1 = best persona on that metric

        def luminance(hex_color):
            r, g, b = (int(hex_color.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4))
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        def rgba(hex_color, alpha):
            r, g, b = (int(hex_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
            return f'rgba({r},{g},{b},{alpha})'

        theta = [METRICS[k][0] for k in keys]
        # Axis labels in black; in dark mode black would be invisible, so they use the theme's light text there.
        RADAR_LABEL = '#ECEAF1' if getattr(st.context.theme, 'type', 'light') == 'dark' else '#000000'
        fig = go.Figure()
        # Darkest persona first = drawn at the back; lighter shapes on top stay visible.
        for _, p in sub.assign(lum=sub['color'].map(luminance)).sort_values('lum').iterrows():
            r = (p[keys] / scale).tolist()
            fig.add_scatterpolar(r=r + r[:1], theta=theta + theta[:1], name=p['name'], fill='toself',
                                 line=dict(color=p['color'], width=2.5), fillcolor=rgba(p['color'], 0.22),
                                 marker=dict(size=6, color=p['color']), mode='lines+markers',
                                 legendrank=ORDER.index(p['name']),
                                 customdata=[METRICS[k][1](p[k]) for k in keys] + [METRICS[keys[0]][1](p[keys[0]])],
                                 hovertemplate=f"<b>{p['name']}</b><br>%{{theta}}: %{{customdata}}<extra></extra>")
        fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', domain=dict(x=[0, 0.78], y=[0, 1]),
                                     radialaxis=dict(range=[0, 1], showticklabels=False, showline=False, ticks='', gridcolor=GRID),
                                     angularaxis=dict(gridcolor=GRID, linecolor=GRID, rotation=90, direction='clockwise',
                                                      tickfont=dict(size=12, color=RADAR_LABEL))))
        style(fig, 560)
        fig.update_layout(margin=dict(l=90, r=20, t=50, b=50),
                          legend=dict(orientation='v', x=0.82, xanchor='left', y=0.5, yanchor='middle',
                                      title=dict(text='Persona'), itemclick='toggle', itemdoubleclick='toggleothers'))
        st.plotly_chart(fig, width='stretch')
        st.caption('Each axis is scaled to the persona with the highest value (= outer ring). Hover for the real values.')
    elif view == 'Heatmap':
        keys = list(METRICS)
        z = (sub[keys] - personas[keys].mean()) / personas[keys].std()
        txt = [[METRICS[k][1](v) for k, v in zip(keys, row)] for row in sub[keys].values]
        fig = go.Figure(go.Heatmap(z=z.values, x=[METRICS[k][0] for k in keys], y=sub['name'], text=txt,
                                   texttemplate='%{text}', colorscale='RdBu_r', zmid=0, zmin=-1.6, zmax=1.6, colorbar=dict(title='vs. avg<br>persona (z)'),
                                   hovertemplate='<b>%{y}</b><br>%{x}: %{text}<extra></extra>'))
        fig.update_yaxes(autorange='reversed')
        st.plotly_chart(style(fig, 120 + 70 * len(sub), legend=False), width='stretch')
        st.caption('Color = how far each persona is from the average persona (red above, blue below). Text = real value.')
    else:
        table = sub.set_index('name')[list(METRICS)].T
        table = table.apply(lambda col: [METRICS[k][1](v) for k, v in zip(table.index, col)])
        table.index = [METRICS[k][0] for k in METRICS]
        st.dataframe(table, width='stretch')

# ------------------------------------------------------------------ TARGET LIST
with tab_target:
    section('Who should Marketing contact for a Flip-Out campaign?')
    f1, f2, f3 = st.columns(3, gap='large')
    sel_p = f1.multiselect('Persona', ORDER, default=ORDER)
    sel_d = f2.multiselect('Score decile (1 = highest scores)', list(range(1, 11)), default=list(range(1, 11)))
    cap = f3.slider('Campaign capacity (% of the filtered users contacted)', 5, 30, 10, step=1, format='%d%%')

    pool = targets[targets['persona'].isin(sel_p) & targets['score_decile'].isin(sel_d)].sort_values('rank')
    if pool.empty:
        st.warning('No users match the filters.')
    else:
        n = len(pool)
        k = max(1, int(np.ceil(cap / 100 * n)))
        contact = pool.head(k)
        events = pool['actual_flip_out'].sum()
        captured = int(contact['actual_flip_out'].sum())
        random_hits = events * k / n
        cltv_model = contact.loc[contact['actual_flip_out'] == 1, 'cltv_mxn'].sum()
        cltv_random = pool.loc[pool['actual_flip_out'] == 1, 'cltv_mxn'].sum() * k / n

        kpi_row([
            kpi('Users to contact', f'{k:,}', help=f'{cap}% of {n:,} filtered users'),
            kpi('Flip-outs captured (model)', f'{captured:,}', f'{captured - random_hits:+,.0f} vs random',
                sgn(captured - random_hits, 0.5)),
            kpi('Flip-outs captured (random)', f'{random_hits:,.0f}',
                help='Flip-outs a random selection of the same size would capture'),
            kpi('Lift vs random', f'{captured / random_hits:.2f}x' if random_hits else '-',
                help='Flip-outs captured by the model / flip-outs a random selection of the same size would capture'),
            kpi('CLTV of captured flip-outs', money(cltv_model), f'{signed_money(cltv_model - cltv_random)} vs random',
                sgn(cltv_model - cltv_random, 0.5)),
        ])

        left, right = st.columns([3, 2], gap='large')
        with left:
            section('Cumulative flip-outs captured', 'backtest Jun-Jul 2026')
            y = pool['actual_flip_out'].values
            x = np.arange(1, n + 1) / n
            cum = np.cumsum(y) / max(y.sum(), 1)
            step = max(1, n // 400)
            fig = go.Figure()
            fig.add_scatter(x=[0, 1], y=[0, 1], name='Random selection', mode='lines',
                            line=dict(color=GREY, dash='dash', width=2), hoverinfo='skip')
            fig.add_scatter(x=np.r_[0, x[::step]], y=np.r_[0, cum[::step]], name='Flip-Out model', mode='lines',
                            line=dict(color=PURPLE, width=2.5),
                            hovertemplate='Contact top %{x:.0%}<br>Capture %{y:.0%} of flip-outs<extra></extra>')
            fig.add_vline(x=k / n, line=dict(color=ORANGE, width=1.5, dash='dot'))
            fig.add_scatter(x=[k / n], y=[captured / max(events, 1)], mode='markers+text', showlegend=False,
                            marker=dict(size=11, color=ORANGE, line=dict(color=WHITE, width=2)),
                            text=[f'  {captured / max(events, 1):.0%} captured at {cap}%'], textposition='middle right',
                            hoverinfo='skip')
            fig.update_layout(xaxis=dict(title='% of filtered users contacted (by score)', tickformat='.0%', range=[0, 1]),
                              yaxis=dict(title='% of flip-outs captured', tickformat='.0%', range=[0, 1.02]))
            st.plotly_chart(style(fig, 400), width='stretch')
        with right:
            section('Distribution of the Flip-Out score', f'top {cap}% contacted')
            HIST_BLUE, HIST_ORANGE, HIST_INK = '#2a78d6', '#dd8452', '#52514e'   # original colors (same as Figure F8a)
            cutoff = contact['flipout_score'].min()                  # score of the last user inside the top cap%
            bins = np.linspace(0, 1, 41)                             # 40 bins of width 0.025
            centers = (bins[:-1] + bins[1:]) / 2
            in_list = pool.index.isin(contact.index)
            h_out, _ = np.histogram(pool.loc[~in_list, 'flipout_score'], bins=bins)
            h_in, _ = np.histogram(pool.loc[in_list, 'flipout_score'], bins=bins)

            fig = go.Figure()
            fig.add_bar(x=centers, y=h_out, width=0.025, marker_color=HIST_BLUE,
                        name=f'Not contacted ({100 - cap}%, {n - k:,} users)',
                        hovertemplate='Score ≈ %{x:.2f}<br>%{y:,} users<extra>Not contacted</extra>')
            fig.add_bar(x=centers, y=h_in, width=0.025, marker_color=HIST_ORANGE,
                        name=f'Contacted - top {cap}% ({k:,} users)',
                        hovertemplate='Score ≈ %{x:.2f}<br>%{y:,} users<extra>Contacted</extra>')
            fig.add_vline(x=cutoff, line=dict(color=HIST_INK, width=1.5, dash='dash'),
                          annotation_text=f'Top {cap}% cut-off = {cutoff:.3f}<br>{k:,} users contacted',
                          annotation_position='top right', annotation_font=dict(color=HIST_INK, size=11))
            fig.update_traces(marker_line=dict(color='white', width=0.5))
            fig.update_layout(barmode='stack', bargap=0,
                              xaxis=dict(title='Predicted Flip-Out score', range=[0, 1]),
                              yaxis_title='Number of users')
            st.plotly_chart(style(fig, 400), width='stretch')

        section(f'Contact list - top {k:,} users by Flip-Out score')
        show = contact[['rank', 'userId', 'persona', 'flipout_score', 'score_decile', 'avg_monthly_spend',
                        'oxxo_spend_share', 'account_age_days', 'cltv_mxn', 'actual_flip_out']].copy()
        show['oxxo_spend_share'] *= 100
        st.dataframe(show, hide_index=True, width='stretch', height=380, column_config={
            'rank': st.column_config.NumberColumn('Rank'),
            'userId': 'User',
            'persona': 'Persona',
            'flipout_score': st.column_config.ProgressColumn('Flip-Out score', min_value=0, max_value=1, format='%.2f'),
            'score_decile': st.column_config.NumberColumn('Decile'),
            'avg_monthly_spend': st.column_config.NumberColumn('Avg monthly spend', format='$%.0f'),
            'oxxo_spend_share': st.column_config.NumberColumn('OXXO share', format='%.0f%%'),
            'account_age_days': st.column_config.NumberColumn('Account age (d)', format='%d'),
            'cltv_mxn': st.column_config.NumberColumn('CLTV (MXN)', format='$%.0f'),
            'actual_flip_out': st.column_config.CheckboxColumn('Flipped out (backtest)')})
        st.download_button('Download contact list (CSV)', contact.to_csv(index=False).encode('utf-8'),
                           file_name=f'spin_flipout_targets_top{cap}pct.csv', mime='text/csv')
        st.caption('Scores as of 31-May-2026. "Flipped out" is the real outcome in Jun-Jul 2026 (out-of-time backtest), '
                   'used to compare the model with a random selection of the same size. Deciles are computed on all '
                   f"{len(targets):,} eligible users; capacity is applied to the filtered users. "
                   f"CLTV uses the commission set in Overview ({c_oxxo:.2%} OXXO / {c_out:.2%} outside).")

# ------------------------------------------------------------------ MODEL
with tab_model:
    cur, prev = card['current'], card['previous']
    section(f"Current model: {card['version']}", card['name'])
    st.markdown(f"<div class='note'>{h(card['target'])}</div>", unsafe_allow_html=True)
    kpi_row([
        kpi('PR-AUC (test)', f"{cur['pr_auc']:.3f}", f"{cur['pr_auc'] - card['base_rate']:+.3f} vs random ({card['base_rate']:.3f})",
            sgn(cur['pr_auc'] - card['base_rate'])),
        kpi('Capture at 10%', f"{cur['capture_top10']:.1%}", f"{cur['capture_top10'] - 0.10:+.1%} vs random (10%)",
            sgn(cur['capture_top10'] - 0.10),
            help='Share of all flip-outs found by contacting the 10% of users with the highest scores'),
        kpi('Lift at 10%', f"{cur['lift_top10']:.2f}x", help='Precision in the top 10% / flip-out rate'),
        kpi('ROC-AUC (test)', f"{cur['roc_auc']:.3f}", f"{cur['roc_auc'] - 0.5:+.3f} vs random (0.500)",
            sgn(cur['roc_auc'] - 0.5)),
        kpi('Flip-Out base rate (test)', f"{card['base_rate']:.1%}",
            help='Share of test users that flipped out = precision of a random selection (PR-AUC of a random model)'),
    ])
    with st.expander('Training and test setup'):
        st.markdown(f"- **Train:** {card['train']}\n- **Test:** {card['test']}\n- **Hyper-parameters:** {card['params']}"
                    f"\n- **CV PR-AUC (T1):** {card['cv_pr_auc']:.3f}")

    left, right = st.columns([3, 2], gap='large')
    with left:
        section('Top drivers', 'mean |SHAP| of the gradient boosting model')
        d = drivers.sort_values('mean_abs_shap').tail(8)
        fig = go.Figure(go.Bar(x=d['mean_abs_shap'], y=d['driver'], orientation='h', marker_color=PURPLE,
                               customdata=d['direction'],
                               hovertemplate='<b>%{y}</b><br>Mean |SHAP|: %{x:.3f}<br>%{customdata}<extra></extra>'))
        fig.update_xaxes(title='Average impact on the Flip-Out score')
        st.plotly_chart(style(fig, 380, legend=False), width='stretch')
    with right:
        section('How to read the drivers')
        for _, r in drivers.head(5).iterrows():
            arrow = 'raises' if r['lr_coefficient'] > 0 else 'lowers'
            st.markdown(f"- **{r['driver']}**: a higher value {arrow} the chance of a flip-out")
        st.caption('Direction taken from the standardized logistic regression coefficients.')
        st.success('**Takeaway:** flip-outs come from users who buy rarely and still lean on OXXO. Low-frequency, '
                   'OXXO-heavy users are the best campaign targets; frequent, diversified users have little room to flip.')

    section('Performance by persona', 'global top-10% threshold')
    bp = by_persona.drop(columns='persona_id').rename(columns={
        'persona': 'Persona', 'eligible_users': 'Eligible users', 'flipout_rate': 'Flip-Out rate', 'avg_score': 'Avg score',
        'pct_in_top10': '% in top 10%', 'capture_top10': 'Capture at 10%', 'pr_auc': 'PR-AUC'})
    st.dataframe(bp.style.format({'Eligible users': '{:,}', 'Flip-Out rate': '{:.1%}', 'Avg score': '{:.3f}',
                                  '% in top 10%': '{:.1%}', 'Capture at 10%': '{:.1%}', 'PR-AUC': '{:.3f}'}),
                 hide_index=True, width='stretch')

    section('Model comparison')
    comp = pd.DataFrame({
        'Version': [f"{card['previous_version']} - {card['previous_name']}", f"{card['version']} - {card['name']}",
                    'Random selection'],
        'PR-AUC': [prev['pr_auc'], cur['pr_auc'], card['base_rate']],
        'ROC-AUC': [prev['roc_auc'], cur['roc_auc'], 0.5],
        'Capture at 10%': [prev['capture_top10'], cur['capture_top10'], 0.10],
        'Lift at 10%': [prev['lift_top10'], cur['lift_top10'], 1.0]})
    st.dataframe(comp.style.format({'PR-AUC': '{:.3f}', 'ROC-AUC': '{:.3f}', 'Capture at 10%': '{:.1%}', 'Lift at 10%': '{:.2f}x'}),
                 hide_index=True, width='stretch')
    st.markdown('\n'.join(f'- {c}' for c in card['changes']))
