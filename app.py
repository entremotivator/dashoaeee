import streamlit as st
import csv
import io
import os
from datetime import date
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="C. Stumpo Development — Construction Estimate",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── HIDE STREAMLIT DEFAULT UI ────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide Streamlit branding, GitHub, settings, deploy button */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    button[title="View fullscreen"] {display: none;}

    /* ── C. Stumpo Brand Palette ─────────────────────── */
    :root {
        --gold:    #B8972A;
        --gold-lt: #D4AF45;
        --dark:    #1A1A1A;
        --charcoal:#2C2C2C;
        --slate:   #4A4A4A;
        --cream:   #F5F0E8;
        --white:   #FFFFFF;
        --border:  #D4B96A;
    }

    /* Body */
    .stApp { background-color: var(--cream); }
    .block-container { padding: 0 2rem 2rem 2rem !important; max-width: 1400px !important; }

    /* Header banner */
    .brand-header {
        background: linear-gradient(135deg, var(--dark) 0%, var(--charcoal) 100%);
        color: var(--gold);
        padding: 2rem 2.5rem 1.5rem;
        margin: -1rem -2rem 2rem -2rem;
        border-bottom: 3px solid var(--gold);
    }
    .brand-header h1 {
        font-family: 'Georgia', serif;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0;
        color: var(--gold-lt);
    }
    .brand-header .sub {
        font-family: 'Georgia', serif;
        font-size: 0.85rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #9A9A9A;
        margin-top: 0.3rem;
    }
    .brand-tagline {
        font-style: italic;
        color: #C8A84C;
        font-size: 0.8rem;
        margin-top: 0.6rem;
    }

    /* Section headers */
    .section-title {
        background: var(--charcoal);
        color: var(--gold);
        padding: 0.5rem 1rem;
        font-family: 'Georgia', serif;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        border-left: 4px solid var(--gold);
        margin: 1.5rem 0 1rem 0;
    }

    /* Inputs */
    .stTextInput > label, .stNumberInput > label, .stTextArea > label, .stSelectbox > label {
        font-family: 'Georgia', serif !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: var(--slate) !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
    }
    .stTextInput input, .stNumberInput input {
        border: 1px solid #C8A84C !important;
        background: var(--white) !important;
        border-radius: 3px !important;
        color: #000000 !important;
        font-family: 'Georgia', serif !important;
        font-weight: 700 !important;
    }
    .stTextArea textarea {
        border: 1px solid #C8A84C !important;
        background: var(--white) !important;
        border-radius: 3px !important;
        color: #000000 !important;
        font-family: 'Georgia', serif !important;
        font-weight: 700 !important;
    }
    /* Number input typed value */
    .stNumberInput input[type="number"] {
        color: #000000 !important;
        font-family: 'Georgia', serif !important;
        font-weight: 700 !important;
    }
    /* Metric value text */
    [data-testid="stMetricValue"] {
        color: var(--gold-lt) !important;
        font-family: 'Georgia', serif !important;
    }
    /* Metric label */
    [data-testid="stMetricLabel"] {
        color: var(--slate) !important;
    }
    /* Column headers bold text */
    .stMarkdown strong {
        color: var(--slate) !important;
        font-family: 'Georgia', serif !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
    }
    /* Caption text */
    .stCaption {
        color: var(--slate) !important;
        font-family: 'Georgia', serif !important;
    }

    /* Buttons */
    .stDownloadButton > button, .stButton > button {
        background: linear-gradient(135deg, var(--dark) 0%, var(--charcoal) 100%) !important;
        color: var(--gold) !important;
        border: 1.5px solid var(--gold) !important;
        border-radius: 3px !important;
        font-family: 'Georgia', serif !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.2s !important;
    }
    .stDownloadButton > button:hover, .stButton > button:hover {
        background: var(--gold) !important;
        color: var(--dark) !important;
    }

    /* Totals box */
    .totals-box {
        background: var(--dark);
        color: var(--white);
        border: 2px solid var(--gold);
        border-radius: 4px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .totals-box .lbl {
        font-family: 'Georgia', serif;
        font-size: 0.78rem;
        color: #9A9A9A;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .totals-box .val {
        font-family: 'Georgia', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--gold-lt);
    }
    .totals-box .grand {
        font-size: 1.8rem;
        color: var(--gold);
        border-top: 1px solid var(--gold);
        padding-top: 0.5rem;
        margin-top: 0.5rem;
    }

    /* Gold divider */
    hr { border-color: var(--gold) !important; opacity: 0.4; }
