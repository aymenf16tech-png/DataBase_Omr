import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# =========================================================
# 1. إعدادات الصفحة العامة
# =========================================================
logo_path = "logo.jfif"

st.set_page_config(
    page_title="مشروع العمر للمصلحين",
    page_icon=logo_path if os.path.exists(logo_path) else "📚",
    layout="wide",
)

# هوية بصرية مبسطة للبطاقات (HTML قياسي متوافق مع الاتجاه)
NAVY = "#1e293b"
GOLD = "#d97706"
EMERALD = "#10b981"
SKY = "#38bdf8"
ROSE = "#f43f5e"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

# حقن CSS شامل لفرض محاذاة اليمين المطلقة لكافة النصوص والعناوين
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');

    /* استهداف مطلق لكل عناصر التطبيق وفرض المحاذاة والخط جهة اليمين */
    * {
        font-family: 'Tajawal', sans-serif !important;
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* استثناء خاص لحاوية أرقام بطاقات الـ KPI لكي لا تنعكس الأرقام العشرية */
    .kpi-num-fix {
        direction: ltr !important;
        text-align: right !important;
        display: inline-block !important;
        font-family: monospace !important;
    }
    
    /* تأمين التبويبات (Tabs) لتبدأ الاصطفاف من اليمين قسراً */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: flex-start !important;
    }
    
    /* إجبار الجداول ومحتوياتها على محاذاة اليمين المطلقة */
    table, th, td, [data-testid="stTable"] * {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* إخفاء شريط التمرير الأفقي السفلي تماماً */
    html, body, [data-testid="stAppViewContainer"] {
        overflow-x: hidden !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 2. أدوات مساعدة وقاعدة البيانات
# =========================================================
@st.cache_data(ttl=300)
def get_data(query: str) -> pd.DataFrame:
    conn = sqlite3.connect('Omr_Project.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def duration_to_hours_expr(col: str) -> str:
    return (f"(SUBSTR({col}, 1, 2) * 3600 + SUBSTR({col}, 4, 2) * 60 "
            f"+ SUBSTR({col}, 7, 2)) / 3600.0")

def kpi_card(icon: str, label: str, value: str, unit: str, accent: str):
    st.markdown(f"""
        <div style="background: linear-gradient(145deg, {NAVY} 0%, #16213a 100%);
                    border-radius: 16px; padding: 22px 20px; border-right: 4px solid {accent};
                    box-shadow: 0 8px 20px -6px rgba(0,0,0,0.45); margin-bottom: 10px;">
            <div style="font-size: 1.6rem;">{icon}</div>
            <div style="display: flex; gap: 8px; align-items: baseline; margin-top: 8px;">
                <span class="kpi-num-fix" style="color: {TEXT_MAIN}; font-size: 2.2rem; font-weight: 700;">{value}</span>
                <span style="color: {TEXT_MUTED}; font-size: 1rem;">{unit}</span>
            </div>
            <div style="color: {TEXT_MUTED}; font-size: 0.92rem; margin-top: 4px;">{label}</div>
        </div>
    """, unsafe_allow_html=True)

def show_table(df: pd.DataFrame):
    if df.empty:
        return
    st.table(df.style.hide(axis="index"))

# إدارة حالة العرض لفرز الأزرار عبر استغلال الـ Session State
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'none'

# =========================================================
# 3. الترويسة الرئيسية والتحكم العلوي
# =========================================================
menu_col1, menu_col2, menu_col3 = st.columns([1, 4, 2])

with menu_col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=80)

with menu_col2:
    st.title("إحصاءات برنامج مشروع العمر ")

with menu_col3:
    st.write("")
    if st.button("🔄 تحديث البيانات ", use_container_width=True):
        st.cache_data.clear()
        st.toast("تم تحديث وجلب البيانات بنجاح! 🚀")
        st.rerun()

st.write("---")

# =========================================================
# 4. الإحصائيات العامة الكلية للمشروع
# =========================================================
st.markdown("### 📊 الإحصائيات العامة لبرنامج مشروع العمر ")
try:
    totals_df = get_data(f"SELECT SUM(CASE WHEN type = 'مسموع' THEN {duration_to_hours_expr('duration_time')} ELSE 0 END) as audio_hours, SUM(CASE WHEN type = 'مقروء' THEN pages_count ELSE 0 END) as read_pages FROM Courses_Materials;")
    events_df = get_data(f"SELECT SUM({duration_to_hours_expr('duration_time')}) as ev_hours FROM Stage_Events;")
    comps_df = get_data("SELECT SUM(contests_count) as c_count FROM Competitions;")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("🎙️", "إجمالي المواد المسموعة", f"{totals_df['audio_hours'].iloc[0]:.1f}", "ساعة", GOLD)
    with c2: kpi_card("📖", "إجمالي الصفحات المقروءة", f"{int(totals_df['read_pages'].iloc[0])}", "صفحة", EMERALD)
    with c3: kpi_card("👥", "إجمالي المدارسات والفعاليات", f"{events_df['ev_hours'].iloc[0]:.1f}", "ساعة", SKY)
    with c4: kpi_card("🏆", "إجمالي المسابقات", f"{int(comps_df['c_count'].iloc[0])}", "مسابقة", ROSE)
except:
    st.error("يرجى التأكد من تشغيل البيانات بنجاح.")

st.write("---")

# =========================================================
# 5. ✨ البرنامج العام والفعاليات المشتركة
# =========================================================
st.markdown("### ✨ البرنامج العام والفعاليات المشتركة")
try:
    gen_events_df = get_data("SELECT title as 'عنوان الفعالية', duration_time as 'المدة الزمنية' FROM Stage_Events WHERE stage_id = 100;")
    if not gen_events_df.empty:
        show_table(gen_events_df)
    else:
        st.caption("لا توجد فعاليات عامة مسجلة حالياً.")
except:
    st.warning("تعذر جلب الأنشطة العامة للمشروع.")

st.write("---")

# =========================================================
# 6. أزرار إظهار الفرز التفصيلي (أسفل الجدول مباشرة)
# =========================================================
st.markdown("### 🗂️ استعراض الفرز والتقارير التفصيلية للبرنامج")
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])

