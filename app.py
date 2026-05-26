import streamlit as st
from streamlit_sortables import sort_items
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import date
import io


# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(
    page_title="Category Order Builder",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ----------------------------------------------------
# DEFAULT DATA
# ----------------------------------------------------
DEFAULT_MAIN_CATEGORIES = [
    "Project Information",
    "Building Construction — CSI Division Line Items",
    "Allowances & Project Subtotal",
    "Insurance, Permits & Fees",
    "Design Costs",
    "Alternate Cost Scenarios",
    "Project Totals",
    "Export",
]

DEFAULT_BUILDING_CATEGORIES = [
    "Government Requirement",
    "Site Work",
    "Demolition",
    "Concrete",
    "Masonry",
    "Misc. Metals",
    "Structural Steel",
    "Carpentry",
    "Millwork",
    "Moisture and Damproofing",
    "Roofing",
    "Insulation",
    "Air and Vapor Barrier",
    "Joint Sealants",
    "Applied Fireproofing",
    "Doors, Frames, Hardware",
    "Overhead Doors",
    "Glass and Glazing",
    "Drywall / Framing / Insulation",
    "Acoustical Ceilings",
    "Flooring",
    "Painting and Coatings",
    "Misc. Specialties",
    "Appliances",
    "Signage",
    "Window Treatments",
    "Window Film",
    "Conveying Systems",
    "Fire Protection",
    "Plumbing",
    "Mechanical",
    "Electrical",
    "Low Voltage",
    "ALT / Contingencies",
]


# ----------------------------------------------------
# SESSION STATE
# ----------------------------------------------------
if "main_categories" not in st.session_state:
    st.session_state.main_categories = DEFAULT_MAIN_CATEGORIES.copy()

if "building_categories" not in st.session_state:
    st.session_state.building_categories = DEFAULT_BUILDING_CATEGORIES.copy()


# ----------------------------------------------------
# CSS
# ----------------------------------------------------
st.markdown(
    """
    <style>
    #MainMenu, header, footer {
        visibility: hidden;
    }

    .stApp {
        background: #f5f0e8;
    }

    .page-header {
        background: linear-gradient(160deg, #111111, #2c2c2c);
        padding: 28px;
        border-bottom: 4px solid #b8972a;
        margin-bottom: 24px;
    }

    .page-header h1 {
        color: #d4af45;
        font-family: Georgia, serif;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0;
    }

    .page-header p {
        color: #cccccc;
        margin-top: 8px;
        font-size: 15px;
    }

    .section-card {
        background: #ffffff;
        padding: 22px;
        border-radius: 10px;
        border: 1px solid #e5d8bd;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        margin-bottom: 20px;
    }

    .section-title {
        font-family: Georgia, serif;
        color: #1a1a1a;
        font-size: 21px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .section-subtitle {
        color: #666666;
        font-size: 14px;
        margin-bottom: 18px;
    }

    .stButton button,
    .stDownloadButton button {
        background: #1a1a1a !important;
        color: #d4af45 !important;
        border: 2px solid #b8972a !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    .stButton button:hover,
    .stDownloadButton button:hover {
        background: #b8972a !important;
        color: #1a1a1a !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------
# PDF BUILDER
# ----------------------------------------------------
def build_pdf(main_categories, building_categories):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Times-Bold",
        fontSize=20,
        textColor=colors.HexColor("#B8972A"),
        alignment=TA_CENTER,
        spaceAfter=10,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER,
        spaceAfter=18,
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontName="Times-Bold",
        fontSize=13,
        textColor=colors.HexColor("#1A1A1A"),
        spaceBefore=14,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        textColor=colors.HexColor("#1A1A1A"),
    )

    story = []

    story.append(Paragraph("C. Stumpo Development", title_style))
    story.append(
        Paragraph(
            f"Drag-and-Drop Category Order List · Generated {date.today().strftime('%B %d, %Y')}",
            subtitle_style,
        )
    )

    story.append(Paragraph("Main App Categories", section_style))

    main_table_data = [["Order", "Category"]]
    for index, item in enumerate(main_categories, start=1):
        main_table_data.append([str(index), Paragraph(item, normal_style)])

    main_table = Table(main_table_data, colWidths=[0.75 * inch, 6.4 * inch])
    main_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A1A1A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#D4AF45")),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D4B96A")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F0E8")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(main_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Building Construction Line Item Categories", section_style))

    building_table_data = [["Order", "Category"]]
    for index, item in enumerate(building_categories, start=1):
        building_table_data.append([str(index), Paragraph(item, normal_style)])

    building_table = Table(building_table_data, colWidths=[0.75 * inch, 6.4 * inch])
    building_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A1A1A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#D4AF45")),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D4B96A")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F0E8")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(building_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# ----------------------------------------------------
# HEADER
# ----------------------------------------------------
st.markdown(
    """
    <div class="page-header">
        <h1>Category Order Builder</h1>
        <p>Drag, reorder, add more categories, and export the final order as a PDF.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------
# MAIN LAYOUT
# ----------------------------------------------------
left, right = st.columns([1, 1])


# ----------------------------------------------------
# MAIN APP CATEGORIES
# ----------------------------------------------------
with left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Main App Categories</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Drag the items to change the page order.</div>',
        unsafe_allow_html=True,
    )

    ordered_main = sort_items(
        st.session_state.main_categories,
        direction="vertical",
        key="main_category_sort",
    )

    st.session_state.main_categories = ordered_main

    new_main = st.text_input("Add Main App Category", key="new_main_category")

    add_main_col, remove_main_col = st.columns(2)

    with add_main_col:
        if st.button("Add Main Category", use_container_width=True):
            if new_main.strip():
                st.session_state.main_categories.append(new_main.strip())
                st.session_state.new_main_category = ""
                st.rerun()

    with remove_main_col:
        selected_main_remove = st.selectbox(
            "Remove Main Category",
            options=[""] + st.session_state.main_categories,
            key="remove_main_select",
        )

        if st.button("Remove Selected Main", use_container_width=True):
            if selected_main_remove:
                st.session_state.main_categories.remove(selected_main_remove)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------
