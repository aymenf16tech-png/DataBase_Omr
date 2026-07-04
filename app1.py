import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =========================================================
# 1. إعدادات الصفحة العامة والهوية البصرية (الألوان أولاً)
# =========================================================
logo_path = "logo.jfif"

st.set_page_config(
    page_title="مشروع العمر للمصلحين",
    page_icon=logo_path if os.path.exists(logo_path) else "📚",
    layout="wide",
)

# تعريف الألوان في الأعلى لكي تراها جميع الدوال
NAVY_DARK = "#0f172a"
NAVY = "#1e293b"
NAVY_LIGHT = "#334155"
GOLD = "#d97706"
EMERALD = "#10b981"
SKY = "#38bdf8"
ROSE = "#f43f5e"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

CHART_PALETTE = [EMERALD, SKY, GOLD, "#a78bfa", ROSE, "#fb923c"]

# ⚠️ استبدل هذا الرابط برابط ملف الـ Google Sheets الخاص بك
SHEET_URL = "https://docs.google.com/spreadsheets/d/1tKLDo08oDTpxa9uCpHckN50DQDy4ALy50bgNsRcL2XA/edit?usp=sharing"

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
def get_google_sheet_url(sheet_name: str) -> str:
    """تحول رابط المعاينة إلى رابط تحميل مباشر بصيغة CSV لتبويب معين"""
    base_url = SHEET_URL.split("/edit")[0]
    return f"{base_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data(ttl=300)
def get_table(sheet_name: str) -> pd.DataFrame:
    """تجلب التبويب من Google Sheets وتحوله إلى DataFrame"""
    url = get_google_sheet_url(sheet_name)
    df = pd.read_csv(url)
    return df

def parse_duration_to_hours(duration_str):
    """تحول نصوص الوقت مثل 14:51:11 إلى ساعات عشرية بدلاً من تعبير SQL القديم"""
    try:
        if pd.isna(duration_str) or str(duration_str).strip() == "":
            return 0.0
        parts = list(map(int, str(duration_str).split(':')))
        if len(parts) == 3:
            return parts[0] + parts[1]/60.0 + parts[2]/3600.0
        return 0.0
    except:
        return 0.0

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
# 3. الترويسة الرئيسية والتحكم العلوي وجلب البيانات
# =========================================================
try:
    courses_df = get_table("Courses_Materials")
    events_df = get_table("Stage_Events")
    competitions_df = get_table("Competitions")
    stages_df = get_table("Stages")
    specialties_df = get_table("Specialties")
    spec_stages_df = get_table("Specialty_Stages")
except Exception as e:
    st.error("خطأ في الاتصال بـ Google Sheets. تأكد من أسماء التبويبات وصلاحية الرابط.")
    st.stop()

menu_col1, menu_col2, menu_col3 = st.columns([1, 4, 2])

with menu_col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=80)

with menu_col2:
    st.title("إحصاءات برنامج مشروع العمر")
  # حساب وعرض التواريخ ديناميكياً من جدول Stages
    try:
        # تصفية المراحل لاستبعاد المرحلة العامة رقم 100 لحساب دقيق للفترة المنهجية
        filtered_stages = stages_df[stages_df['stage_id'] != 100].copy()
        
        # التأكد من تحويل الأعمدة إلى نصوص وتصفية القيم الفارغة
        filtered_stages = filtered_stages.dropna(subset=['start_date_gregorian', 'end_date_gregorian'])
        
        if not filtered_stages.empty:
            # جلب أقل تاريخ بداية وأعلى تاريخ نهاية
            first_date_raw = filtered_stages['start_date_gregorian'].min()
            last_date_raw = filtered_stages['end_date_gregorian'].max()
            
            # تعديل التنسيق هنا ليخرج بصيغة (السنة/الشهر/اليوم) بشكل صارم ومحمي هندسياً
            fd = datetime.strptime(str(first_date_raw).strip(), "%Y-%m-%d").strftime("%Y/%m/%d")
            ld = datetime.strptime(str(last_date_raw).strip(), "%Y-%m-%d").strftime("%Y/%m/%d")

        
            st.markdown(
                f"<div class='section-badge'>🗓️ الإحصاء من  "
                f"<span class='num-date'>{fd}</span> إلى <span class='num-date'>{ld}</span></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div class='section-badge'>🗓️ يشمل جميع المراحل المعتمدة</div>", unsafe_allow_html=True)
    except Exception as e:
        st.markdown("<div class='section-badge'>🗓️ يشمل جميع المراحل المعتمدة</div>", unsafe_allow_html=True)