with btn_col1:
    if st.button("👤 إظهار فرز التخصصات", use_container_width=True):
        st.session_state.view_mode = 'specialty'

with btn_col2:
    if st.button("🎯 إظهار فرز المراحل الدراسية", use_container_width=True):
        st.session_state.view_mode = 'stage'

with btn_col3:
    if st.session_state.view_mode != 'none':
        if st.button("❌ إغلاق التقارير التفصيلية", use_container_width=True):
            st.session_state.view_mode = 'none'
            st.rerun()

st.write("")

# ---------------------------------------------------------
# سياق عرض الفرز المختار ديناميكياً
# ---------------------------------------------------------
if st.session_state.view_mode == 'specialty':
    st.markdown("#### 🔍 الفرز والإحصاء التفصيلي حسب التخصص الدراسي")
    try:
        specialties_options = get_data("SELECT name FROM Specialties;")['name'].tolist()
        selected_spec = st.selectbox("👤 حدد التخصص المراد استعراض إحصاءاته:", specialties_options)
        
        spec_stats = get_data(f"SELECT IFNULL(SUM(CASE WHEN cm.type='مسموع' THEN {duration_to_hours_expr('cm.duration_time')} ELSE 0 END), 0) as audio_h, IFNULL(SUM(CASE WHEN cm.type='مقروء' THEN cm.pages_count ELSE 0 END), 0) as read_p FROM Courses_Materials cm JOIN Specialty_Stages ss ON cm.stage_id = ss.stage_id JOIN Specialties s ON ss.specialty_id = s.specialty_id WHERE s.name = '{selected_spec}' AND cm.stage_id != 100;")
        spec_ev = get_data(f"SELECT IFNULL(SUM({duration_to_hours_expr('se.duration_time')}), 0) as ev_h FROM Stage_Events se JOIN Specialty_Stages ss ON se.stage_id = ss.stage_id JOIN Specialties s ON ss.specialty_id = s.specialty_id WHERE s.name = '{selected_spec}' AND se.stage_id != 100;")
        spec_comp = get_data(f"SELECT IFNULL(SUM(c.contests_count), 0) as c_cnt FROM Competitions c JOIN Specialty_Stages ss ON c.stage_id = ss.stage_id JOIN Specialties s ON ss.specialty_id = s.specialty_id WHERE s.name = '{selected_spec}' AND c.stage_id != 100;")

        sp1, sp2, sp3, sp4 = st.columns(4)
        with sp1: kpi_card("🎙️", "ساعات المواد المسموعة ", f"{spec_stats['audio_h'].iloc[0]:.1f}", "ساعة", GOLD)
        with sp2: kpi_card("📖", "صفحات المواد المقروءة", f"{int(spec_stats['read_p'].iloc[0])}", "صفحة", EMERALD)
        with sp3: kpi_card("👥", "من المدارسات والفعاليات", f"{spec_ev['ev_h'].iloc[0]:.1f}", "ساعة", SKY)
        with sp4: kpi_card("🏆", "المسابقات المعقودة", f"{int(spec_comp['c_cnt'].iloc[0])}", "مسابقة", ROSE)

        st.markdown(f"##### 📋 المراحل المنهجية المحددة لتخصص ({selected_spec})")
        spec_stages_df = get_data(f"SELECT st.name as 'اسم المرحلة', st.start_date_gregorian as 'تاريخ البداية', st.end_date_gregorian as 'تاريخ الانتهاء' FROM Stages st JOIN Specialty_Stages ss ON st.stage_id = ss.stage_id JOIN Specialties s ON ss.specialty_id = s.specialty_id WHERE s.name = '{selected_spec}' AND st.stage_id != 100;")
        show_table(spec_stages_df)
    except:
        st.warning("لا توجد بيانات مسجلة حالياً لهذا التخصص.")