# BUILDING LINE ITEM CATEGORIES
# ----------------------------------------------------
with right:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Building Construction Line Item Categories</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Drag the construction categories into the order you want.</div>',
        unsafe_allow_html=True,
    )

    ordered_building = sort_items(
        st.session_state.building_categories,
        direction="vertical",
        key="building_category_sort",
    )

    st.session_state.building_categories = ordered_building

    new_building = st.text_input("Add Building Category", key="new_building_category")

    add_building_col, remove_building_col = st.columns(2)

    with add_building_col:
        if st.button("Add Building Category", use_container_width=True):
            if new_building.strip():
                st.session_state.building_categories.append(new_building.strip())
                st.session_state.new_building_category = ""
                st.rerun()

    with remove_building_col:
        selected_building_remove = st.selectbox(
            "Remove Building Category",
            options=[""] + st.session_state.building_categories,
            key="remove_building_select",
        )

        if st.button("Remove Selected Building", use_container_width=True):
            if selected_building_remove:
                st.session_state.building_categories.remove(selected_building_remove)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------
# FINAL ORDER PREVIEW
# ----------------------------------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Final Ordered Preview</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">This is the order that will be saved into the PDF.</div>',
    unsafe_allow_html=True,
)

preview_left, preview_right = st.columns(2)

with preview_left:
    st.subheader("Main App Categories")
    for index, item in enumerate(st.session_state.main_categories, start=1):
        st.write(f"{index}. {item}")

with preview_right:
    st.subheader("Building Construction Categories")
    for index, item in enumerate(st.session_state.building_categories, start=1):
        st.write(f"{index}. {item}")

st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------
# ACTION BUTTONS
# ----------------------------------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Save / Export</div>', unsafe_allow_html=True)

action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    pdf_data = build_pdf(
        st.session_state.main_categories,
        st.session_state.building_categories,
    )

    st.download_button(
        label="Download Ordered PDF",
        data=pdf_data,
        file_name="category_order_builder.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

with action_col2:
    if st.button("Reset Main Categories", use_container_width=True):
        st.session_state.main_categories = DEFAULT_MAIN_CATEGORIES.copy()
        st.rerun()

with action_col3:
    if st.button("Reset Building Categories", use_container_width=True):
        st.session_state.building_categories = DEFAULT_BUILDING_CATEGORIES.copy()
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