</style>
""", unsafe_allow_html=True)

# ─── BRAND HEADER ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <h1>C. Stumpo Development</h1>
    <div class="sub">Construction Estimate Form &nbsp;·&nbsp; Marlborough, MA</div>
    <div class="brand-tagline">Excellence in Luxury Home Building &nbsp;|&nbsp; 373 Boylston St, Newton MA &nbsp;|&nbsp; (617) 964-5440</div>
</div>
""", unsafe_allow_html=True)

# ─── PROJECT INFO ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Project Information</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    project_name = st.text_input("Project Name", value="NEIA A Hive")
with col2:
    project_location = st.text_input("Project Location", value="Marlborough MA")
with col3:
    project_date = st.text_input("Date", value=str(date.today().strftime("%-m.%-d.%y")))

# ─── LINE ITEMS ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Building Construction — CSI Division Line Items</div>', unsafe_allow_html=True)

# Default data matching the invoice image
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
    ("",   "ALT/Contingencies",             422765.39, "Design contingency until plans are put together to get hard bids"),
]

if "line_items" not in st.session_state:
    st.session_state.line_items = [list(i) for i in DEFAULT_ITEMS]

# Column headers
hcols = st.columns([1, 3, 2, 4])
hcols[0].markdown("**CSI Div**")
hcols[1].markdown("**Description**")
hcols[2].markdown("**Sub-Total ($)**")
hcols[3].markdown("**Notes**")

updated_items = []
for i, item in enumerate(st.session_state.line_items):
    cols = st.columns([1, 3, 2, 4])
    div  = cols[0].text_input("", value=item[0], key=f"div_{i}", label_visibility="collapsed")
    desc = cols[1].text_input("", value=item[1], key=f"desc_{i}", label_visibility="collapsed")
    amt  = cols[2].number_input("", value=float(item[2]), min_value=0.0, step=100.0, format="%.2f", key=f"amt_{i}", label_visibility="collapsed")
    note = cols[3].text_input("", value=item[3], key=f"note_{i}", label_visibility="collapsed")
    updated_items.append([div, desc, amt, note])

st.session_state.line_items = updated_items

# Add / remove rows
c1, c2 = st.columns([1, 1])
with c1:
    if st.button("＋ Add Line Item"):
        st.session_state.line_items.append(["", "", 0.0, ""])
        st.rerun()
with c2:
    if st.button("－ Remove Last Row") and len(st.session_state.line_items) > 1:
        st.session_state.line_items.pop()
        st.rerun()

# ─── ALLOWANCES / SUBTOTALS ───────────────────────────────────────────────────
st.markdown('<div class="section-title">Allowances & Project Subtotal</div>', unsafe_allow_html=True)

construction_subtotal = sum(row[2] for row in st.session_state.line_items)

col1, col2, col3 = st.columns(3)
with col1:
    site_services = st.number_input("Site Services Subtotal ($)", value=68557.63, step=100.0, format="%.2f")
    site_note = st.text_input("Site Services Note", value="If other projects are going at the same time this would be lower")
with col2:
    gen_conditions = st.number_input("General Conditions Subtotal ($)", value=160191.20, step=100.0, format="%.2f")
    gen_note = st.text_input("General Conditions Note", value="If other projects are going at the same time this would be lower")
with col3:
    project_subtotal = construction_subtotal + site_services + gen_conditions
    st.metric("Project Subtotal", f"${project_subtotal:,.2f}")

# ─── INSURANCE / FEES ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Insurance, Permits & Fees</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    insurance = st.number_input("Insurance ($)", value=54753.76, step=100.0, format="%.2f")
with col2:
    permit = st.number_input("Permit ($)", value=55306.82, step=100.0, format="%.2f")
with col3:
    builders_risk = st.number_input("Builder's Risk ($)", value=33184.09, step=100.0, format="%.2f")
    builders_note = st.text_input("Builder's Risk Note", value="Bentley carrying for now, NEIA can carry")
with col4:
    perf_bond = st.number_input("Payment and Performance Bond ($)", value=0.0, step=100.0, format="%.2f")

# ─── DESIGN COSTS ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Design & Final Totals</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    design_costs = st.number_input("Design Costs ($)", value=90000.0, step=500.0, format="%.2f")
with col2:
    design_notes = st.text_input("Design Notes", value="")