with menu_col3:
    st.write("")
    if st.button("🔄 تحديث البيانات اللحظية", use_container_width=True):
        st.cache_data.clear()
        st.toast("تم تحديث وجلب البيانات بنجاح! 🚀")
        st.rerun()

st.write("---")

# =========================================================
# 4. الإحصائيات العامة الكلية للمشروع
# =========================================================
st.markdown("### 📊 الإحصائيات العامة لبرنامج مشروع العمر  ")
try:
    # حساب الساعات المسموعة والصفحات المقروءة
    courses_df['hours'] = courses_df['duration_time'].apply(parse_duration_to_hours)
    audio_hours = courses_df[courses_df['type'] == 'مسموع']['hours'].sum()
    read_pages = courses_df[courses_df['type'] == 'مقروء']['pages_count'].sum()

    # حساب ساعات الفعاليات والمسابقات
    events_df['hours'] = events_df['duration_time'].apply(parse_duration_to_hours)
    ev_hours = events_df['hours'].sum()
    c_count = competitions_df['contests_count'].sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("🎙️", "إجمالي الساعات المسموعة", f"{audio_hours:.1f}", "ساعة", GOLD)
    with c2: kpi_card("📖", "إجمالي الصفحات المقروءة", f"{int(read_pages)}", "صفحة", EMERALD)
    with c3: kpi_card("👥", "إجمالي ساعات المدارسات و الفعاليات", f"{ev_hours:.1f}", "ساعة", SKY)
    with c4: kpi_card("🏆", "إجمالي المسابقات", f"{int(c_count)}", "مسابقة", ROSE)
except Exception as e:
    st.error(f"حدث خطأ أثناء حساب الإحصائيات: {e}")

st.write("---")

# =========================================================
# 5. ✨ البرنامج العام والفعاليات المشتركة
# =========================================================
st.markdown("### ✨ البرنامج العام والفعاليات المشتركة")
try:
    gen_events_df = events_df[events_df['stage_id'] == 100][['title', 'duration_time']].copy()
    gen_events_df.columns = ['عنوان الفعالية', 'المدة الزمنية']
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
st.markdown("### 🗂️استعراض الفرز والتقارير التفصيلية للبرنامج")
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
        specialties_options = specialties_df['name'].tolist()
        selected_spec = st.selectbox("👤 حدد التخصص المراد استعراض إحصاءاته:", specialties_options)
        
        spec_row = specialties_df[specialties_df['name'] == selected_spec]
        if not spec_row.empty:
            spec_id = spec_row['specialty_id'].iloc[0]
            
            allowed_stages = spec_stages_df[spec_stages_df['specialty_id'] == spec_id]['stage_id'].tolist()
            allowed_stages = [x for x in allowed_stages if x != 100]
            
            spec_courses = courses_df[courses_df['stage_id'].isin(allowed_stages)].copy()
            spec_courses['hours'] = spec_courses['duration_time'].apply(parse_duration_to_hours)
            spec_audio_h = spec_courses[spec_courses['type'] == 'مسموع']['hours'].sum()
            spec_read_p = spec_courses[spec_courses['type'] == 'مقروء']['pages_count'].sum()
            
            spec_events = events_df[events_df['stage_id'].isin(allowed_stages)].copy()
            spec_events['hours'] = spec_events['duration_time'].apply(parse_duration_to_hours)
            spec_ev_h = spec_events['hours'].sum()
            
            spec_c_cnt = competitions_df[competitions_df['stage_id'].isin(allowed_stages)]['contests_count'].sum()

            sp1, sp2, sp3, sp4 = st.columns(4)
            with sp1: kpi_card("🎙️", "من المواد المسموعة  ", f"{spec_audio_h:.1f}", "ساعة", GOLD)
            with sp2: kpi_card("📖", "من الصفحات المقروءة  ", f"{int(spec_read_p)}", "صفحة", EMERALD)
            with sp3: kpi_card("👥", "من المدارسات و الفعاليات", f"{spec_ev_h:.1f}", "ساعة", SKY)
            with sp4: kpi_card("🏆", "من المسابقات المعقودة", f"{int(spec_c_cnt)}", "مسابقة", ROSE)

            st.markdown(f"##### 📋 المراحل الدراسية لتخصص ({selected_spec})")
            spec_stages_df_view = stages_df[stages_df['stage_id'].isin(allowed_stages)][['name', 'start_date_gregorian', 'end_date_gregorian']].copy()
            spec_stages_df_view.columns = ['اسم المرحلة', 'تاريخ البداية', 'تاريخ الانتهاء']
            
            spec_stages_df_view['تاريخ البداية'] = spec_stages_df_view['تاريخ البداية'].apply(lambda x: datetime.strptime(str(x).strip(), "%Y-%m-%d").strftime("%Y/%m/%d") if pd.notna(x) else x)
            spec_stages_df_view['تاريخ الانتهاء'] = spec_stages_df_view['تاريخ الانتهاء'].apply(lambda x: datetime.strptime(str(x).strip(), "%Y-%m-%d").strftime("%Y/%m/%d") if pd.notna(x) else x)
            
            show_table(spec_stages_df_view)
    except Exception as e:
        st.warning("لا توجد بيانات مسجلة حالياً لهذا التخصص.")

