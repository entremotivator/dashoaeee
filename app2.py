import streamlit as st
import csv
import io
from datetime import date
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="C. Stumpo Development — Construction Estimate",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Hide Streamlit chrome ─────────────────────────────── */
#MainMenu, header, footer,
.stDeployButton,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
button[title="View fullscreen"] { display: none !important; visibility: hidden !important; }

/* ── Palette ───────────────────────────────────────────── */
:root {
    --gold:     #B8972A;
    --gold-lt:  #D4AF45;
    --dark:     #1A1A1A;
    --charcoal: #2C2C2C;
    --slate:    #4A4A4A;
    --cream:    #F5F0E8;
    --white:    #FFFFFF;
}

/* ── Base ──────────────────────────────────────────────── */
html, body, .stApp { background-color: var(--cream) !important; }
.block-container { padding: 0 0 4rem 0 !important; max-width: 100% !important; }

/* ── Brand header ──────────────────────────────────────── */
.brand-header {
    background: linear-gradient(160deg, #0e0e0e 0%, #2a2a2a 100%);
    border-bottom: 3px solid var(--gold);
    padding: 1.4rem 1.6rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    flex-wrap: wrap;
    margin-bottom: 0;
}
.brand-mark {
    width: 56px; height: 56px; min-width: 56px;
    background: var(--gold);
    display: flex; align-items: center; justify-content: center;
    font-family: Georgia, serif; font-size: 1.7rem; font-weight: 700;
    color: var(--dark); border-radius: 2px; flex-shrink: 0;
    letter-spacing: -0.02em;
}
.brand-copy { flex: 1; min-width: 160px; }
.brand-copy h1 {
    font-family: Georgia, serif;
    font-size: clamp(1.1rem, 3.5vw, 1.9rem);
    font-weight: 700; letter-spacing: 0.07em;
    text-transform: uppercase; margin: 0 0 3px;
    color: var(--gold-lt); line-height: 1.1;
}
.brand-copy .tag {
    font-size: clamp(0.6rem, 1.8vw, 0.76rem);
    letter-spacing: 0.18em; text-transform: uppercase;
    color: #888; margin: 0;
}
.brand-contact {
    text-align: right; flex-shrink: 0;
    font-family: Georgia, serif;
    font-style: italic; color: #C8A84C;
    font-size: clamp(0.6rem, 1.5vw, 0.74rem);
    line-height: 1.8;
}
@media (max-width: 600px) { .brand-contact { display: none; } }

/* ── Section headers ───────────────────────────────────── */
.sec-hdr {
    display: flex; align-items: center; gap: 0.6rem;
    background: var(--dark);
    border-left: 5px solid var(--gold);
    padding: 0.7rem 1.2rem;
    margin: 1.2rem 0 0 0;
}
.sec-hdr .icon { font-size: 1rem; line-height: 1; }
.sec-hdr .title {
    font-family: Georgia, serif;
    font-size: clamp(0.72rem, 2vw, 0.88rem);
    font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--gold-lt);
    flex: 1;
}
.sec-hdr .rule {
    flex: 1; max-width: 120px; height: 1px;
    background: linear-gradient(to right, var(--gold), transparent);
    opacity: 0.45;
}
.sec-body {
    background: var(--white);
    padding: 0.9rem 1.2rem 1.1rem;
    border-bottom: 1px solid #E0D5BF;
}

/* ── Grid col headers ──────────────────────────────────── */
.col-hdr {
    font-family: Georgia, serif;
    font-size: 0.68rem; font-weight: 700;
    color: var(--slate); letter-spacing: 0.1em;
    text-transform: uppercase;
    border-bottom: 2px solid var(--gold);
    padding-bottom: 0.35rem; margin-bottom: 0.3rem;
}

/* ── Inputs ────────────────────────────────────────────── */
.stTextInput > label, .stNumberInput > label,
.stTextArea > label, .stSelectbox > label {
    font-family: Georgia, serif !important;
    font-size: 0.68rem !important; font-weight: 700 !important;
    color: var(--slate) !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
}
.stTextInput input,
.stNumberInput input,
.stNumberInput input[type="number"] {
    border: 1.5px solid #C8A84C !important;
    border-radius: 3px !important;
    background: #FEFCF7 !important;
    color: #000000 !important;
    font-family: Georgia, serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}
