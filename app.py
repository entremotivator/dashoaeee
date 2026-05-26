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
import pandas as pd
import json
import io
import os


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Mobile Category Order Builder",
    page_icon="📲",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# DEFAULT CATEGORY DATA
# =========================================================
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


SAVE_FILE = "saved_category_order.json"


# =========================================================
# SESSION STATE
# =========================================================
if "main_categories" not in st.session_state:
    st.session_state.main_categories = DEFAULT_MAIN_CATEGORIES.copy()

if "building_categories" not in st.session_state:
    st.session_state.building_categories = DEFAULT_BUILDING_CATEGORIES.copy()

if "selected_group" not in st.session_state:
    st.session_state.selected_group = "Main App Categories"


# =========================================================
# MOBILE-FIRST CSS
# =========================================================
st.markdown(
    """
    <style>
    #MainMenu, header, footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        visibility: hidden !important;
        display: none !important;
    }

    html, body, .stApp {
        background: #f5f0e8 !important;
    }

    .block-container {
        max-width: 100% !important;
        padding: 0 0 4rem 0 !important;
    }

    .hero {
        background: linear-gradient(145deg, #101010 0%, #292929 100%);
        padding: 1.35rem 1rem;
        border-bottom: 4px solid #b8972a;
    }

    .hero h1 {
        color: #d4af45;
        font-family: Georgia, serif;
        font-size: clamp(1.25rem, 5vw, 2.3rem);
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        line-height: 1.1;
    }

    .hero p {
        color: #d7d7d7;
        font-size: clamp(0.85rem, 3vw, 1rem);
        margin: 0.45rem 0 0;
        line-height: 1.45;
    }

    .mobile-note {
        background: #fff8e7;
        border: 1px solid #d4af45;
        border-left: 5px solid #b8972a;
        padding: 0.9rem 1rem;
        margin: 1rem;
        border-radius: 10px;
        color: #2c2c2c;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .section-card {
        background: #ffffff;
        margin: 1rem;
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #e1d5bf;
        box-shadow: 0 8px 24px rgba(0,0,0,0.07);
    }

    .section-title {
        font-family: Georgia, serif;
        font-size: clamp(1.05rem, 4vw, 1.55rem);
        color: #1a1a1a;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .section-subtitle {
        color: #666;
        font-size: 0.92rem;
        margin-bottom: 0.85rem;
        line-height: 1.4;
    }

    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.75rem;
        margin: 1rem;
    }

    .stat-card {
        background: #1a1a1a;
        color: #d4af45;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #b8972a;
    }

    .stat-card .label {
        color: #aaa;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.7rem;
        margin-bottom: 0.25rem;
    }

    .stat-card .value {
        font-size: 1.45rem;
        font-family: Georgia, serif;
        font-weight: 700;
    }

    .preview-item {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        background: #fffaf0;
        border: 1px solid #e2d3b2;
        padding: 0.75rem 0.85rem;
        border-radius: 10px;
        margin-bottom: 0.45rem;
        color: #1a1a1a;
        font-weight: 600;
    }

    .preview-num {
        background: #1a1a1a;
        color: #d4af45;
        min-width: 32px;
        height: 32px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: Georgia, serif;
        font-weight: 700;
        font-size: 0.85rem;
    }

    .small-help {
        font-size: 0.82rem;
        color: #666;
        line-height: 1.45;
    }

    .stButton > button,
    .stDownloadButton > button,
    button[kind="primary"],
    button[kind="secondary"] {
        min-height: 48px !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        letter-spacing: 0.04em !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        background: #1a1a1a !important;
        color: #d4af45 !important;
        border: 2px solid #b8972a !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #b8972a !important;
        color: #1a1a1a !important;
    }

    input, textarea, select {
        min-height: 46px !important;
        font-size: 16px !important;
    }

    div[data-testid="stSelectbox"] div,
    div[data-testid="stTextInput"] input {
        font-size: 16px !important;
    }

    @media (max-width: 768px) {
        .hero {
            padding: 1.1rem 0.9rem;
        }

        .section-card {
            margin: 0.75rem;
            padding: 0.9rem;
            border-radius: 12px;
        }

        .mobile-note {
            margin: 0.75rem;
        }

        .stat-grid {
            margin: 0.75rem;
            grid-template-columns: repeat(2, 1fr);
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def get_group_key(group_name):
    if group_name == "Main App Categories":
        return "main_categories"
    return "building_categories"


def clean_category_name(name):
    return " ".join(name.strip().split())


def add_category(group_key, name):
    name = clean_category_name(name)

    if not name:
        st.warning("Please enter a category name.")
        return

    if name in st.session_state[group_key]:
        st.warning("That category already exists.")
        return

    st.session_state[group_key].append(name)
    st.success(f"Added: {name}")


def remove_category(group_key, name):
    if name and name in st.session_state[group_key]:
        st.session_state[group_key].remove(name)
        st.success(f"Removed: {name}")


def rename_category(group_key, old_name, new_name):
    new_name = clean_category_name(new_name)

    if not old_name:
        st.warning("Choose a category to rename.")
        return

    if not new_name:
        st.warning("Enter the new category name.")
        return

    if new_name in st.session_state[group_key] and new_name != old_name:
        st.warning("That new category name already exists.")
        return

    items = st.session_state[group_key]
    index = items.index(old_name)
    items[index] = new_name
    st.session_state[group_key] = items
    st.success(f"Renamed to: {new_name}")


def move_item(group_key, item, direction):
    items = st.session_state[group_key]

    if item not in items:
        return

    index = items.index(item)

    if direction == "up" and index > 0:
        items[index], items[index - 1] = items[index - 1], items[index]

    if direction == "down" and index < len(items) - 1:
        items[index], items[index + 1] = items[index + 1], items[index]

    st.session_state[group_key] = items


def save_to_json_file():
    data = {
        "saved_date": str(date.today()),
        "main_categories": st.session_state.main_categories,
        "building_categories": st.session_state.building_categories,
    }

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return data


def load_from_json_file():
    if not os.path.exists(SAVE_FILE):
        return False

    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    st.session_state.main_categories = data.get(
        "main_categories",
        DEFAULT_MAIN_CATEGORIES.copy(),
    )

    st.session_state.building_categories = data.get(
        "building_categories",
        DEFAULT_BUILDING_CATEGORIES.copy(),
    )

    return True


def build_csv():
    rows = []

    for index, item in enumerate(st.session_state.main_categories, start=1):
        rows.append(
            {
                "Group": "Main App Categories",
                "Order": index,
                "Category": item,
            }
        )

    for index, item in enumerate(st.session_state.building_categories, start=1):
        rows.append(
            {
                "Group": "Building Construction Line Item Categories",
                "Order": index,
                "Category": item,
            }
        )

    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")


def build_json_export():
    data = {
        "generated_date": str(date.today()),
        "main_categories": st.session_state.main_categories,
        "building_categories": st.session_state.building_categories,
    }

    return json.dumps(data, indent=4).encode("utf-8")


def build_pdf():
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
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=9,
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER,
        spaceAfter=16,
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontName="Times-Bold",
        fontSize=13,
        textColor=colors.HexColor("#1A1A1A"),
        spaceBefore=12,
        spaceAfter=8,
    )

    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1A1A1A"),
    )

    story = []

    story.append(Paragraph("C. Stumpo Development", title_style))
    story.append(
        Paragraph(
            f"Mobile Category Order Builder · Generated {date.today().strftime('%B %d, %Y')}",
            subtitle_style,
        )
    )

    story.append(Paragraph("Main App Categories", section_style))

    main_table_data = [["Order", "Category"]]
    for index, item in enumerate(st.session_state.main_categories, start=1):
        main_table_data.append([str(index), Paragraph(item, cell_style)])

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
    for index, item in enumerate(st.session_state.building_categories, start=1):
        building_table_data.append([str(index), Paragraph(item, cell_style)])

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


def render_preview_items(items):
    for index, item in enumerate(items, start=1):
        st.markdown(
            f"""
            <div class="preview-item">
                <div class="preview-num">{index}</div>
                <div>{item}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
    <div class="hero">
        <h1>Mobile Category Order Builder</h1>
        <p>
            Drag categories into the right order, add more items, edit names,
            save your layout, and export the final structure as a PDF.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mobile-note">
        <strong>Mobile tip:</strong> press and hold a category, then drag it up or down.
        If your phone browser does not drag smoothly, use the Move Up / Move Down controls below.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# STATS
# =========================================================
st.markdown(
    f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="label">Main Categories</div>
            <div class="value">{len(st.session_state.main_categories)}</div>
        </div>
        <div class="stat-card">
            <div class="label">Building Categories</div>
            <div class="value">{len(st.session_state.building_categories)}</div>
        </div>
        <div class="stat-card">
            <div class="label">Total Categories</div>
            <div class="value">{len(st.session_state.main_categories) + len(st.session_state.building_categories)}</div>
        </div>
        <div class="stat-card">
            <div class="label">PDF Ready</div>
            <div class="value">Yes</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# GROUP SELECTOR
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Choose Category Group</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Work on one group at a time for a cleaner mobile experience.</div>',
    unsafe_allow_html=True,
)

selected_group = st.radio(
    "Category Group",
    ["Main App Categories", "Building Construction Line Item Categories"],
    horizontal=True,
    label_visibility="collapsed",
)

st.session_state.selected_group = selected_group
group_key = get_group_key(selected_group)

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# DRAG AND DROP ORDERING
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown(f'<div class="section-title">{selected_group}</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-subtitle">
        Drag the cards into the order you want. This order is used in the PDF, CSV, and JSON exports.
    </div>
    """,
    unsafe_allow_html=True,
)

ordered_items = sort_items(
    st.session_state[group_key],
    direction="vertical",
    key=f"sortable_{group_key}",
)

st.session_state[group_key] = ordered_items

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# MOBILE MOVE CONTROLS
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Mobile Move Controls</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-subtitle">
        Use this when phone dragging feels slow. Pick a category and move it one step at a time.
    </div>
    """,
    unsafe_allow_html=True,
)

move_item_name = st.selectbox(
    "Select Category to Move",
    options=st.session_state[group_key],
    key=f"move_select_{group_key}",
)

move_col1, move_col2 = st.columns(2)

with move_col1:
    if st.button("⬆ Move Up", use_container_width=True):
        move_item(group_key, move_item_name, "up")
        st.rerun()

with move_col2:
    if st.button("⬇ Move Down", use_container_width=True):
        move_item(group_key, move_item_name, "down")
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# ADD CATEGORY
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Add More Categories</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Add a new category to the selected group.</div>',
    unsafe_allow_html=True,
)