# ─── ALTERNATE SCENARIOS ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">Alternate Cost Scenarios</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    without_contingency   = st.number_input("Without Contingency ($)",                                    value=2485820.48, step=100.0, format="%.2f")
    remove_roofing        = st.number_input("Remove Roofing, Add $50K Allowance from Overall Cost ($)",   value=2942760.87, step=100.0, format="%.2f")
with col2:
    bldg_cost_components  = st.number_input("Cost Associated with Building (Roofing, Stairwell, Masonry, Air Handler) ($)", value=491534.48, step=100.0, format="%.2f")
    fitout_without_bldg   = st.number_input("Costs of Fitout Without Building Costs ($)",                 value=2507051.39, step=100.0, format="%.2f")

# ─── COMPUTE TOTALS ───────────────────────────────────────────────────────────
construction_total = project_subtotal + insurance + permit + builders_risk + perf_bond
grand_total        = construction_total + design_costs

# ─── TOTALS DISPLAY ───────────────────────────────────────────────────────────
st.markdown(f"""
<div class="totals-box">
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-bottom:1rem;">
        <div>
            <div class="lbl">Construction Subtotal</div>
            <div class="val">${construction_subtotal:,.2f}</div>
        </div>
        <div>
            <div class="lbl">Project Subtotal</div>
            <div class="val">${project_subtotal:,.2f}</div>
        </div>
        <div>
            <div class="lbl">Construction Total</div>
            <div class="val">${construction_total:,.2f}</div>
        </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
        <div>
            <div class="lbl">Design Costs</div>
            <div class="val">${design_costs:,.2f}</div>
        </div>
        <div>
            <div class="lbl grand">Total Construction &amp; Design Costs</div>
            <div class="val grand">${grand_total:,.2f}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── EXPORT FUNCTIONS ─────────────────────────────────────────────────────────

def build_csv():
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["C. STUMPO DEVELOPMENT — CONSTRUCTION ESTIMATE"])
    writer.writerow(["373 Boylston Street, Newton MA 02459 | (617) 964-5440 | cstumpodevelopment.com"])
    writer.writerow([])
    writer.writerow(["Project Name:", project_name])
    writer.writerow(["Project Location:", project_location])
    writer.writerow(["Date:", project_date])
    writer.writerow([])
    writer.writerow(["--- BUILDING CONSTRUCTION ---"])
    writer.writerow(["CSI Division", "Description", "Sub-Total Amount", "Notes"])

    for row in st.session_state.line_items:
        writer.writerow([row[0], row[1], f"${row[2]:,.2f}" if row[2] else "-", row[3]])

    writer.writerow([])
    writer.writerow(["Construction Subtotal", "", f"${construction_subtotal:,.2f}", ""])
    writer.writerow([])
    writer.writerow(["--- ALLOWANCES ---"])
    writer.writerow(["Construction Subtotal", "", f"${construction_subtotal:,.2f}", ""])
    writer.writerow(["Site Services Subtotal", "", f"${site_services:,.2f}", site_note])
    writer.writerow(["General Conditions Subtotal", "", f"${gen_conditions:,.2f}", gen_note])
    writer.writerow(["Project Subtotal", "", f"${project_subtotal:,.2f}", ""])
    writer.writerow([])
    writer.writerow(["--- INSURANCE / FEES ---"])
    writer.writerow(["Insurance", "", f"${insurance:,.2f}", ""])
    writer.writerow(["Permit", "", f"${permit:,.2f}", ""])
    writer.writerow(["Builder's Risk", "", f"${builders_risk:,.2f}", builders_note])
    writer.writerow(["Payment and Performance Bond", "", f"${perf_bond:,.2f}", ""])
    writer.writerow([])
    writer.writerow(["Construction Total", "", f"${construction_total:,.2f}", ""])
    writer.writerow(["Design Costs", "", f"${design_costs:,.2f}", design_notes])
    writer.writerow(["TOTAL CONSTRUCTION AND DESIGN COSTS", "", f"${grand_total:,.2f}", ""])
    writer.writerow([])
    writer.writerow(["--- ALTERNATE SCENARIOS ---"])
    writer.writerow(["Without Contingency", "", f"${without_contingency:,.2f}", ""])
    writer.writerow(["Remove Roofing Add $50K Allowance", "", f"${remove_roofing:,.2f}", ""])
    writer.writerow(["Cost Associated with Building (Roofing/Stairwell/Masonry/Air Handler)", "", f"${bldg_cost_components:,.2f}", ""])
    writer.writerow(["Costs of Fitout Without Building Costs", "", f"${fitout_without_bldg:,.2f}", ""])

    return output.getvalue().encode("utf-8")


def build_pdf():
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(letter),
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
    )

    DARK   = colors.HexColor("#1A1A1A")
    GOLD   = colors.HexColor("#B8972A")
    CREAM  = colors.HexColor("#F5F0E8")
    LGOLD  = colors.HexColor("#D4AF45")
    SLATE  = colors.HexColor("#4A4A4A")
    WHITE  = colors.white

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("BrandTitle",
        fontName="Times-Bold", fontSize=20,
        textColor=LGOLD, alignment=TA_CENTER, spaceAfter=2)
    sub_style = ParagraphStyle("BrandSub",
        fontName="Times-Italic", fontSize=9,
        textColor=colors.HexColor("#9A9A9A"), alignment=TA_CENTER, spaceAfter=6)
    section_style = ParagraphStyle("Section",
        fontName="Times-Bold", fontSize=9,
        textColor=GOLD, alignment=TA_LEFT, spaceBefore=8, spaceAfter=4)
    total_style = ParagraphStyle("Total",
        fontName="Times-Bold", fontSize=13,
        textColor=LGOLD, alignment=TA_RIGHT, spaceBefore=6)

    story = []

    # Header block (drawn as a table for background color)
    header_data = [[
        Paragraph("C. STUMPO DEVELOPMENT", title_style),
    ]]
    header_tbl = Table(header_data, colWidths=[10*inch])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK),
        ("LINEBELOW",  (0,0), (-1,-1), 2, GOLD),
        ("TOPPADDING",  (0,0), (-1,-1), 12),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
    ]))
    story.append(header_tbl)

    sub_data = [[
        Paragraph("Construction Estimate  ·  Excellence in Luxury Home Building  ·  373 Boylston St, Newton MA  ·  (617) 964-5440  ·  cstumpodevelopment.com", sub_style),
    ]]
    sub_tbl = Table(sub_data, colWidths=[10*inch])
    sub_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,-1), DARK),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
    ]))
    story.append(sub_tbl)
    story.append(Spacer(1, 8))

    # Project info
    pi_style = ParagraphStyle("PI", fontName="Times-Bold", fontSize=9, textColor=SLATE)
    pi_val   = ParagraphStyle("PIv", fontName="Times-Roman", fontSize=9, textColor=DARK)
    pi_data  = [[
        Paragraph("Project Name:", pi_style), Paragraph(project_name, pi_val),
        Paragraph("Location:", pi_style),     Paragraph(project_location, pi_val),
        Paragraph("Date:", pi_style),          Paragraph(project_date, pi_val),
    ]]
    pi_tbl = Table(pi_data, colWidths=[1*inch, 2.2*inch, 0.8*inch, 2.2*inch, 0.6*inch, 1.4*inch])
    pi_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), CREAM),
        ("LINEBELOW",  (0,0),(-1,-1), 0.5, GOLD),
        ("TOPPADDING",  (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ]))
    story.append(pi_tbl)
    story.append(Spacer(1, 8))

    # Section: Building Construction
    story.append(Paragraph("BUILDING CONSTRUCTION — CSI DIVISION LINE ITEMS", section_style))

    hdr_sty = ParagraphStyle("Hdr", fontName="Times-Bold", fontSize=8, textColor=WHITE)
    cell_sty = ParagraphStyle("Cell", fontName="Times-Roman", fontSize=8, textColor=DARK)
    cell_r   = ParagraphStyle("CellR", fontName="Times-Roman", fontSize=8, textColor=DARK, alignment=TA_RIGHT)
    note_sty = ParagraphStyle("Note", fontName="Times-Italic", fontSize=7, textColor=SLATE)

    tbl_data = [[
        Paragraph("CSI Div", hdr_sty),
        Paragraph("Description", hdr_sty),
        Paragraph("Sub-Total", hdr_sty),
        Paragraph("Notes", hdr_sty),
    ]]
    for row in st.session_state.line_items:
        amt_str = f"${row[2]:,.2f}" if row[2] else "—"
        tbl_data.append([
            Paragraph(str(row[0]), cell_sty),
            Paragraph(str(row[1]), cell_sty),
            Paragraph(amt_str, cell_r),
            Paragraph(str(row[3]), note_sty),
        ])

    main_tbl = Table(tbl_data, colWidths=[0.6*inch, 2.5*inch, 1.3*inch, 5.6*inch], repeatRows=1)
    row_count = len(tbl_data)
    ts = [
        ("BACKGROUND",  (0,0), (-1,0),  DARK),
        ("TEXTCOLOR",   (0,0), (-1,0),  GOLD),
        ("LINEBELOW",   (0,0), (-1,0),  1.5, GOLD),
        ("FONTNAME",    (0,0), (-1,0),  "Times-Bold"),
        ("FONTSIZE",    (0,0), (-1,0),  8),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LINEBELOW",   (0,1), (-1,-1), 0.3, colors.HexColor("#D4B96A")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, CREAM]),
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
        ("ALIGN",       (2,1), (2,-1),  "RIGHT"),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING",(0,0), (-1,-1), 5),
    ]
    main_tbl.setStyle(TableStyle(ts))
    story.append(main_tbl)
    story.append(Spacer(1, 6))

    # Subtotals / Allowances
    story.append(Paragraph("ALLOWANCES & PROJECT SUBTOTAL", section_style))
    allow_data = [
        [Paragraph("Construction Subtotal",      cell_sty), Paragraph(f"${construction_subtotal:,.2f}", cell_r), Paragraph("",       note_sty)],
        [Paragraph("Site Services Subtotal",     cell_sty), Paragraph(f"${site_services:,.2f}",         cell_r), Paragraph(site_note, note_sty)],
        [Paragraph("General Conditions Subtotal",cell_sty), Paragraph(f"${gen_conditions:,.2f}",        cell_r), Paragraph(gen_note,  note_sty)],
        [Paragraph("Project Subtotal",           ParagraphStyle("PSub",fontName="Times-Bold",fontSize=8,textColor=DARK)),
                                                            Paragraph(f"${project_subtotal:,.2f}",       ParagraphStyle("PSub2",fontName="Times-Bold",fontSize=8,textColor=DARK,alignment=TA_RIGHT)),
                                                            Paragraph("",note_sty)],
    ]
    allow_tbl = Table(allow_data, colWidths=[2.5*inch, 1.3*inch, 6.2*inch])
    allow_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,CREAM]),
        ("LINEBELOW",    (0,-1),(-1,-1), 1.5, GOLD),
        ("LINEBELOW",    (0,0), (-1,-2), 0.3, colors.HexColor("#D4B96A")),
        ("TOPPADDING",   (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING",  (0,0),(-1,-1), 5),
        ("ALIGN",        (1,0),(1,-1),  "RIGHT"),
    ]))
    story.append(allow_tbl)
    story.append(Spacer(1, 4))

    # Insurance / Fees
    story.append(Paragraph("INSURANCE, PERMITS & FEES", section_style))
    fee_data = [
        [Paragraph("Insurance",                     cell_sty), Paragraph(f"${insurance:,.2f}",     cell_r), Paragraph("", note_sty)],
        [Paragraph("Permit",                        cell_sty), Paragraph(f"${permit:,.2f}",        cell_r), Paragraph("", note_sty)],
        [Paragraph("Builder's Risk",                cell_sty), Paragraph(f"${builders_risk:,.2f}", cell_r), Paragraph(builders_note, note_sty)],
        [Paragraph("Payment and Performance Bond",  cell_sty), Paragraph(f"${perf_bond:,.2f}",     cell_r), Paragraph("", note_sty)],
    ]
    fee_tbl = Table(fee_data, colWidths=[2.5*inch, 1.3*inch, 6.2*inch])
    fee_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,CREAM]),
        ("LINEBELOW",    (0,0),(-1,-1), 0.3, colors.HexColor("#D4B96A")),
        ("TOPPADDING",   (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING",  (0,0),(-1,-1), 5),
        ("ALIGN",        (1,0),(1,-1), "RIGHT"),
    ]))
    story.append(fee_tbl)
    story.append(Spacer(1, 4))

    # Grand totals
    gt_data = [
        [Paragraph("Construction Total",                  ParagraphStyle("gt1",fontName="Times-Bold",fontSize=9,textColor=DARK)),
         Paragraph(f"${construction_total:,.2f}",         ParagraphStyle("gt1v",fontName="Times-Bold",fontSize=9,textColor=DARK,alignment=TA_RIGHT)),
         Paragraph("",note_sty)],
        [Paragraph("Design Costs",                        ParagraphStyle("gt2",fontName="Times-Bold",fontSize=9,textColor=DARK)),
         Paragraph(f"${design_costs:,.2f}",               ParagraphStyle("gt2v",fontName="Times-Bold",fontSize=9,textColor=DARK,alignment=TA_RIGHT)),
         Paragraph(design_notes, note_sty)],
        [Paragraph("TOTAL CONSTRUCTION AND DESIGN COSTS", ParagraphStyle("gt3",fontName="Times-Bold",fontSize=11,textColor=DARK)),
         Paragraph(f"${grand_total:,.2f}",                ParagraphStyle("gt3v",fontName="Times-Bold",fontSize=11,textColor=LGOLD,alignment=TA_RIGHT)),
         Paragraph("",note_sty)],
    ]
    gt_tbl = Table(gt_data, colWidths=[2.5*inch, 1.3*inch, 6.2*inch])
    gt_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,2),(-1,2), DARK),
        ("LINEABOVE",     (0,0),(-1,0), 1.5, GOLD),
        ("LINEBELOW",     (0,1),(-1,1), 0.5, GOLD),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("ALIGN",         (1,0),(1,-1), "RIGHT"),
    ]))
    story.append(gt_tbl)
    story.append(Spacer(1, 6))

    # Alternate scenarios
    story.append(Paragraph("ALTERNATE COST SCENARIOS", section_style))
    alt_data = [
        [Paragraph("Without Contingency",                                         cell_sty), Paragraph(f"${without_contingency:,.2f}",  cell_r)],
        [Paragraph("Remove Roofing, Add $50K Allowance from Overall Cost",        cell_sty), Paragraph(f"${remove_roofing:,.2f}",       cell_r)],
        [Paragraph("Cost Associated with Building (Roofing, Stairwell, Masonry, Air Handler)", cell_sty), Paragraph(f"${bldg_cost_components:,.2f}", cell_r)],
        [Paragraph("Costs of Fitout Without Building Costs",                      cell_sty), Paragraph(f"${fitout_without_bldg:,.2f}", cell_r)],
    ]
    alt_tbl = Table(alt_data, colWidths=[8.7*inch, 1.3*inch])
    alt_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,CREAM]),
        ("LINEBELOW",    (0,0),(-1,-1), 0.3, colors.HexColor("#D4B96A")),
        ("TOPPADDING",   (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING",  (0,0),(-1,-1), 5),
        ("ALIGN",        (1,0),(1,-1), "RIGHT"),
    ]))
    story.append(alt_tbl)

    # Footer
    story.append(Spacer(1, 10))
    footer_data = [[
        Paragraph("C. Stumpo Development, Inc.  ·  373 Boylston Street (Route 9 West), Newton, MA 02459  ·  (617) 964-5440  ·  cstumpodevelopment.com",
                  ParagraphStyle("foot", fontName="Times-Italic", fontSize=7, textColor=colors.HexColor("#9A9A9A"), alignment=TA_CENTER))
    ]]
    foot_tbl = Table(footer_data, colWidths=[10*inch])
    foot_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), DARK),
        ("LINEABOVE",    (0,0),(-1,-1), 1.5, GOLD),
        ("TOPPADDING",   (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
    ]))
    story.append(foot_tbl)

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ─── EXPORT BUTTONS ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Export</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    csv_data = build_csv()
    fname_csv = f"CStumpo_Estimate_{project_name.replace(' ','_')}_{project_date.replace('.','')}.csv"
    st.download_button(
        label="⬇ Download CSV",
        data=csv_data,
        file_name=fname_csv,
        mime="text/csv",
    )
with col2:
    pdf_data = build_pdf()
    fname_pdf = f"CStumpo_Estimate_{project_name.replace(' ','_')}_{project_date.replace('.','')}.pdf"
    st.download_button(
        label="⬇ Download PDF",
        data=pdf_data,
        file_name=fname_pdf,
        mime="application/pdf",
    )
with col3:
    st.markdown("")
    st.caption("Both exports include full branding, all line items, subtotals, fees, and alternate scenarios.")