.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px rgba(184,151,42,0.2) !important;
    outline: none !important;
}
.stTextArea textarea {
    border: 1.5px solid #C8A84C !important;
    border-radius: 3px !important;
    background: #FEFCF7 !important;
    color: #000000 !important;
    font-family: Georgia, serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}

/* ── Metric ────────────────────────────────────────────── */
[data-testid="stMetricValue"] {
    color: var(--gold-lt) !important;
    font-family: Georgia, serif !important; font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: var(--slate) !important;
    font-family: Georgia, serif !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important; font-size: 0.68rem !important;
}

/* ── Buttons (full-width on mobile) ────────────────────── */
.stDownloadButton > button, .stButton > button {
    background: var(--dark) !important;
    color: var(--gold) !important;
    border: 2px solid var(--gold) !important;
    border-radius: 3px !important;
    font-family: Georgia, serif !important;
    font-size: 0.8rem !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    padding: 0.55rem 1.2rem !important;
    width: 100% !important;
    transition: all 0.18s ease !important;
}
.stDownloadButton > button:hover, .stButton > button:hover {
    background: var(--gold) !important; color: var(--dark) !important;
}

/* ── Totals panel ──────────────────────────────────────── */
.totals-panel {
    background: var(--dark);
    border: 2px solid var(--gold);
    border-radius: 4px;
    padding: 1.3rem 1.2rem;
    margin: 0.5rem 0 0.5rem;
}
.t-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
}
.t-item .lbl {
    font-family: Georgia, serif; font-size: 0.65rem;
    color: #888; letter-spacing: 0.12em; text-transform: uppercase;
    margin-bottom: 3px;
}
.t-item .val {
    font-family: Georgia, serif;
    font-size: clamp(0.95rem, 2.5vw, 1.3rem);
    font-weight: 700; color: var(--gold-lt);
}
.t-grand-row {
    border-top: 1.5px solid var(--gold);
    margin-top: 1rem; padding-top: 1rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
}
.t-item .grand {
    font-size: clamp(1.15rem, 3.5vw, 1.7rem);
    color: var(--gold);
}

/* ── Caption ───────────────────────────────────────────── */
.stCaption p {
    color: var(--slate) !important;
    font-family: Georgia, serif !important; font-style: italic;
}

/* ── Tighten column gaps ───────────────────────────────── */
[data-testid="stHorizontalBlock"] { gap: 0.45rem !important; }
</style>
""", unsafe_allow_html=True)

# ── BRAND HEADER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <div class="brand-mark">CS</div>
    <div class="brand-copy">
        <h1>C. Stumpo Development</h1>
        <p class="tag">Construction Estimate &nbsp;·&nbsp; Excellence in Luxury Building</p>
    </div>
    <div class="brand-contact">
        373 Boylston St (Rte 9 W), Newton MA 02459<br>
        (617) 964-5440 &nbsp;·&nbsp; cstumpodevelopment.com
    </div>
</div>
""", unsafe_allow_html=True)

# ── helper: section header ─────────────────────────────────────────────────────
def sec(icon, title):
    st.markdown(f"""
    <div class="sec-hdr">
        <span class="icon">{icon}</span>
        <span class="title">{title}</span>
        <span class="rule"></span>
    </div>
    """, unsafe_allow_html=True)