elif st.session_state.view_mode == 'stage':
    st.markdown("#### 🎯 الفرز والإحصاء التفصيلي حسب المرحلة الدراسية")
    try:
        stages_options = stages_df[stages_df['stage_id'] != 100]['name'].tolist()
        selected_stage = st.selectbox("🎯 حدد المرحلة الدراسية المعنية:", stages_options)
        
        stage_row = stages_df[stages_df['name'] == selected_stage]
        if not stage_row.empty:
            current_stage_id = int(stage_row['stage_id'].iloc[0])

            stage_courses = courses_df[courses_df['stage_id'] == current_stage_id].copy()
            stage_courses['hours'] = stage_courses['duration_time'].apply(parse_duration_to_hours)
            stage_audio_h = stage_courses[stage_courses['type'] == 'مسموع']['hours'].sum()
            stage_read_p = stage_courses[stage_courses['type'] == 'مقروء']['pages_count'].sum()

            stage_events = events_df[events_df['stage_id'] == current_stage_id].copy()
            stage_events['hours'] = stage_events['duration_time'].apply(parse_duration_to_hours)
            stage_ev_h = stage_events['hours'].sum()

            stage_c_cnt = competitions_df[competitions_df['stage_id'] == current_stage_id]['contests_count'].sum()

            c1, c2, c3, c4 = st.columns(4)
            with c1: kpi_card("🎙️", "ساعات الاستماع المقررة ", f"{stage_audio_h:.1f}", "ساعة", GOLD)
            with c2: kpi_card("📖", "صفحات القراءة المقررة ", f"{int(stage_read_p)}", "صفحة", EMERALD)
            with c3: kpi_card("👥", "ساعات المدارسات و الفعاليات", f"{stage_ev_h:.1f}", "ساعة", SKY)
            with c4: kpi_card("🏆", "المسابقات المقررة", f"{int(stage_c_cnt)}", "مسابقة", ROSE)

            st.write("---")
            tab1, tab2, tab3 = st.tabs(["📚 المقررات الدراسية", "👥 الفعاليات والمدارسات", "🎯 التخصصات المعنية"])
            
            with tab1:
                # 🛠️ إصلاح المشكلة هنا: بناء عمود ذكي يعتمد على نوع المقرر
                def build_size_column(row):
                    if row['type'] == 'مسموع':
                        return str(row['duration_time'])
                    elif row['type'] == 'مقروء':
                        return f"{int(row['pages_count'])} صفحة"
                    return ""

                # تطبيق الدالة الذكية لملء عمود الحجم/المدى بشكل صحيح
                stage_courses['المدى / الحجم المقرّر'] = stage_courses.apply(build_size_column, axis=1)
                
                view_c = stage_courses[['title', 'type', 'المدى / الحجم المقرّر']].copy()
                view_c.columns = ['اسم المقرر الدراسي', 'نوع المقرر', 'المدى / الحجم المقرّر']
                
                if not view_c.empty:
                    show_table(view_c)
                else:
                    st.caption("لا توجد مقررات مسجلة لهذه المرحلة.")
                    
            with tab2:
                view_e = stage_events[['title', 'duration_time']].copy()
                view_e.columns = ['عنوان الفعالية', 'المدة الزمنية']
                if not view_e.empty:
                    show_table(view_e)
                else:
                    st.caption("لا توجد فعاليات مسجلة لهذه المرحلة.")
                    
            with tab3:
                allowed_specs = spec_stages_df[spec_stages_df['stage_id'] == current_stage_id]['specialty_id'].tolist()
                view_s = specialties_df[specialties_df['specialty_id'].isin(allowed_specs)][['name']].copy()
                view_s.columns = ['التخصص المعني بالدراسة']
                show_table(view_s)
    except Exception as e:
        st.error(f"حدث خطأ أثناء الفرز: {e}")