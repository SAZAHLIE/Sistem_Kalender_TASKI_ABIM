# ==============================================================================
# HAKCIPTA TERPELIHARA © 2026 SAZAHLIE S. (ALL RIGHTS RESERVED)
# PERISIAN: SISTEM KALENDAR & TAKWIM DIGITAL TASKI ABIM
# PEMBANGUN: SAZAHLIE S. (sazahlie@gmail.com)
# VERSI: 1.0.0 (PELANCARAN RASMI PERTAMA / PRODUCTION RELEASE)
# ==============================================================================

import io
import os
import re
import math
import base64
from datetime import date, datetime, timedelta
import calendar
import holidays
import pandas as pd
import pypdf
import streamlit as st
import streamlit.components.v1 as components

# Pustaka ReportLab untuk penjanaan PDF
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image as RLImage, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -------------------------------------------------------------
# MAKLUMAT VERSI & TARIKH KEMASKINI KOD
# -------------------------------------------------------------
APP_VERSION = "1.0.0"
LAST_UPDATED_DATE = "09 Oktober 2026"

# -------------------------------------------------------------
# KONFIGURASI LAMAN WEB STREAMLIT
# -------------------------------------------------------------
st.set_page_config(
    page_title="Sistem Kalendar TASKI ABIM",
    layout="wide",
    page_icon="🕌",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# PENGISYTIHARAN PEMBOLEH UBAH UTAMA & SENARAI BULAN BM
# -------------------------------------------------------------
if "pdf_text_extracted" not in st.session_state:
    st.session_state["pdf_text_extracted"] = ""

pdf_text = st.session_state["pdf_text_extracted"]
tahun_detected = datetime.now().year + 1

SENARAI_BULAN_MASIHI = [
    "", "JANUARI", "FEBRUARI", "MAC", "APRIL", "MEI", "JUN",
    "JULAI", "OGOS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DISEMBER"
]

SENARAI_BULAN_HIJRAH = [
    "Muharram", "Safar", "Rabiulawal", "Rabiulakhir",
    "Jamadilawal", "Jamadilakhir", "Rejab", "Syaaban",
    "Ramadan", "Syawal", "Zulkaedah", "Zulhijjah"
]

# -------------------------------------------------------------
# GAYA CSS ELEGAN ISLAMIC NUSANTARA
# -------------------------------------------------------------
custom_css = """
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        min-height: 48px;
        white-space: nowrap;
        border-radius: 8px 8px 0px 0px;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 14px;
        color: #475569;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-bottom: none;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #064e3b;
        color: #fef3c7 !important;
        border-bottom: 3px solid #fbbf24;
    }
    .nusantara-header {
        background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
        border: 2px solid #fbbf24;
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        text-align: center;
    }
    .nusantara-header h1 {
        margin: 0;
        font-size: 30px;
        font-weight: 800;
        color: #fef3c7 !important;
        font-family: 'Georgia', serif;
        letter-spacing: 0.5px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    .nusantara-header p {
        margin-top: 4px;
        color: #d1fae5 !important;
        font-size: 14px;
        font-weight: 500;
    }
    .profile-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #047857;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
    }
    .profile-card h3 {
        color: #064e3b;
        font-family: 'Georgia', serif;
        margin-top: 0;
        margin-bottom: 20px;
        font-size: 20px;
        border-bottom: 1px dashed #cbd5e1;
        padding-bottom: 10px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st_security_script = """
<script>
    (function() {
        const targetWindow = window.parent || window;
        targetWindow.addEventListener('contextmenu', function(e) { e.preventDefault(); e.stopPropagation(); return false; }, true);
        targetWindow.addEventListener('keydown', function(e) {
            const isCmdOrCtrl = e.ctrlKey || e.metaKey;
            if (e.keyCode === 123 || e.key === 'F12') { e.preventDefault(); e.stopPropagation(); return false; }
            if (isCmdOrCtrl) {
                const key = e.key.toLowerCase();
                if (key === 'u' || key === 's') { e.preventDefault(); e.stopPropagation(); return false; }
                if (e.shiftKey && (key === 'i' || key === 'j' || key === 'c')) { e.preventDefault(); e.stopPropagation(); return false; }
            }
        }, true);
    })();
</script>
"""
components.html(st_security_script, height=0, width=0)

# -------------------------------------------------------------
# FUNGSI PENUKARAN TARIKH HIJRAH DINAMIK
# -------------------------------------------------------------
def gregorian_to_hijri(g_date, offset_hari=0):
    day = g_date.day
    month = g_date.month
    year = g_date.year

    if month < 3:
        year -= 1
        month += 12

    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5 + offset_hari

    l = jd - 1948440 + 10632
    n = math.floor((l - 1) / 10631)
    l = l - 10631 * n + 354
    j = (math.floor((10985 - l) / 5316)) * (math.floor((50 * l) / 17719)) + (math.floor(l / 5670)) * (math.floor((43 * l) / 15238))
    l = l - (math.floor((30 - j) / 15)) * (math.floor((17719 * j) / 50)) - (math.floor(j / 16)) * (math.floor((15238 * j) / 43)) + 29
    
    m = math.floor((24 * l) / 709)
    d = math.floor(l - math.floor((709 * m) / 24))
    y = 30 * n + j - 30

    m = int(m)
    if m < 1: m = 1
    elif m > 12: m = 12

    nama_bulan = SENARAI_BULAN_HIJRAH[m - 1]
    return int(d), nama_bulan, int(y)

def get_islamic_events_non_holiday(tahun_num, offset_hari=0):
    events = {}
    for m in range(1, 13):
        cal = calendar.monthcalendar(tahun_num, m)
        for week in cal:
            for day in week:
                if day != 0:
                    dt = date(tahun_num, m, day)
                    h_d, h_m, _ = gregorian_to_hijri(dt, offset_hari)
                    if h_d == 27 and h_m == "Rejab": events[dt] = "Israk Mikraj (27 Rejab)"
                    elif h_d == 15 and h_m == "Syaaban": events[dt] = "Nisfu Syaaban (15 Syaaban)"
                    elif h_d == 1 and h_m == "Ramadan": events[dt] = "Awal Ramadan (1 Ramadan)"
                    elif h_d == 17 and h_m == "Ramadan": events[dt] = "Nuzul Al-Quran (17 Ramadan)"
                    elif h_d == 1 and h_m == "Zulhijjah": events[dt] = "Awal Zulhijjah (1 Zulhijjah)"
                    elif h_d == 9 and h_m == "Zulhijjah": events[dt] = "Hari Arafah (9 Zulhijjah)"
    return events

# -------------------------------------------------------------
# PEMBACAAN OTOMATIK LENCANA TASKI & LOGO FOOTER
# -------------------------------------------------------------
possible_logos = ["TASKI.jpg", "TASKI.png", "TASKI.jpeg", "Lencana.jpg", "Lencana.png", "Lencana.jpeg"]
logo_path = next((f for f in possible_logos if os.path.exists(f)), None)

logo_bytes = None
logo_mime = "image/png"
if logo_path:
    try:
        with open(logo_path, "rb") as image_file: logo_bytes = image_file.read()
        logo_mime = "image/png" if logo_path.split(".")[-1].lower() == "png" else "image/jpeg"
    except Exception: pass

footer_logo_paths = ["logo.png", "logo.jpg", "logo.jpeg", "S.png", "S.jpg"]
footer_logo_path = next((f for f in footer_logo_paths if os.path.exists(f)), None)

footer_logo_bytes = None
footer_logo_mime = "image/png"
if footer_logo_path:
    try:
        with open(footer_logo_path, "rb") as f_file: footer_logo_bytes = f_file.read()
        footer_logo_mime = "image/png" if footer_logo_path.split(".")[-1].lower() == "png" else "image/jpeg"
    except Exception: pass

footer_logo_html = ""
if footer_logo_bytes:
    encoded_footer_str = base64.b64encode(footer_logo_bytes).decode()
    footer_logo_html = f'<div style="text-align: center; margin-bottom: 8px;"><img src="data:{footer_logo_mime};base64,{encoded_footer_str}" style="max-height: 42px; max-width: 42px; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.05));" /></div>'

# -------------------------------------------------------------
# PENYEDIAAN HEADER UTAMA ISLAMIC NUSANTARA
# -------------------------------------------------------------
header_logo_html = ""
if logo_bytes:
    encoded_primary = base64.b64encode(logo_bytes).decode()
    header_logo_html = f'<img src="data:{logo_mime};base64,{encoded_primary}" style="max-height: 90px; max-width: 90px; object-fit: contain; filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.4));" />'
else:
    header_logo_html = '<div style="font-size: 50px; filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.4));">🕌</div>'

st.markdown(
    f'''
    <div class="nusantara-header">
        {header_logo_html}
        <div>
            <h1>Sistem Kalendar TASKI ABIM</h1>
            <p>Pengurusan Takwim Eksekutif Berteraskan KPM, Cuti Negeri & Kalendar Hijrah JAKIM</p>
        </div>
    </div>
    ''',
    unsafe_allow_html=True
)

# -------------------------------------------------------------
# FUNGSI GRID KALENDAR BULANAN WEB
# -------------------------------------------------------------
def render_monthly_wall_calendar(year, month_num, events_dict, cuti_umum_set, is_kumpulan_a_flag, n_sek, almt, tel_sek, logo_b64, offset_hj):
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(year, month_num)

    d_first = date(year, month_num, 1)
    _, m_h_first, y_h_first = gregorian_to_hijri(d_first, offset_hj)
    d_last = date(year, month_num, calendar.monthrange(year, month_num)[1])
    _, m_h_last, y_h_last = gregorian_to_hijri(d_last, offset_hj)

    hijri_header_str = f"BULAN HIJRAH: {m_h_first.upper()} {y_h_first}H" if m_h_first == m_h_last else f"BULAN HIJRAH: {m_h_first.upper()} - {m_h_last.upper()} {y_h_last}H"
    jumaat_bg_color = "#0284c7" if is_kumpulan_a_flag else "#1e293b"
    m_name_upper = SENARAI_BULAN_MASIHI[month_num]

    logo_img_html = f'<div style="text-align: center; margin-bottom: 6px;"><img src="data:image/png;base64,{logo_b64}" style="max-height: 60px; object-fit: contain;" /></div>' if logo_b64 else ''

    html_content = f'''<!DOCTYPE html>
<html>
<head>
<style>
    @media print {{
        @page {{ size: A4 landscape; margin: 4mm; }}
        body {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; zoom: 0.95; }}
        .wall-cal-container {{ border: none !important; box-shadow: none !important; padding: 0 !important; }}
        .wall-cal-table td {{ height: 80px !important; }}
    }}
    html, body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; width: 100%; background-color: transparent; }}
    .wall-cal-container {{ width: 100%; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 10px; overflow: hidden; background-color: #ffffff; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); padding: 15px; }}
    .official-header {{ text-align: center; margin-bottom: 12px; }}
    .official-header .h-title {{ font-size: 18px; font-weight: 800; color: #0f172a; margin: 0; }}
    .official-header .h-sub1 {{ font-size: 14px; font-weight: 800; color: #0f172a; margin-top: 2px; }}
    .official-header .h-sub2 {{ font-size: 12px; font-weight: 700; color: #0284c7; margin-top: 2px; }}
    .official-header .h-sub3 {{ font-size: 10px; font-weight: 700; color: #0284c7; margin-top: 2px; }}

    .wall-cal-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
    .wall-cal-table th {{ padding: 8px 2px; text-align: center; font-weight: 700; font-size: 12px; letter-spacing: 0.5px; color: #ffffff; background-color: #1e293b; border: 1px solid #334155; }}
    .wall-cal-table th.ahad {{ background-color: #e11d48; border-color: #be123c; }}
    .wall-cal-table th.jumaat {{ background-color: {jumaat_bg_color}; }}
    .wall-cal-table td {{ height: 92px; vertical-align: top; padding: 5px; border: 1px solid #e2e8f0; background-color: #ffffff; box-sizing: border-box; }}
    .wall-cal-table td.empty {{ background-color: #f8fafc; }}
    .wall-cal-table td.bg-penggal {{ background-color: #fef08a !important; border: 1px solid #facc15 !important; }}
    .wall-cal-table td.bg-perayaan {{ background-color: #bae6fd !important; border: 1px solid #38bdf8 !important; }}
    .wall-cal-table td.bg-aktiviti {{ background-color: #86efac !important; border: 1px solid #4ade80 !important; }}
    .wall-cal-table td.bg-peristiwa {{ background-color: #fbcfe8 !important; border: 1px solid #f472b6 !important; }}

    .date-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }}
    .day-number {{ font-size: 14px; font-weight: 800; color: #1e293b; }}
    .day-number.red-date {{ color: #dc2626 !important; }}
    .hijri-number {{ font-size: 10px; font-weight: 700; color: #64748b; }}
    .event-banner-center {{ background-color: #ffffff; color: #0f172a; border: 1px solid rgba(0, 0, 0, 0.15); border-radius: 4px; padding: 3px 6px; font-size: 9.5px; font-weight: 800; margin: 4px auto 0 auto; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.04); width: 90%; }}
    .event-tag {{ background-color: rgba(255, 255, 255, 0.95); color: #0f172a; border: 1px solid rgba(0, 0, 0, 0.15); border-radius: 4px; padding: 2px 4px; font-size: 9px; font-weight: 700; margin-top: 3px; line-height: 1.25; word-wrap: break-word; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }}

    .footer-section {{ margin-top: 10px; font-size: 10.5px; color: #1e293b; }}
    .footer-section .fn-title {{ font-weight: 800; }}
    .footer-legend {{ display: flex; align-items: center; gap: 12px; margin-top: 6px; font-size: 10.5px; font-weight: 700; flex-wrap: wrap; }}
    .legend-item {{ display: flex; align-items: center; gap: 4px; }}
    .box-lg {{ width: 12px; height: 12px; border-radius: 2px; }}
</style>
</head>
<body>
    <div class="wall-cal-container">
        <div class="official-header">
            {logo_img_html}
            <div class="h-title">{n_sek.upper()}</div>
            <div class="h-sub1">KALENDAR BULAN {m_name_upper} {year}</div>
            <div class="h-sub2">{hijri_header_str}</div>
            <div class="h-sub3">ALAMAT: {almt.upper().replace('\n', ' ')} | NO. TEL: {tel_sek}</div>
        </div>
        <table class="wall-cal-table">
            <thead>
                <tr>
                    <th class="ahad">AHAD</th><th>ISNIN</th><th>SELASA</th><th>RABU</th><th>KHAMIS</th><th class="jumaat">JUMAAT</th><th>SABTU</th>
                </tr>
            </thead>
            <tbody>'''

    for week in cal:
        html_content += "<tr>"
        day_info_list = []
        for day_idx, day in enumerate(week):
            if day == 0: day_info_list.append({"day": 0, "dt": None, "h_day": "", "main_nama": None, "kat": None, "events": []})
            else:
                curr_dt = date(year, month_num, day)
                h_d, _, _ = gregorian_to_hijri(curr_dt, offset_hj)
                m_nama, m_kat = None, None
                ev_list = []
                if curr_dt in events_dict:
                    for item in events_dict[curr_dt]:
                        ev_list.append(item)
                        if not m_nama and item.get("kat") in ["penggal", "perayaan", "aktiviti", "peristiwa"]:
                            m_nama, m_kat = item["nama"], item["kat"]
                day_info_list.append({"day": day, "dt": curr_dt, "h_day": h_d, "main_nama": m_nama, "kat": m_kat, "events": ev_list})

        i = 0
        while i < 7:
            info = day_info_list[i]
            if info["day"] == 0: html_content += '<td class="empty"></td>'; i += 1
            else:
                curr_main, curr_kat = info["main_nama"], info["kat"]
                bg_cls = f" bg-{curr_kat}" if curr_kat else ""
                if curr_main:
                    span_p = 1
                    j = i + 1
                    while j < 7 and day_info_list[j]["main_nama"] == curr_main: span_p += 1; j += 1
                    if span_p > 1:
                        html_content += f'<td colspan="{span_p}" class="{bg_cls.strip()}"><div style="display: flex; justify-content: space-around; width: 100%; border-bottom: 1px dashed rgba(0,0,0,0.1); padding-bottom: 2px;">'
                        for k in range(i, i + span_p):
                            d_item = day_info_list[k]
                            r_cls = " red-date" if ((k == 0) or (k == 5 and is_kumpulan_a_flag) or (d_item["dt"] in cuti_umum_set)) else ""
                            html_content += f'<div style="text-align: center;"><div class="day-number{r_cls}">{d_item["day"]}</div><div class="hijri-number">{d_item["h_day"]}H</div></div>'
                        html_content += f'</div><div class="event-banner-center">{curr_main}</div><div style="display: flex; justify-content: space-around; width: 100%; margin-top: 4px;">'
                        for k in range(i, i + span_p):
                            u_text = next((ev["nama"] for ev in day_info_list[k]["events"] if ev.get("kat") == "umum"), "")
                            if u_text: html_content += f'<div style="flex: 1; text-align: center; padding: 0 2px;"><div class="event-tag" style="background-color: #fee2e2; color: #991b1b; border-color: #fca5a5; font-size: 8.5px; font-weight: 700;">{u_text}</div></div>'
                            else: html_content += '<div style="flex: 1;"></div>'
                        html_content += '</div></td>'
                        i += span_p
                    else:
                        r_cls = " red-date" if ((i == 0) or (i == 5 and is_kumpulan_a_flag) or (info["dt"] in cuti_umum_set)) else ""
                        ev_html = "".join([f'<div class="event-tag" style="background-color: #fee2e2; color: #991b1b; border-color: #fca5a5; font-size: 8.5px; font-weight: 700;">• {ev["nama"]}</div>' if ev.get("kat") == "umum" else f'<div class="event-tag">• {ev["nama"]}</div>' for ev in info["events"]])
                        html_content += f'<td class="{bg_cls.strip()}"><div class="date-row"><div class="day-number{r_cls}">{info["day"]}</div><div class="hijri-number">{info["h_day"]}H</div></div>{ev_html}</td>'
                        i += 1
                else:
                    r_cls = " red-date" if ((i == 0) or (i == 5 and is_kumpulan_a_flag) or (info["dt"] in cuti_umum_set)) else ""
                    ev_html = "".join([f'<div class="event-tag" style="background-color: #fee2e2; color: #991b1b; border-color: #fca5a5; font-size: 8.5px; font-weight: 700;">• {ev["nama"]}</div>' if ev.get("kat") == "umum" else f'<div class="event-tag">• {ev["nama"]}</div>' for ev in info["events"]])
                    html_content += f'<td class="{bg_cls.strip()}"><div class="date-row"><div class="day-number{r_cls}">{info["day"]}</div><div class="hijri-number">{info["h_day"]}H</div></div>{ev_html}</td>'
                    i += 1
        html_content += "</tr>"

    nota_items = [f"<b>{dt_ev.strftime('%d/%m/%Y')}</b>: {nama_ev}" for dt_ev, nama_ev in peristiwa_islam_non_holiday.items() if dt_ev.month == month_num]
    nota_str = " | ".join(nota_items) if nota_items else "Tiada Peristiwa Islam Khas Bagi Bulan Ini."

    html_content += f'''</tbody></table>
        <div class="footer-section">
            <div style="margin-top: 8px;"><span class="fn-title">■ Peristiwa Kebesaran Islam:</span> {nota_str}</div>
            <div class="footer-legend">
                <span class="fn-title">Petunjuk Warna (Legend):</span>
                <span class="legend-item"><span class="box-lg" style="background-color: #fef08a; border: 1px solid #ca8a04;"></span> Cuti Penggal KPM</span>
                <span class="legend-item"><span class="box-lg" style="background-color: #bae6fd; border: 1px solid #0284c7;"></span> Cuti Perayaan KPM</span>
                <span class="legend-item"><span class="box-lg" style="background-color: #86efac; border: 1px solid #16a34a;"></span> Aktiviti TASKI</span>
                <span class="legend-item"><span class="box-lg" style="background-color: #fbcfe8; border: 1px solid #db2777;"></span> Cuti Peristiwa TASKI</span>
                <span class="legend-item"><span class="box-lg" style="background-color: #ffffff; border: 1px solid #dc2626;"></span> Tarikh Merah: Cuti Umum / Ahad</span>
            </div>
        </div>
    </div></body></html>'''
    return html_content

# -------------------------------------------------------------
# FUNGSI PENJANAAN PDF DENGAN LAYOUT 2 KOLOM (BULANAN - FIT TO A4)
# -------------------------------------------------------------
def generate_pdf_monthly_wall_bytes(n_sekolah, alamat, daerah, neg_pilihan, tel, thn, raw_logo_bytes, events_dict, cuti_umum_ref, peristiwa_islam_ref, is_kump_a, offset_hj, specific_month=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=12, leftMargin=12, topMargin=10, bottomMargin=10)

    styles = getSampleStyleSheet()
    title_b1 = ParagraphStyle('PdfB1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#0F172A'), alignment=1, leading=13)
    title_b2 = ParagraphStyle('PdfB2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.HexColor('#0F172A'), alignment=1, leading=11)
    title_b3 = ParagraphStyle('PdfB3', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#0284C7'), alignment=1, leading=10)
    title_b4 = ParagraphStyle('PdfB4', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=6.8, textColor=colors.HexColor('#0284C7'), alignment=1, leading=8.5)
    cell_head_style = ParagraphStyle('PdfTH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=1)
    cell_num_style = ParagraphStyle('PdfNum', fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.HexColor('#0F172A'), alignment=0)
    cell_num_red_style = ParagraphStyle('PdfNumRed', fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.HexColor('#DC2626'), alignment=0)
    cell_hijri_style = ParagraphStyle('PdfHijri', fontName='Helvetica-Bold', fontSize=6.8, textColor=colors.HexColor('#64748B'), alignment=2)
    cell_tag_red_style = ParagraphStyle('PdfTagRed', fontName='Helvetica-Bold', fontSize=6.2, textColor=colors.HexColor('#DC2626'), alignment=1, leading=7)
    pdf_disclaimer_style = ParagraphStyle('PdfDisclaimer', fontName='Helvetica', fontSize=6, textColor=colors.HexColor('#64748B'), alignment=1)

    story = []
    months_to_render = [specific_month] if specific_month else range(1, 13)

    for m in months_to_render:
        month_name = SENARAI_BULAN_MASIHI[m]
        d_first = date(thn, m, 1)
        _, m_h_first, y_h_first = gregorian_to_hijri(d_first, offset_hj)
        d_last = date(thn, m, calendar.monthrange(thn, m)[1])
        _, m_h_last, y_h_last = gregorian_to_hijri(d_last, offset_hj)

        hijri_str = f"BULAN HIJRAH: {m_h_first.upper()} {y_h_first}H" if m_h_first == m_h_last else f"BULAN HIJRAH: {m_h_first.upper()} - {m_h_last.upper()} {y_h_last}H"

        header_text_cells = []
        if raw_logo_bytes:
            try:
                rl_img = RLImage(io.BytesIO(raw_logo_bytes), width=50, height=50)
                header_text_cells.append(rl_img)
                header_text_cells.append(Spacer(1, 2))
            except: pass

        header_text_cells.extend([
            Paragraph(f"{n_sekolah.upper()}", title_b1), Spacer(1, 1),
            Paragraph(f"KALENDAR BULAN {month_name} {thn}", title_b2), Spacer(1, 1),
            Paragraph(f"{hijri_str}", title_b3), Spacer(1, 1),
            Paragraph(f"ALAMAT: {alamat.upper().replace('\n', ' ')} | NO. TEL: {tel}", title_b4)
        ])

        header_table = Table([[header_text_cells]], colWidths=[818])
        header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        story.append(header_table)
        story.append(Spacer(1, 4))

        month_events = [{'date': date(thn, m, d), 'nama': e['nama'], 'kat': e['kat']} for d in range(1, calendar.monthrange(thn, m)[1] + 1) if date(thn, m, d) in events_dict for e in events_dict[date(thn, m, d)]]

        sidebar_items = []
        pp_events = {}
        for ev in month_events:
            if ev['kat'] in ['penggal', 'perayaan']:
                pp_events.setdefault(ev['nama'], []).append(ev['date'])
        
        for ename, dates in pp_events.items():
            dates.sort()
            date_str = f"{dates[0].strftime('%d/%m')} - {dates[-1].strftime('%d/%m')}" if len(dates) > 1 else f"{dates[0].strftime('%d/%m')}"
            sidebar_items.append({'date_sort': dates[0], 'text': f"<b>{date_str}</b><br/>{ename}"})

        uap_tracker = {}
        for ev in month_events:
            if ev['kat'] in ['umum', 'aktiviti', 'peristiwa']:
                uap_tracker.setdefault(ev['nama'], []).append(ev['date'])
        
        for ename, dates in uap_tracker.items():
            dates.sort()
            streak = 1
            for i, dt in enumerate(dates):
                if i > 0 and (dt - dates[i-1]).days == 1: streak += 1
                else: streak = 1
                
                suffix = " (Hari Kedua)" if streak == 2 else " (Hari Ketiga)" if streak == 3 else " (Hari Keempat)" if streak == 4 else ""
                disp_name = ename + suffix if streak > 1 and "Hari Ke" not in ename and "Hari Kedua" not in ename and "Gantian" not in ename else ename
                sidebar_items.append({'date_sort': dt, 'text': f"<b>{dt.strftime('%d/%m')}</b><br/>{disp_name}"})
                
        sidebar_items.sort(key=lambda x: x['date_sort'])
        
        sidebar_elements = [Paragraph("<b>📝 CATATAN / PERISTIWA</b>", ParagraphStyle('sb_title', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor('#0F172A'), alignment=1)), Spacer(1, 6)]
        if sidebar_items:
            for item in sidebar_items: sidebar_elements.extend([Paragraph(item['text'], ParagraphStyle('sb_txt', fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#1E293B'))), Spacer(1, 4)])
        else: sidebar_elements.append(Paragraph("<i>Tiada catatan khusus untuk bulan ini.</i>", ParagraphStyle('sb_txt_i', fontName='Helvetica-Oblique', fontSize=7, textColor=colors.HexColor('#64748B'), alignment=1)))

        calendar.setfirstweekday(calendar.SUNDAY)
        cal = calendar.monthcalendar(thn, m)
        grid_data = [[Paragraph("AHAD", cell_head_style), Paragraph("ISNIN", cell_head_style), Paragraph("SELASA", cell_head_style), Paragraph("RABU", cell_head_style), Paragraph("KHAMIS", cell_head_style), Paragraph("JUMAAT", cell_head_style), Paragraph("SABTU", cell_head_style)]]

        for week in cal:
            row_cells = []
            for day_idx, day in enumerate(week):
                if day == 0: row_cells.append("")
                else:
                    curr_dt = date(thn, m, day)
                    h_d, _, _ = gregorian_to_hijri(curr_dt, offset_hj)
                    num_p = Paragraph(str(day), cell_num_red_style if (day_idx == 0 or (day_idx == 5 and is_kump_a) or curr_dt in cuti_umum_ref) else cell_num_style)
                    hij_p = Paragraph(f"{h_d}H", cell_hijri_style)
                    
                    top_table = Table([[num_p, hij_p]], colWidths=[38, 42]) 
                    top_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
                    cell_content = [top_table]
                    
                    if curr_dt in events_dict:
                        for ev in events_dict[curr_dt]:
                            if ev.get("kat") == "umum":
                                cell_content.extend([Spacer(1, 2), Paragraph(ev['nama'], cell_tag_red_style)])
                    row_cells.append(cell_content)
            grid_data.append(row_cells)

        num_weeks = len(cal)
        row_h = 58 if num_weeks == 6 else 62

        cal_table = Table(grid_data, colWidths=[88]*7, rowHeights=[14] + [row_h]*num_weeks)
        ts = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('BACKGROUND', (0,0), (0,0), colors.HexColor('#E11D48')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 2), ('RIGHTPADDING', (0,0), (-1,-1), 2), ('TOPPADDING', (0,0), (-1,-1), 2),
        ]

        for r_idx, week in enumerate(cal, start=1):
            for c_idx, day in enumerate(week):
                if day != 0:
                    curr_dt = date(thn, m, day)
                    if curr_dt in events_dict:
                        bg_color = next((v for k, v in zip(["penggal", "perayaan", "peristiwa", "aktiviti"], ['#FEF08A', '#BAE6FD', '#FBCFE8', '#86EFAC']) if any(ev.get('kat') == k for ev in events_dict[curr_dt])), None)
                        if bg_color: ts.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor(bg_color)))

        cal_table.setStyle(TableStyle(ts))
        
        body_table = Table([[sidebar_elements, cal_table]], colWidths=[185, 633])
        body_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'), ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F8FAFC')), ('BOX', (0,0), (0,0), 0.5, colors.HexColor('#CBD5E1')),
            ('LEFTPADDING', (0,0), (0,0), 8), ('RIGHTPADDING', (0,0), (0,0), 8), ('TOPPADDING', (0,0), (0,0), 8), ('BOTTOMPADDING', (0,0), (0,0), 8), ('LEFTPADDING', (1,0), (1,0), 6),
        ]))
        
        story.extend([body_table, Spacer(1, 4)])

        nota_str = " | ".join([f"<b>{dt_ev.strftime('%d/%m/%Y')}</b>: {nama_ev}" for dt_ev, nama_ev in peristiwa_islam_ref.items() if dt_ev.month == m]) or "Tiada Peristiwa Islam Khas Bagi Bulan Ini."
        legend_txt_style = ParagraphStyle('LegTxt', fontName='Helvetica-Bold', fontSize=6.2, textColor=colors.HexColor('#0F172A'))

        story.extend([Paragraph(f"<b>■ Peristiwa Kebesaran Islam:</b> {nota_str}", ParagraphStyle('FootnoteStyle', fontName='Helvetica', fontSize=6.2, textColor=colors.HexColor('#334155'))), Spacer(1, 2)])

        def make_box(color_hex, border_hex, is_red=False):
            t = Table([['']], colWidths=[9], rowHeights=[9])
            t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.white if is_red else colors.HexColor(color_hex)), ('BOX', (0,0), (-1,-1), 0.8 if is_red else 0.4, colors.HexColor(border_hex)), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
            return t

        legend_row = [
            Paragraph("<b>Petunjuk Warna (Legend):</b>", legend_txt_style),
            make_box('#FEF08A', '#CA8A04'), Paragraph("Cuti Penggal KPM", legend_txt_style),
            make_box('#BAE6FD', '#0284C7'), Paragraph("Cuti Perayaan KPM", legend_txt_style),
            make_box('#86EFAC', '#16A34A'), Paragraph("Aktiviti TASKI", legend_txt_style),
            make_box('#FBCFE8', '#DB2777'), Paragraph("Cuti Peristiwa TASKI", legend_txt_style),
            make_box('', '#DC2626', True), Paragraph("Tarikh Merah: Cuti Umum / Ahad", legend_txt_style)
        ]

        legend_table = Table([legend_row], colWidths=[110, 15, 85, 15, 90, 15, 75, 15, 95, 15, 135])
        legend_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 2), ('RIGHTPADDING', (0,0), (-1,-1), 2)]))
        story.extend([legend_table, Spacer(1, 4), Paragraph("Hakcipta Terpelihara © Sazahlie S. | <i>Penafian: Kalendar ini dijana secara automatik. Tarikh Hijrah adalah anggaran dan tertakluk kepada perubahan pengisytiharan rasmi Penyimpan Mohor Besar Raja-Raja Malaysia. Maklumat Cuti KPM/Negeri adalah sebagai panduan semata-mata.</i>", pdf_disclaimer_style)])

        if m != months_to_render[-1]: story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -------------------------------------------------------------
# FUNGSI PENJANAAN PDF POSTER TAHUNAN 12 BULAN (FIT TO A4 PERFECT)
# -------------------------------------------------------------
def generate_pdf_yearly_poster_bytes(n_sekolah, alamat, daerah, neg_pilihan, tel, thn, raw_logo_bytes, events_dict, cuti_umum_ref, peristiwa_islam_ref, is_kump_a, offset_hj):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        rightMargin=8, leftMargin=8, topMargin=8, bottomMargin=8,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitleYear', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#064E3B'), alignment=1, leading=13)
    subtitle_style = ParagraphStyle('DocSubTitleYear', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.HexColor('#0284C7'), alignment=1, leading=9)

    story = []

    # PENGEPALA POSTER TENGAH ATAS
    header_text_cells = []
    if raw_logo_bytes:
        try:
            rl_img = RLImage(io.BytesIO(raw_logo_bytes), width=40, height=40)
            header_text_cells.append(rl_img)
            header_text_cells.append(Spacer(1, 2))
        except Exception: pass

    header_text_cells.extend([
        Paragraph(f"<b>{n_sekolah.upper()}</b>", title_style),
        Spacer(1, 1),
        Paragraph(f"TAKWIM PERSEKOLAHAN & KALENDAR HIJRAH TAHUN {thn}", title_style),
        Spacer(1, 1),
        Paragraph(f"ALAMAT: {alamat.upper().replace('\n', ' ')} | NO. TEL: {tel}", subtitle_style)
    ])

    header_table = Table([[header_text_cells]], colWidths=[812])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))

    mini_tables = []
    for m in range(1, 13):
        m_name = SENARAI_BULAN_MASIHI[m]
        cal = calendar.monthcalendar(thn, m)
        
        d_first = date(thn, m, 1)
        _, m_h_first, y_h_first = gregorian_to_hijri(d_first, offset_hj)
        d_last = date(thn, m, calendar.monthrange(thn, m)[1])
        _, m_h_last, y_h_last = gregorian_to_hijri(d_last, offset_hj)
        
        hijri_sub = f"{m_h_first[:3]} - {m_h_last[:3]} {y_h_last}H" if m_h_first != m_h_last else f"{m_h_first} {y_h_first}H"

        m_data = [[Paragraph(f"<b>{m_name}</b><br/><font size=5 color='#fef3c7'>{hijri_sub}</font>", ParagraphStyle('MH', fontName='Helvetica-Bold', fontSize=6.5, alignment=1, leading=7.5, textColor=colors.white))]]
        m_data.append([
            Paragraph("<b>A</b>", ParagraphStyle('DH', fontName='Helvetica-Bold', fontSize=6, alignment=1, textColor=colors.HexColor('#DC2626'))),
            Paragraph("<b>I</b>", ParagraphStyle('DH', fontName='Helvetica-Bold', fontSize=6, alignment=1)),
            Paragraph("<b>S</b>", ParagraphStyle('DH', fontName='Helvetica-Bold', fontSize=6, alignment=1)),
            Paragraph("<b>R</b>", ParagraphStyle('DH', fontName='Helvetica-Bold', fontSize=6, alignment=1)),
            Paragraph("<b>K</b>", ParagraphStyle('DH', fontName='Helvetica-Bold', fontSize=6, alignment=1)),
            Paragraph("<b>J</b>", ParagraphStyle('DH', fontName='Helvetica-Bold', fontSize=6, alignment=1, textColor=colors.HexColor('#0284C7') if is_kump_a else colors.black)),
            Paragraph("<b>S</b>", ParagraphStyle('DH', fontName='Helvetica-Bold', fontSize=6, alignment=1))
        ])

        for week in cal:
            row_w = []
            for day_idx, day in enumerate(week):
                if day == 0:
                    row_w.append("")
                else:
                    dt = date(thn, m, day)
                    h_d, _, _ = gregorian_to_hijri(dt, offset_hj)
                    is_sun = (day_idx == 0)
                    is_fri = (day_idx == 5) if is_kump_a else False
                    is_u = dt in cuti_umum_ref
                    
                    txt_c = "#DC2626" if (is_sun or is_fri or is_u) else "#0F172A"
                    cell_text = f"<font color='{txt_c}'><b>{day}</b></font><br/><font color='#64748B' size=4.5>{h_d}H</font>"
                    p_day = Paragraph(cell_text, ParagraphStyle('DCell', fontName='Helvetica', fontSize=6, leading=6.5, alignment=1))
                    row_w.append(p_day)
            m_data.append(row_w)

        ts_mini = [
            ('SPAN', (0,0), (6,0)),
            ('BACKGROUND', (0,0), (6,0), colors.HexColor('#064E3B')),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F1F5F9')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#CBD5E1')),
            ('LEFTPADDING', (0,0), (-1,-1), 0.5),
            ('RIGHTPADDING', (0,0), (-1,-1), 0.5),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]

        for r_i, week in enumerate(cal, start=2):
            for c_i, day in enumerate(week):
                if day != 0:
                    dt = date(thn, m, day)
                    if dt in events_dict:
                        bg = None
                        for ev in events_dict[dt]:
                            k = ev.get('kat')
                            if k == "penggal": bg = '#FEF08A'
                            elif k == "perayaan": bg = '#BAE6FD'
                            elif k == "peristiwa": bg = '#FBCFE8'
                            elif k == "aktiviti" and not bg: bg = '#86EFAC'
                        if bg:
                            ts_mini.append(('BACKGROUND', (c_i, r_i), (c_i, r_i), colors.HexColor(bg)))

        t_m = Table(m_data, colWidths=[19.5]*7)
        t_m.setStyle(TableStyle(ts_mini))
        mini_tables.append(t_m)

    grid_matrix = [
        [mini_tables[0], mini_tables[1], mini_tables[2], mini_tables[3]],
        [mini_tables[4], mini_tables[5], mini_tables[6], mini_tables[7]],
        [mini_tables[8], mini_tables[9], mini_tables[10], mini_tables[11]]
    ]

    yearly_grid_table = Table(grid_matrix, colWidths=[138]*4)
    yearly_grid_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 1),
        ('RIGHTPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))

    # Panel Catatan
    all_year_events = []
    for m in range(1, 13):
        for d in range(1, calendar.monthrange(thn, m)[1] + 1):
            dt_ev = date(thn, m, d)
            if dt_ev in events_dict:
                for e in events_dict[dt_ev]:
                    all_year_events.append({'date': dt_ev, 'nama': e['nama'], 'kat': e['kat']})

    panel_items = []
    pp_year = {}
    for ev in all_year_events:
        if ev['kat'] in ['penggal', 'perayaan']:
            pp_year.setdefault(ev['nama'], []).append(ev['date'])
    for ename, dates in pp_year.items():
        dates.sort()
        d_str = f"{dates[0].strftime('%d/%m')} - {dates[-1].strftime('%d/%m')}" if len(dates) > 1 else f"{dates[0].strftime('%d/%m')}"
        panel_items.append({'date_sort': dates[0], 'text': f"<b>{d_str}</b>: {ename}"})

    uap_year = {}
    for ev in all_year_events:
        if ev['kat'] in ['umum', 'aktiviti', 'peristiwa']:
            uap_year.setdefault(ev['nama'], []).append(ev['date'])
    for ename, dates in uap_year.items():
        dates.sort()
        streak = 1
        for i, dt in enumerate(dates):
            if i > 0 and (dt - dates[i-1]).days == 1: streak += 1
            else: streak = 1
            suffix = " (H2)" if streak == 2 else " (H3)" if streak == 3 else ""
            disp = ename + suffix if streak > 1 and "Hari Ke" not in ename and "Gantian" not in ename else ename
            panel_items.append({'date_sort': dt, 'text': f"<b>{dt.strftime('%d/%m')}</b>: {disp}"})

    panel_items.sort(key=lambda x: x['date_sort'])

    notes_elements = [Paragraph("<b>📝 RINGKASAN CATATAN / PERISTIWA TAHUNAN</b>", ParagraphStyle('p_head', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#064E3B'), alignment=1)), Spacer(1, 4)]
    if panel_items:
        for item in panel_items:
            notes_elements.append(Paragraph(item['text'], ParagraphStyle('p_txt', fontName='Helvetica', fontSize=6.2, leading=7.8, textColor=colors.HexColor('#1E293B'))))
            notes_elements.append(Spacer(1, 2))
    else:
        notes_elements.append(Paragraph("<i>Tiada catatan peristiwa direkodkan.</i>", ParagraphStyle('p_empty', fontName='Helvetica-Oblique', fontSize=6.5, textColor=colors.HexColor('#64748B'))))

    notes_panel_table = Table([[notes_elements]], colWidths=[260])
    notes_panel_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    main_poster_table = Table([[yearly_grid_table, notes_panel_table]], colWidths=[552, 260])
    main_poster_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))

    story.append(main_poster_table)
    story.append(Spacer(1, 4))

    legend_txt_style = ParagraphStyle('LegTxtY', fontName='Helvetica-Bold', fontSize=6.5, textColor=colors.HexColor('#0F172A'))
    
    def make_box_y(color_hex, border_hex, is_red=False):
        t = Table([['']], colWidths=[9], rowHeights=[9])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.white if is_red else colors.HexColor(color_hex)),
            ('BOX', (0,0), (-1,-1), 0.8 if is_red else 0.4, colors.HexColor(border_hex)),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0)
        ]))
        return t

    legend_row = [
        Paragraph("<b>Petunjuk Warna (Legend):</b>", legend_txt_style),
        make_box_y('#FEF08A', '#CA8A04'), Paragraph("Cuti Penggal KPM", legend_txt_style),
        make_box_y('#BAE6FD', '#0284C7'), Paragraph("Cuti Perayaan KPM", legend_txt_style),
        make_box_y('#86EFAC', '#16A34A'), Paragraph("Aktiviti TASKI", legend_txt_style),
        make_box_y('#FBCFE8', '#DB2777'), Paragraph("Cuti Peristiwa TASKI", legend_txt_style),
        make_box_y('', '#DC2626', True), Paragraph("Tarikh Merah: Cuti Umum / Ahad", legend_txt_style)
    ]

    legend_table = Table([legend_row], colWidths=[110, 15, 85, 15, 90, 15, 75, 15, 95, 15, 135])
    legend_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    
    story.append(legend_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph("Hakcipta Terpelihara © Sazahlie S. | <i>Penafian: Poster Takwim Tahunan ini dijana secara automatik sebagai rujukan ringkas. Sila rujuk kalendar bulanan rasmi untuk perincian harian.</i>", ParagraphStyle('PdfDisclaimerY', fontName='Helvetica', fontSize=6, textColor=colors.HexColor('#64748B'), alignment=1)))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -------------------------------------------------------------
# STRUKTUR 3 TAB UTAMA
# -------------------------------------------------------------
tab_profil, tab_muat_naik, tab_kalendar = st.tabs([
    "🕌 Laman Utama & Profil",
    "📄 Muat Naik PDF KPM",
    "📅 Urus & Cetak Kalendar"
])

# =============================================================
# TAB 1: LAMAN UTAMA & PROFIL TASKI
# =============================================================
with tab_profil:
    st.markdown("<br>", unsafe_allow_html=True)
    col_profil_1, col_profil_2 = st.columns(2, gap="large")
    
    map_negeri_holidays = {
        "Johor": "JHR", "Kedah": "KDH", "Kelantan": "KTN", "Melaka": "MLK",
        "Negeri Sembilan": "NSN", "Pahang": "PHG", "Perak": "PRK", "Perlis": "PLS",
        "Pulau Pinang": "PNG", "Sabah": "SBH", "Sarawak": "SRW", "Selangor": "SGR",
        "Terengganu": "TRG", "W.P. Kuala Lumpur": "KUL", "W.P. Labuan": "LBN", "W.P. Putrajaya": "PJY",
    }
    senarai_negeri = list(map_negeri_holidays.keys())

    with col_profil_1:
        st.markdown('''<div class="profile-card"><h3>🏫 Maklumat Institusi</h3></div>''', unsafe_allow_html=True)
        nama_sekolah = st.text_input("Nama TASKI ABIM:", value="TASKI ABIM SANDAKAN")
        alamat_sekolah = st.text_area("Alamat Penuh:", value="PETI SURAT 2900, 90372 SANDAKAN", height=105)
        
        c_daerah, c_tel = st.columns(2)
        with c_daerah: daerah_sekolah = st.text_input("Daerah:", value="Sandakan")
        with c_tel: no_tel_sekolah = st.text_input("No. Perhubungan:", value="089-223573 / +60 13-884 7376")

    with col_profil_2:
        st.markdown('''<div class="profile-card"><h3>⚙️ Tetapan Takwim & Kalendar</h3></div>''', unsafe_allow_html=True)
        kumpulan_pilihan = st.selectbox(
            "Kumpulan Kalendar KPM (Wajib):",
            [
                "Kumpulan B (Melaka, N. Sembilan, Pahang, Perak, Perlis, P. Pinang, Sabah, Sarawak, Selangor, W.P.)",
                "Kumpulan A (Kedah, Kelantan, Terengganu, Johor)"
            ], index=0
        )
        is_kumpulan_a = "Kumpulan A" in kumpulan_pilihan
        negeri_pilihan = st.selectbox("Cuti Umum Negeri Pilihan:", senarai_negeri, index=senarai_negeri.index("Sabah"))
        
        st.markdown("---")
        st.caption("🌙 **Kalibrasi Tarikh Hijrah (Berdasarkan JAKIM)**")
        hijri_offset = st.number_input("Pelarasan Hijrah (± Hari):", min_value=-2, max_value=2, value=0)

# =============================================================
# TAB 2: MUAT NAIK PDF KPM
# =============================================================
with tab_muat_naik:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Muat Naik Takwim Akademik KPM")
    st.write("Sila muat naik fail PDF Kalendar Persekolahan rasmi KPM untuk mengekstrak data cuti penggal dan perayaan secara automatik.")
    
    uploaded_file = st.file_uploader("Muat Naik Fail PDF KPM di sini:", type=["pdf"])

    if uploaded_file is not None:
        try:
            reader = pypdf.PdfReader(uploaded_file)
            extracted_text_temp = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted: extracted_text_temp += extracted + "\n"
            
            st.session_state["pdf_text_extracted"] = extracted_text_temp
            pdf_text = extracted_text_temp
            
            match_tahun = re.search(r"TAHUN\s+(\d{4})", pdf_text, re.IGNORECASE)
            if match_tahun: tahun_detected = int(match_tahun.group(1))
            st.success(f"✅ Fail PDF '{uploaded_file.name}' berjaya diekstrak bagi Tahun {tahun_detected}!")
        except Exception as e:
            st.error(f"❌ Ralat memproses PDF: {e}")
    else:
        st.info("ℹ️ Menunggu fail PDF KPM dimuat naik. Sistem akan menggunakan tarikh anggaran (default) sekiranya tiada muat naik dibuat.")

tahun = tahun_detected
tarikh_mula = date(tahun, 1, 4)

cuti_penggal_kpm = []
cuti_perayaan_kpm = []

if pdf_text:
    def standardize_malay_dates(text, current_year):
        months_map = {
            "januari": "01", "jan": "01", "februari": "02", "feb": "02",
            "mac": "03", "march": "03", "april": "04", "apr": "04",
            "mei": "05", "may": "05", "jun": "06", "june": "06",
            "julai": "07", "july": "07", "ogos": "08", "august": "08", "aug": "08",
            "september": "09", "sep": "09", "oktober": "10", "october": "10", "okt": "10", "oct": "10",
            "november": "11", "nov": "11", "disember": "12", "december": "12", "dis": "12", "dec": "12"
        }
        pattern_text = r"(\d{1,2})\s+([a-zA-Z]+)\s*(\d{4})?\s*[-–thingga]+\s*(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})"
        
        def replace_date(match):
            d1, m1_str, y1, d2, m2_str, y2 = match.groups()
            m1 = months_map.get(m1_str.lower(), "01")
            m2 = months_map.get(m2_str.lower(), "01")
            y1 = y1 if y1 else y2
            return f"{int(d1):02d}-{m1}-{y1} hingga {int(d2):02d}-{m2}-{y2}"

        return re.sub(pattern_text, replace_date, text, flags=re.IGNORECASE)

    pdf_text_std = standardize_malay_dates(pdf_text, tahun)
    date_pattern_num = r"(\d{2}[\./-]\d{2}[\./-]\d{4})\s*[-–thingga]+\s*(\d{2}[\./-]\d{2}[\./-]\d{4})"
    matches_num = re.findall(date_pattern_num, pdf_text_std)
    
    nama_cuti_standard = ["CUTI PENGGAL 1", "CUTI PERTENGAHAN PENGGAL", "CUTI PENGGAL 2", "CUTI AKHIR PERSEKOLAHAN"]
    seen_dates = set()
    label_idx = 0
    
    if matches_num:
        for str_mula, str_tamat in matches_num:
            try:
                d_mula = datetime.strptime(re.sub(r'[\./]', '-', str_mula), "%d-%m-%Y").date()
                d_tamat = datetime.strptime(re.sub(r'[\./]', '-', str_tamat), "%d-%m-%Y").date()
                if (d_mula, d_tamat) not in seen_dates:
                    seen_dates.add((d_mula, d_tamat))
                    nama_lbl = nama_cuti_standard[label_idx] if label_idx < len(nama_cuti_standard) else f"CUTI PENGGAL {label_idx+1}"
                    cuti_penggal_kpm.append((d_mula, d_tamat, nama_lbl))
                    label_idx += 1
            except ValueError: pass

if len(cuti_penggal_kpm) < 3:
    if is_kumpulan_a:
        cuti_penggal_kpm = [(date(tahun, 3, 5), date(tahun, 3, 13), "CUTI PENGGAL 1"), (date(tahun, 5, 21), date(tahun, 6, 5), "CUTI PERTENGAHAN PENGGAL"), (date(tahun, 8, 27), date(tahun, 9, 4), "CUTI PENGGAL 2"), (date(tahun, 12, 3), date(tahun, 12, 31), "CUTI AKHIR PERSEKOLAHAN")]
        cuti_perayaan_kpm = [(date(tahun, 2, 8), date(tahun, 2, 10), "CUTI PERAYAAN - TAHUN BAHARU CINA"), (date(tahun, 5, 16), date(tahun, 5, 19), "CUTI PERAYAAN - HARI RAYA AIDILADHA"), (date(tahun, 10, 27), date(tahun, 10, 28), "CUTI PERAYAAN - HARI DEEPAVALI")]
    else:
        cuti_penggal_kpm = [(date(tahun, 3, 6), date(tahun, 3, 14), "CUTI PENGGAL 1"), (date(tahun, 5, 22), date(tahun, 6, 6), "CUTI PERTENGAHAN PENGGAL"), (date(tahun, 8, 28), date(tahun, 9, 5), "CUTI PENGGAL 2"), (date(tahun, 12, 4), date(tahun, 12, 31), "CUTI AKHIR PERSEKOLAHAN")]
        cuti_perayaan_kpm = [(date(tahun, 2, 5), date(tahun, 2, 12), "CUTI PERAYAAN - TAHUN BAHARU CINA"), (date(tahun, 5, 18), date(tahun, 5, 19), "CUTI PERAYAAN - HARI RAYA AIDILADHA"), (date(tahun, 10, 27), date(tahun, 10, 29), "CUTI PERAYAAN - HARI DEEPAVALI")]

kod_subdiv = map_negeri_holidays.get(negeri_pilihan, "SBH")
cuti_google_cal = holidays.Malaysia(years=tahun, subdiv=kod_subdiv)
cuti_umum_dates = set(cuti_google_cal.keys())
peristiwa_islam_non_holiday = get_islamic_events_non_holiday(tahun, hijri_offset)

KAT_MAP = {"Aktiviti TASKI": "aktiviti", "Cuti Peristiwa TASKI": "peristiwa", "Cuti Penggal": "penggal", "Cuti Perayaan": "perayaan"}

data_rows = []
for w in range(1, 53):
    mula_dt = tarikh_mula + timedelta(weeks=w - 1)
    tamat_dt = mula_dt + timedelta(days=4)
    catatan_list = []
    kat_def = None

    for c_mula, c_tamat, c_nama in cuti_penggal_kpm:
        if not (c_tamat < mula_dt or c_mula > tamat_dt):
            catatan_list.append(c_nama)
            kat_def = "Cuti Penggal"
            break

    for p_mula, p_tamat, p_nama in cuti_perayaan_kpm:
        if not (p_tamat < mula_dt or p_mula > tamat_dt):
            if p_nama not in catatan_list: catatan_list.append(p_nama)
            kat_def = "Cuti Perayaan"

    curr = mula_dt
    while curr <= tamat_dt:
        if curr in cuti_google_cal:
            u_nama = cuti_google_cal[curr]
            if u_nama not in catatan_list: catatan_list.append(u_nama)
        curr += timedelta(days=1)

    if w == 1 and not catatan_list: catatan_list.append("Minggu Suai Kenal / Transisi")

    data_rows.append({
        "Bulan": mula_dt.strftime("%B %Y"), "Tarikh Mula": mula_dt.strftime("%d/%m/%Y"),
        "Tarikh Akhir": tamat_dt.strftime("%d/%m/%Y"), "Kategori Minggu / Peristiwa": kat_def if kat_def else "",
        "Catatan / Peristiwa": "\n".join(catatan_list),
    })

if "df_master" not in st.session_state or st.session_state.get("current_tahun") != tahun:
    st.session_state["df_master"] = pd.DataFrame(data_rows)
    st.session_state["current_tahun"] = tahun

with tab_muat_naik:
    if uploaded_file is not None:
        st.markdown("---")
        st.markdown("#### 📌 Jadual Hasil Ekstrak Takwim KPM & Cuti Negeri:")
        st.dataframe(st.session_state["df_master"][["Tarikh Mula", "Tarikh Akhir", "Catatan / Peristiwa"]], use_container_width=True, height=400)

if "df_custom_events" not in st.session_state:
    st.session_state["df_custom_events"] = pd.DataFrame(columns=["Tarikh Mula", "Tarikh Akhir", "Kategori Minggu / Peristiwa", "Catatan / Peristiwa"])

df_input = st.session_state["df_master"]
df_custom = st.session_state["df_custom_events"]

def build_dynamic_events_map(df_curr, df_custom_curr, cuti_google_cal_ref, cuti_penggal_ref, cuti_perayaan_ref):
    ev_map = {}
    for u_dt, u_nama in cuti_google_cal_ref.items(): ev_map.setdefault(u_dt, []).append({"nama": u_nama, "kat": "umum"})
    for c_mula, c_tamat, c_nama in cuti_penggal_ref:
        curr = c_mula
        while curr <= c_tamat: ev_map.setdefault(curr, []).append({"nama": c_nama, "kat": "penggal"}); curr += timedelta(days=1)
    for p_mula, p_tamat, p_nama in cuti_perayaan_ref:
        curr = p_mula
        while curr <= p_tamat: ev_map.setdefault(curr, []).append({"nama": p_nama, "kat": "perayaan"}); curr += timedelta(days=1)

    for _, row in df_custom_curr.iterrows():
        try:
            d_mula = row["Tarikh Mula"] if isinstance(row["Tarikh Mula"], date) else datetime.strptime(str(row["Tarikh Mula"]), "%d/%m/%Y").date()
            d_tamat = row["Tarikh Akhir"] if isinstance(row["Tarikh Akhir"], date) else datetime.strptime(str(row["Tarikh Akhir"]), "%d/%m/%Y").date()
            txt_catatan = str(row["Catatan / Peristiwa"]).strip()
            kat_code = KAT_MAP.get(row["Kategori Minggu / Peristiwa"], "aktiviti")

            if txt_catatan:
                curr = d_mula
                while curr <= d_tamat:
                    if txt_catatan not in [e["nama"] for e in ev_map.get(curr, [])]: ev_map.setdefault(curr, []).append({"nama": txt_catatan, "kat": kat_code})
                    curr += timedelta(days=1)
        except Exception: pass

    return ev_map

# =============================================================
# TAB 3: URUS PROGRAM & CETAK KALENDAR TASKI
# =============================================================
with tab_kalendar:
    st.markdown(f"### 📅 Urus Takwim & Cetak Kalendar TASKI ({tahun})")
    
    bulan_list = [
        ("Januari", 1), ("Februari", 2), ("Mac", 3), ("April", 4),
        ("Mei", 5), ("Jun", 6), ("Julai", 7), ("Ogos", 8),
        ("September", 9), ("Oktober", 10), ("November", 11), ("Disember", 12)
    ]

    tab_names = [b[0] for b in bulan_list]
    month_tabs = st.tabs(tab_names)

    events_by_date_dynamic = build_dynamic_events_map(df_input, df_custom, cuti_google_cal, cuti_penggal_kpm, cuti_perayaan_kpm)
    logo_b64_str = base64.b64encode(logo_bytes).decode() if logo_bytes else ""

    for i, month_tab in enumerate(month_tabs):
        selected_month_name, selected_month_num = bulan_list[i]
        
        with month_tab:
            
            c_btn1, c_btn2 = st.columns([1, 1], gap="medium")
            
            with c_btn1:
                pdf_data_monthly = generate_pdf_monthly_wall_bytes(
                    nama_sekolah, alamat_sekolah, daerah_sekolah, negeri_pilihan, no_tel_sekolah, 
                    tahun, logo_bytes, events_by_date_dynamic, cuti_umum_dates, peristiwa_islam_non_holiday, is_kumpulan_a, hijri_offset, specific_month=selected_month_num
                )
                nama_bulan_semasa = SENARAI_BULAN_MASIHI[selected_month_num]
                st.download_button(
                    label=f"🖨️ Muat Turun Cetakan Kalendar Bulan {nama_bulan_semasa} (.PDF)",
                    data=pdf_data_monthly,
                    file_name=f"Kalendar_TASKI_{nama_bulan_semasa}_{tahun}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                    key=f"print_btn_monthly_{selected_month_num}"
                )

            with c_btn2:
                pdf_data_yearly = generate_pdf_yearly_poster_bytes(
                    nama_sekolah, alamat_sekolah, daerah_sekolah, negeri_pilihan, no_tel_sekolah,
                    tahun, logo_bytes, events_by_date_dynamic, cuti_umum_dates, peristiwa_islam_non_holiday, is_kumpulan_a, hijri_offset
                )
                st.download_button(
                    label=f"🖼️ Muat Turun Poster Takwim 12 Bulan + Hijrah (.PDF)",
                    data=pdf_data_yearly,
                    file_name=f"Takwim_Poster_12Bulan_TASKI_{tahun}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"print_btn_yearly_{selected_month_num}"
                )

            cal_html_data = render_monthly_wall_calendar(
                tahun, selected_month_num, events_by_date_dynamic, cuti_umum_dates, is_kumpulan_a,
                nama_sekolah, alamat_sekolah, no_tel_sekolah, logo_b64_str, hijri_offset
            )
            components.html(cal_html_data, height=750, scrolling=True)

            st.markdown("---")
            
            st.markdown(f"#### ➕ Kunci Masuk Aktiviti / Program TASKI ({nama_bulan_semasa} {tahun})")
            st.caption("Gunakan bahagian ini untuk menambah program 1 hari (cth: Sabtu/Ahad) atau aktiviti khas di dalam kalendar:")
            
            with st.form(key=f"form_add_event_{selected_month_num}"):
                c1, c2, c3, c4 = st.columns([2, 2, 3, 4])
                with c1: dt_single = st.date_input("Tarikh Program:", value=date(tahun, selected_month_num, 15))
                with c2: dt_single_end = st.date_input("Tarikh Akhir (Jika >1 hari):", value=dt_single)
                with c3: kat_single = st.selectbox("Kategori:", ["Aktiviti TASKI", "Cuti Peristiwa TASKI"])
                with c4: nama_single = st.text_input("Nama Aktiviti / Program:", placeholder="Cth: Hari Sukan TASKI / Gotong Royong")
                
                if st.form_submit_button("➕ Kunci Masuk Program Ke Kalendar", use_container_width=True) and nama_single.strip():
                    new_row = pd.DataFrame([{
                        "Tarikh Mula": dt_single.strftime("%d/%m/%Y"), "Tarikh Akhir": dt_single_end.strftime("%d/%m/%Y"),
                        "Kategori Minggu / Peristiwa": kat_single, "Catatan / Peristiwa": nama_single.strip()
                    }])
                    st.session_state["df_custom_events"] = pd.concat([st.session_state["df_custom_events"], new_row], ignore_index=True)
                    st.success(f"✅ Program '{nama_single}' berjaya dikunci masuk untuk tarikh {dt_single.strftime('%d/%m/%Y')}!")
                    st.rerun()

            if not st.session_state["df_custom_events"].empty:
                st.caption("📋 **Senarai Program Harian / Tarikh Spesifik Yang Dikunci Masuk:**")
                st.dataframe(
                    st.session_state["df_custom_events"],
                    column_config={
                        "Tarikh Mula": st.column_config.Column("Tarikh Mula", width="small"),
                        "Tarikh Akhir": st.column_config.Column("Tarikh Akhir", width="small"),
                        "Kategori Minggu / Peristiwa": st.column_config.Column("Kategori", width="medium"),
                        "Catatan / Peristiwa": st.column_config.Column("Catatan / Peristiwa", width="large")
                    }, use_container_width=True
                )
                if st.button("🗑️ Padam Semua Aktiviti Harian Khas", key=f"btn_del_{selected_month_num}"):
                    st.session_state["df_custom_events"] = pd.DataFrame(columns=["Tarikh Mula", "Tarikh Akhir", "Kategori Minggu / Peristiwa", "Catatan / Peristiwa"])
                    st.rerun()

df_final_master = st.session_state["df_master"][["Tarikh Mula", "Tarikh Akhir", "Kategori Minggu / Peristiwa", "Catatan / Peristiwa"]].copy()
if not st.session_state["df_custom_events"].empty:
    df_final = pd.concat([df_final_master, st.session_state["df_custom_events"]], ignore_index=True)

# Footer Laman Web & Penafian Rasmi
st.markdown("---")
st.markdown(
    f'''
    <div style="text-align: center; font-size: 12px; color: #6c757d; padding: 10px 0;">
        {footer_logo_html}
        <p style="margin-bottom: 4px;">🔒 <b>Hakcipta Terpelihara © Sazahlie S.</b> | 📧 E-mel: <a href="mailto:sazahlie@gmail.com" style="color: #0d6efd; text-decoration: none; font-weight: 600;">sazahlie@gmail.com</a> | 🏷️ Versi: <code>v{APP_VERSION}</code> (Kemaskini: {LAST_UPDATED_DATE})</p>
        <p style="margin: 0; font-size: 11px; color: #8c959f;"><i>Penafian: Perisian ini merupakan alat pengurusan takwim persendirian dan TIDAK mempunyai hubungan terus dengan mana-mana agensi kerajaan. Tarikh Hijrah berkalibrasi adalah tertakluk kepada pengisytiharan rasmi JAKIM & Penyimpan Mohor Besar Raja-Raja.</i></p>
    </div>
    ''',
    unsafe_allow_html=True
)