# ── PROJECT INFO ───────────────────────────────────────────────────────────────
sec("📋", "Project Information")
st.markdown('<div class="sec-body">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    project_name = st.text_input("Project Name", value="NEIA A Hive")
with c2:
    project_location = st.text_input("Project Location", value="Marlborough MA")
with c3:
    project_date = st.text_input("Date", value=str(date.today().strftime("%-m.%-d.%y")))
st.markdown('</div>', unsafe_allow_html=True)

# ── LINE ITEMS ─────────────────────────────────────────────────────────────────
DEFAULT_ITEMS = [
    ("00", "Government Requirement",        0.0,       ""),
    ("02", "Site Work",                     15825.0,   "Sidewalk to roadway"),
    ("02", "Demolition",                    59121.20,  "Includes allowance for removing existing material"),
    ("03", "Concrete",                      21100.0,   "Sidewalk to roadway"),
    ("04", "Masonry",                       52750.0,   "Allowance for re-pointing leaks"),
    ("05", "Misc. Metals",                  0.0,       ""),
    ("05", "Structural Steel",              31650.0,   "Stairwell rails (2 stairs 1 on each side)"),
    ("06", "Carpentry",                     15825.0,   "In wall blocking bathroom and misc."),
    ("06", "Millwork",                      0.0,       ""),
    ("07", "Moisture and Damproofing",      0.0,       ""),
    ("07", "Roofing",                       259884.48, "Could just be a patching allowance to lower cost"),
    ("07", "Insulation",                    0.0,       ""),
    ("07", "Air and Vapor Barrier",         0.0,       ""),
    ("07", "Joint Sealants",                0.0,       ""),
    ("07", "Applied Fireproofing",          0.0,       ""),
    ("08", "Doors, Frames, Hardware",       79125.0,   ""),
    ("08", "Overhead Doors",                0.0,       ""),
    ("08", "Glass and Glazing",             0.0,       ""),
    ("09", "Drywall/Framing/Insulation",    52939.90,  "Keep as many existing walls as possible, patching, bathrooms"),
    ("09", "Acoustical Ceilings",           50640.0,   "Hallways and bathroom, remainder of the area exposed"),
    ("09", "Flooring",                      180157.08, "LVT to match current Hive and tile in bathroom to match"),
    ("09", "Painting and Coatings",         52987.38,  "Walls and exposed ceilings"),
    ("10", "Misc. Specialties",             10550.0,   "Bathrooms, Fire Extinguishers, corner guards"),
    ("11", "Appliances",                    0.0,       ""),
    ("12", "Signage",                       7912.50,   ""),
    ("12", "Window Treatments",             0.0,       ""),
    ("12", "Window Film",                   0.0,       ""),
    ("14", "Conveying Systems",             21100.0,   "Allowance if you want to upgrade floor or lighting"),
    ("21", "Fire Protection",               76831.69,  "Providing uprights for exposed ceilings"),
    ("22", "Plumbing",                      105500.0,  "New bathroom for campus standards"),
    ("23", "Mechanical",                    581911.63, "Includes $200K for a new air handler unit"),
    ("26", "Electrical",                    369809.15, ""),
    ("27", "Low Voltage",                   68206.98,  "Cameras, door access and low voltage costs"),
    ("",   "ALT/Contingencies",             422765.39, "Design contingency until plans are put together"),
]

if "line_items" not in st.session_state:
    st.session_state.line_items = [list(i) for i in DEFAULT_ITEMS]

sec("🏗️", "Building Construction — CSI Division Line Items")
st.markdown('<div class="sec-body">', unsafe_allow_html=True)

# Column header row
hc = st.columns([1, 3, 2, 4])
hc[0].markdown('<div class="col-hdr">CSI Div</div>', unsafe_allow_html=True)
hc[1].markdown('<div class="col-hdr">Description</div>', unsafe_allow_html=True)
hc[2].markdown('<div class="col-hdr">Sub-Total ($)</div>', unsafe_allow_html=True)
hc[3].markdown('<div class="col-hdr">Notes</div>', unsafe_allow_html=True)

updated_items = []
for i, item in enumerate(st.session_state.line_items):
    c = st.columns([1, 3, 2, 4])
    div  = c[0].text_input("", value=item[0], key=f"div_{i}",  label_visibility="collapsed")
    desc = c[1].text_input("", value=item[1], key=f"desc_{i}", label_visibility="collapsed")
    amt  = c[2].number_input("", value=float(item[2]), min_value=0.0, step=100.0, format="%.2f", key=f"amt_{i}", label_visibility="collapsed")
    note = c[3].text_input("", value=item[3], key=f"note_{i}", label_visibility="collapsed")
    updated_items.append([div, desc, amt, note])

st.session_state.line_items = updated_items

bc1, bc2 = st.columns(2)
with bc1:
    if st.button("＋  Add Line Item"):
        st.session_state.line_items.append(["", "", 0.0, ""])
        st.rerun()
with bc2:
    if st.button("－  Remove Last Row") and len(st.session_state.line_items) > 1:
        st.session_state.line_items.pop()
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── ALLOWANCES ─────────────────────────────────────────────────────────────────
construction_subtotal = sum(r[2] for r in st.session_state.line_items)

sec("📊", "Allowances & Project Subtotal")
st.markdown('<div class="sec-body">', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    site_services = st.number_input("Site Services Subtotal ($)", value=68557.63, step=100.0, format="%.2f")
    site_note = st.text_input("Site Services Note", value="If other projects are going at the same time this would be lower")
with c2:
    gen_conditions = st.number_input("General Conditions Subtotal ($)", value=160191.20, step=100.0, format="%.2f")
    gen_note = st.text_input("General Conditions Note", value="If other projects are going at the same time this would be lower")
with c3:
    project_subtotal = construction_subtotal + site_services + gen_conditions
    st.metric("Project Subtotal", f"${project_subtotal:,.2f}")
st.markdown('</div>', unsafe_allow_html=True)

# ── INSURANCE / FEES ───────────────────────────────────────────────────────────
sec("🛡️", "Insurance, Permits & Fees")
st.markdown('<div class="sec-body">', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    insurance = st.number_input("Insurance ($)", value=54753.76, step=100.0, format="%.2f")
with c2:
    permit = st.number_input("Permit ($)", value=55306.82, step=100.0, format="%.2f")
with c3:
    builders_risk = st.number_input("Builder's Risk ($)", value=33184.09, step=100.0, format="%.2f")
    builders_note = st.text_input("Builder's Risk Note", value="Bentley carrying for now, NEIA can carry")
with c4:
    perf_bond = st.number_input("Payment and Performance Bond ($)", value=0.0, step=100.0, format="%.2f")
st.markdown('</div>', unsafe_allow_html=True)

# ── DESIGN & TOTALS ────────────────────────────────────────────────────────────
sec("✏️", "Design Costs")
st.markdown('<div class="sec-body">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    design_costs = st.number_input("Design Costs ($)", value=90000.0, step=500.0, format="%.2f")
with c2:
    design_notes = st.text_input("Design Notes", value="")
st.markdown('</div>', unsafe_allow_html=True)

# ── ALTERNATE SCENARIOS ────────────────────────────────────────────────────────
sec("🔀", "Alternate Cost Scenarios")
st.markdown('<div class="sec-body">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    without_contingency  = st.number_input("Without Contingency ($)",                                         value=2485820.48, step=100.0, format="%.2f")
    remove_roofing       = st.number_input("Remove Roofing, Add $50K Allowance ($)",                          value=2942760.87, step=100.0, format="%.2f")
with c2:
    bldg_cost_components = st.number_input("Building Costs (Roofing, Stairwell, Masonry, Air Handler) ($)",   value=491534.48,  step=100.0, format="%.2f")
    fitout_without_bldg  = st.number_input("Fitout Without Building Costs ($)",                               value=2507051.39, step=100.0, format="%.2f")
st.markdown('</div>', unsafe_allow_html=True)

# ── TOTALS ─────────────────────────────────────────────────────────────────────
construction_total = project_subtotal + insurance + permit + builders_risk + perf_bond
grand_total        = construction_total + design_costs

sec("💰", "Project Totals")
st.markdown(f"""
<div class="sec-body">
<div class="totals-panel">
    <div class="t-grid">
        <div class="t-item"><div class="lbl">Construction Subtotal</div><div class="val">${construction_subtotal:,.2f}</div></div>
        <div class="t-item"><div class="lbl">Project Subtotal</div><div class="val">${project_subtotal:,.2f}</div></div>
        <div class="t-item"><div class="lbl">Construction Total</div><div class="val">${construction_total:,.2f}</div></div>
        <div class="t-item"><div class="lbl">Design Costs</div><div class="val">${design_costs:,.2f}</div></div>
    </div>
    <div class="t-grand-row">
        <div class="t-item">
            <div class="lbl">Total Construction &amp; Design Costs</div>
            <div class="val grand">${grand_total:,.2f}</div>
        </div>
    </div>
</div>
</div>
""", unsafe_allow_html=True)

# ── EXPORT FUNCTIONS ───────────────────────────────────────────────────────────
def build_csv():
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["C. STUMPO DEVELOPMENT — CONSTRUCTION ESTIMATE"])
    w.writerow(["373 Boylston Street, Newton MA 02459 | (617) 964-5440 | cstumpodevelopment.com"])
    w.writerow([])
    w.writerow(["Project Name:", project_name])
    w.writerow(["Project Location:", project_location])
    w.writerow(["Date:", project_date])
    w.writerow([])
    w.writerow(["--- BUILDING CONSTRUCTION ---"])
    w.writerow(["CSI Division", "Description", "Sub-Total Amount", "Notes"])
    for row in st.session_state.line_items:
        w.writerow([row[0], row[1], f"${row[2]:,.2f}" if row[2] else "-", row[3]])
    w.writerow([])
    w.writerow(["--- ALLOWANCES ---"])
    w.writerow(["Construction Subtotal",      "", f"${construction_subtotal:,.2f}", ""])
    w.writerow(["Site Services Subtotal",     "", f"${site_services:,.2f}",         site_note])
    w.writerow(["General Conditions Subtotal","", f"${gen_conditions:,.2f}",        gen_note])
    w.writerow(["Project Subtotal",           "", f"${project_subtotal:,.2f}",      ""])
    w.writerow([])
    w.writerow(["--- INSURANCE / FEES ---"])
    w.writerow(["Insurance",                    "", f"${insurance:,.2f}",     ""])
    w.writerow(["Permit",                       "", f"${permit:,.2f}",        ""])
    w.writerow(["Builder's Risk",               "", f"${builders_risk:,.2f}", builders_note])
    w.writerow(["Payment and Performance Bond", "", f"${perf_bond:,.2f}",     ""])
    w.writerow([])
    w.writerow(["Construction Total",                    "", f"${construction_total:,.2f}", ""])
    w.writerow(["Design Costs",                          "", f"${design_costs:,.2f}",       design_notes])
    w.writerow(["TOTAL CONSTRUCTION AND DESIGN COSTS",   "", f"${grand_total:,.2f}",        ""])
    w.writerow([])
    w.writerow(["--- ALTERNATE SCENARIOS ---"])
    w.writerow(["Without Contingency",                                          "", f"${without_contingency:,.2f}",  ""])
    w.writerow(["Remove Roofing Add $50K Allowance",                            "", f"${remove_roofing:,.2f}",       ""])
    w.writerow(["Building Costs (Roofing/Stairwell/Masonry/Air Handler)",       "", f"${bldg_cost_components:,.2f}", ""])
    w.writerow(["Fitout Without Building Costs",                                "", f"${fitout_without_bldg:,.2f}",  ""])
    return out.getvalue().encode("utf-8")


def build_pdf():
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(letter),
                            leftMargin=0.5*inch, rightMargin=0.5*inch,
                            topMargin=0.45*inch, bottomMargin=0.45*inch)

    DARK  = colors.HexColor("#1A1A1A")
    GOLD  = colors.HexColor("#B8972A")
    LGOLD = colors.HexColor("#D4AF45")
    CREAM = colors.HexColor("#F5F0E8")
    SLATE = colors.HexColor("#4A4A4A")
    WHITE = colors.white

    def sty(name, **kw):
        return ParagraphStyle(name, **kw)

    title_s  = sty("T",  fontName="Times-Bold",   fontSize=19, textColor=LGOLD, alignment=TA_CENTER)
    sub_s    = sty("S",  fontName="Times-Italic",  fontSize=8,  textColor=colors.HexColor("#999"), alignment=TA_CENTER)
    sec_s    = sty("SE", fontName="Times-Bold",    fontSize=8,  textColor=GOLD,  spaceBefore=7, spaceAfter=3)
    cell_s   = sty("C",  fontName="Times-Roman",   fontSize=8,  textColor=DARK)
    cell_r   = sty("CR", fontName="Times-Roman",   fontSize=8,  textColor=DARK,  alignment=TA_RIGHT)
    note_s   = sty("N",  fontName="Times-Italic",  fontSize=7,  textColor=SLATE)
    hdr_s    = sty("H",  fontName="Times-Bold",    fontSize=8,  textColor=WHITE)
    pi_lbl   = sty("PL", fontName="Times-Bold",    fontSize=8,  textColor=SLATE)
    pi_val   = sty("PV", fontName="Times-Roman",   fontSize=8,  textColor=DARK)

    story = []

    # ── PDF Header ──────────────────────────────────────
    h = Table([[Paragraph("C. STUMPO DEVELOPMENT", title_s)]], colWidths=[10*inch])
    h.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK),("LINEBELOW",(0,0),(-1,-1),2,GOLD),
                            ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    story.append(h)
    s = Table([[Paragraph("Construction Estimate  ·  Excellence in Luxury Home Building  ·  373 Boylston St, Newton MA  ·  (617) 964-5440  ·  cstumpodevelopment.com", sub_s)]], colWidths=[10*inch])
    s.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK),("BOTTOMPADDING",(0,0),(-1,-1),10)]))
    story.append(s)
    story.append(Spacer(1,7))

    # ── Project info ─────────────────────────────────────
    pi = Table([[Paragraph("Project:", pi_lbl), Paragraph(project_name, pi_val),
                 Paragraph("Location:", pi_lbl), Paragraph(project_location, pi_val),
                 Paragraph("Date:", pi_lbl), Paragraph(project_date, pi_val)]],
               colWidths=[0.8*inch, 2.3*inch, 0.8*inch, 2.3*inch, 0.55*inch, 1.25*inch])
    pi.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),CREAM),("LINEBELOW",(0,0),(-1,-1),0.5,GOLD),
                             ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),5)]))
    story.append(pi)
    story.append(Spacer(1,7))

    # ── Line items ───────────────────────────────────────
    story.append(Paragraph("BUILDING CONSTRUCTION — CSI DIVISION LINE ITEMS", sec_s))
    td = [[Paragraph("CSI Div",hdr_s), Paragraph("Description",hdr_s), Paragraph("Sub-Total",hdr_s), Paragraph("Notes",hdr_s)]]
    for row in st.session_state.line_items:
        td.append([Paragraph(str(row[0]),cell_s), Paragraph(str(row[1]),cell_s),
                   Paragraph(f"${row[2]:,.2f}" if row[2] else "—", cell_r), Paragraph(str(row[3]),note_s)])
    mt = Table(td, colWidths=[0.6*inch, 2.5*inch, 1.3*inch, 5.6*inch], repeatRows=1)
    mt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),DARK),("LINEBELOW",(0,0),(-1,0),1.5,GOLD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,CREAM]),
        ("LINEBELOW",(0,1),(-1,-1),0.3,colors.HexColor("#D4B96A")),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("ALIGN",(2,1),(2,-1),"RIGHT"),
    ]))
    story.append(mt)
    story.append(Spacer(1,5))

    # ── Allowances ───────────────────────────────────────
    story.append(Paragraph("ALLOWANCES & PROJECT SUBTOTAL", sec_s))
    bold_s = sty("B", fontName="Times-Bold", fontSize=8, textColor=DARK)
    bold_r = sty("BR", fontName="Times-Bold", fontSize=8, textColor=DARK, alignment=TA_RIGHT)
    at = Table([
        [Paragraph("Construction Subtotal",      cell_s), Paragraph(f"${construction_subtotal:,.2f}", cell_r), Paragraph("", note_s)],
        [Paragraph("Site Services Subtotal",     cell_s), Paragraph(f"${site_services:,.2f}",         cell_r), Paragraph(site_note, note_s)],
        [Paragraph("General Conditions Subtotal",cell_s), Paragraph(f"${gen_conditions:,.2f}",        cell_r), Paragraph(gen_note,  note_s)],
        [Paragraph("Project Subtotal",           bold_s), Paragraph(f"${project_subtotal:,.2f}",      bold_r), Paragraph("", note_s)],
    ], colWidths=[2.5*inch, 1.3*inch, 6.2*inch])
    at.setStyle(TableStyle([("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,CREAM]),
                             ("LINEBELOW",(0,-1),(-1,-1),1.5,GOLD),("LINEBELOW",(0,0),(-1,-2),0.3,colors.HexColor("#D4B96A")),
                             ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                             ("LEFTPADDING",(0,0),(-1,-1),5),("ALIGN",(1,0),(1,-1),"RIGHT")]))
    story.append(at)
    story.append(Spacer(1,4))

    # ── Fees ─────────────────────────────────────────────
    story.append(Paragraph("INSURANCE, PERMITS & FEES", sec_s))
    ft = Table([
        [Paragraph("Insurance",                    cell_s), Paragraph(f"${insurance:,.2f}",     cell_r), Paragraph("", note_s)],
        [Paragraph("Permit",                       cell_s), Paragraph(f"${permit:,.2f}",        cell_r), Paragraph("", note_s)],
        [Paragraph("Builder's Risk",               cell_s), Paragraph(f"${builders_risk:,.2f}", cell_r), Paragraph(builders_note, note_s)],
        [Paragraph("Payment and Performance Bond", cell_s), Paragraph(f"${perf_bond:,.2f}",     cell_r), Paragraph("", note_s)],
    ], colWidths=[2.5*inch, 1.3*inch, 6.2*inch])
    ft.setStyle(TableStyle([("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,CREAM]),
                             ("LINEBELOW",(0,0),(-1,-1),0.3,colors.HexColor("#D4B96A")),
                             ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                             ("LEFTPADDING",(0,0),(-1,-1),5),("ALIGN",(1,0),(1,-1),"RIGHT")]))
    story.append(ft)
    story.append(Spacer(1,4))

    # ── Grand totals ──────────────────────────────────────
    grand_s  = sty("GS",  fontName="Times-Bold", fontSize=11, textColor=DARK)
    grand_sv = sty("GSV", fontName="Times-Bold", fontSize=11, textColor=LGOLD, alignment=TA_RIGHT)
    gtt = Table([
        [Paragraph("Construction Total",                  bold_s), Paragraph(f"${construction_total:,.2f}", bold_r), Paragraph("", note_s)],
        [Paragraph("Design Costs",                        bold_s), Paragraph(f"${design_costs:,.2f}",       bold_r), Paragraph(design_notes, note_s)],
        [Paragraph("TOTAL CONSTRUCTION AND DESIGN COSTS", grand_s),Paragraph(f"${grand_total:,.2f}",        grand_sv),Paragraph("", note_s)],
    ], colWidths=[2.5*inch, 1.3*inch, 6.2*inch])
    gtt.setStyle(TableStyle([("BACKGROUND",(0,2),(-1,2),DARK),
                              ("LINEABOVE",(0,0),(-1,0),1.5,GOLD),("LINEBELOW",(0,1),(-1,1),0.5,GOLD),
                              ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                              ("LEFTPADDING",(0,0),(-1,-1),5),("ALIGN",(1,0),(1,-1),"RIGHT")]))
    story.append(gtt)
    story.append(Spacer(1,5))

    # ── Alternates ────────────────────────────────────────
    story.append(Paragraph("ALTERNATE COST SCENARIOS", sec_s))
    alt = Table([
        [Paragraph("Without Contingency",                                       cell_s), Paragraph(f"${without_contingency:,.2f}",  cell_r)],
        [Paragraph("Remove Roofing, Add $50K Allowance from Overall Cost",      cell_s), Paragraph(f"${remove_roofing:,.2f}",       cell_r)],
        [Paragraph("Cost Associated with Building (Roofing/Stairwell/Masonry/Air Handler)", cell_s), Paragraph(f"${bldg_cost_components:,.2f}", cell_r)],
        [Paragraph("Costs of Fitout Without Building Costs",                    cell_s), Paragraph(f"${fitout_without_bldg:,.2f}",  cell_r)],
    ], colWidths=[8.7*inch, 1.3*inch])
    alt.setStyle(TableStyle([("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,CREAM]),
                              ("LINEBELOW",(0,0),(-1,-1),0.3,colors.HexColor("#D4B96A")),
                              ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                              ("LEFTPADDING",(0,0),(-1,-1),5),("ALIGN",(1,0),(1,-1),"RIGHT")]))
    story.append(alt)

    # ── Footer ────────────────────────────────────────────
    story.append(Spacer(1,10))
    ftr = Table([[Paragraph(
        "C. Stumpo Development, Inc.  ·  373 Boylston Street (Route 9 West), Newton, MA 02459  ·  (617) 964-5440  ·  cstumpodevelopment.com",
        sty("F", fontName="Times-Italic", fontSize=7, textColor=colors.HexColor("#999"), alignment=TA_CENTER)
    )]], colWidths=[10*inch])
    ftr.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK),("LINEABOVE",(0,0),(-1,-1),1.5,GOLD),
                              ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    story.append(ftr)

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ── EXPORT BUTTONS ─────────────────────────────────────────────────────────────
sec("⬇️", "Export")
st.markdown('<div class="sec-body">', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    fname_csv = f"CStumpo_{project_name.replace(' ','_')}_{project_date.replace('.','')}.csv"
    st.download_button("⬇  Download CSV", data=build_csv(), file_name=fname_csv, mime="text/csv")
with c2:
    fname_pdf = f"CStumpo_{project_name.replace(' ','_')}_{project_date.replace('.','')}.pdf"
    st.download_button("⬇  Download PDF", data=build_pdf(), file_name=fname_pdf, mime="application/pdf")
with c3:
    st.caption("Both exports include full branding, all line items, subtotals, fees, and alternate scenarios.")
st.markdown('</div>', unsafe_allow_html=True)