elif st.session_state.view_mode == 'stage':
    st.markdown("#### 🎯 الفرز والإحصاء التفصيلي حسب المرحلة الدراسية")
    try:
        stages_options = get_data("SELECT name FROM Stages WHERE stage_id != 100;")['name'].tolist()
        selected_stage = st.selectbox("🎯 حدد المرحلة الدراسية المعنية:", stages_options)
        current_stage_id = int(get_data(f"SELECT stage_id FROM Stages WHERE name = '{selected_stage}';")['stage_id'].iloc[0])

        stage_stats = get_data(f"SELECT IFNULL(SUM(CASE WHEN type='مسموع' THEN {duration_to_hours_expr('duration_time')} ELSE 0 END), 0) as audio_h, IFNULL(SUM(CASE WHEN type='مقروء' THEN pages_count ELSE 0 END), 0) as read_p FROM Courses_Materials WHERE stage_id = {current_stage_id};")
        stage_ev = get_data(f"SELECT IFNULL(SUM({duration_to_hours_expr('duration_time')}), 0) as ev_h FROM Stage_Events WHERE stage_id = {current_stage_id};")
        stage_comp = get_data(f"SELECT IFNULL(SUM(contests_count), 0) as c_cnt FROM Competitions WHERE stage_id = {current_stage_id};")

        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi_card("🎙️", "المقررات المسموعة", f"{stage_stats['audio_h'].iloc[0]:.1f}", "ساعة", GOLD)
        with c2: kpi_card("📖", "المواد المقروءة", f"{int(stage_stats['read_p'].iloc[0])}", "صفحة", EMERALD)
        with c3: kpi_card("👥", "المدارسات والفعاليات", f"{stage_ev['ev_h'].iloc[0]:.1f}", "ساعة", SKY)
        with c4: kpi_card("🏆", "المسابقات المعقودة", f"{int(stage_comp['c_cnt'].iloc[0])}", "مسابقة", ROSE)

        st.write("---")
        tab1, tab2, tab3 = st.tabs(["📚 المقررات الدراسية", "👥 الفعاليات والمدارسات", "🎯 التخصصات المعنية"])
        
        with tab1:
            courses_df = get_data(f"SELECT title as 'اسم المقرر الدراسي', type as 'نوع المقرر', CASE WHEN type = 'مسموع' THEN duration_time ELSE CAST(pages_count AS TEXT) || ' صفحة' END as 'المدى / الحجم المقرّر' FROM Courses_Materials WHERE stage_id = {current_stage_id};")
            if not courses_df.empty:
                show_table(courses_df)
            else:
                st.caption("لا توجد مقررات مسجلة لهذه المرحلة.")
                
        with tab2:
            events_list_df = get_data(f"SELECT title as 'عنوان الفعالية', duration_time as 'المدة الزمنية' FROM Stage_Events WHERE stage_id = {current_stage_id};")
            if not events_list_df.empty:
                show_table(events_list_df)
            else:
                st.caption("لا توجد فعاليات مسجلة لهذه المرحلة.")
                
        with tab3:
            stage_specs = get_data(f"SELECT s.name as 'التخصص المعني بالدراسة' FROM Specialty_Stages ss JOIN Specialties s ON ss.specialty_id = s.specialty_id WHERE ss.stage_id = {current_stage_id};")
            show_table(stage_specs)
            
    except:
        st.warning("تأكد من إعدادات قاعدة البيانات لهذه المرحلة.")