with st.form(f"add_form_{group_key}", clear_on_submit=True):
    new_category = st.text_input("New Category Name")
    submitted_add = st.form_submit_button("＋ Add Category", use_container_width=True)

    if submitted_add:
        add_category(group_key, new_category)
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# RENAME CATEGORY
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Rename Category</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Edit a category name without changing its order.</div>',
    unsafe_allow_html=True,
)

with st.form(f"rename_form_{group_key}", clear_on_submit=True):
    old_name = st.selectbox(
        "Category to Rename",
        options=st.session_state[group_key],
        key=f"rename_select_{group_key}",
    )

    new_name = st.text_input("New Name")

    submitted_rename = st.form_submit_button("Rename Category", use_container_width=True)

    if submitted_rename:
        rename_category(group_key, old_name, new_name)
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# REMOVE CATEGORY
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Remove Category</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Remove a category from the selected group.</div>',
    unsafe_allow_html=True,
)

remove_name = st.selectbox(
    "Category to Remove",
    options=[""] + st.session_state[group_key],
    key=f"remove_select_{group_key}",
)

if st.button("－ Remove Selected Category", use_container_width=True):
    if remove_name:
        remove_category(group_key, remove_name)
        st.rerun()
    else:
        st.warning("Choose a category first.")

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# FINAL PREVIEW
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Final Ordered Preview</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">This is the full final order that will be exported.</div>',
    unsafe_allow_html=True,
)

preview_tab1, preview_tab2 = st.tabs(
    [
        "Main App Categories",
        "Building Construction Categories",
    ]
)

with preview_tab1:
    render_preview_items(st.session_state.main_categories)

with preview_tab2:
    render_preview_items(st.session_state.building_categories)

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SAVE / LOAD / RESET
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Save, Load, and Reset</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Save the order locally, reload it later, or reset the original category list.</div>',
    unsafe_allow_html=True,
)

save_col1, save_col2, save_col3, save_col4 = st.columns(4)

with save_col1:
    if st.button("💾 Save Order", use_container_width=True):
        save_to_json_file()
        st.success("Category order saved.")

with save_col2:
    if st.button("📂 Load Saved", use_container_width=True):
        loaded = load_from_json_file()
        if loaded:
            st.success("Saved category order loaded.")
            st.rerun()
        else:
            st.warning("No saved order found yet.")

with save_col3:
    if st.button("Reset Main", use_container_width=True):
        st.session_state.main_categories = DEFAULT_MAIN_CATEGORIES.copy()
        st.success("Main categories reset.")
        st.rerun()

with save_col4:
    if st.button("Reset Building", use_container_width=True):
        st.session_state.building_categories = DEFAULT_BUILDING_CATEGORIES.copy()
        st.success("Building categories reset.")
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# EXPORTS
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Export Ordered Categories</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Download your final order as a PDF, CSV, or JSON file.</div>',
    unsafe_allow_html=True,
)

export_col1, export_col2, export_col3 = st.columns(3)

with export_col1:
    st.download_button(
        label="⬇ Download PDF",
        data=build_pdf(),
        file_name="mobile_category_order_builder.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

with export_col2:
    st.download_button(
        label="⬇ Download CSV",
        data=build_csv(),
        file_name="mobile_category_order_builder.csv",
        mime="text/csv",
        use_container_width=True,
    )

with export_col3:
    st.download_button(
        label="⬇ Download JSON",
        data=build_json_export(),
        file_name="mobile_category_order_builder.json",
        mime="application/json",
        use_container_width=True,
    )

st.markdown("</div>", unsafe_allow_html=True)
