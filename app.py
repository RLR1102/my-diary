import os
import time
import shutil
import pandas as pd
import streamlit as st
from datetime import datetime
import extra_streamlit_components as stx  # Подключаем работу с куки

# Настройка интерфейса под мобильные экраны
st.set_page_config(
    page_title="Электронный Журнал", page_icon="🏫", layout="centered"
)

# --- МЕНЕДЖЕР КУКИ (ИСПРАВЛЕНО: УБРАН ДЕКОРАТОР КЭША) ---
def get_cookie_manager():
    return stx.CookieManager()

cookie_manager = get_cookie_manager()

# --- АДАПТИВНЫЙ SMARTPHONE СТИЛЬ ДЛЯ СВЕТЛОЙ И ТЕМНОЙ ТЕМЫ ---
st.markdown(
    """
    <style>
    #GithubIcon { visibility: hidden !important; display: none !important; }
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK { display: none !important; }
    [data-testid="stSidebar"] { min-width: 250px; max-width: 280px; }
    
    .report-card-header { margin-top: 15px; margin-bottom: 10px; color: var(--text-color); font-weight: bold; font-size: 1.2rem; }
    .grade-badge { font-size: 18px; letter-spacing: 2px; color: #2C3E50; font-weight: bold; background-color: #F8F9FA; padding: 3px 8px; border-radius: 5px; border: 1px solid #E2E8F0; }
    
    .leaderboard-box { 
        padding: 10px; border-radius: 8px; margin-bottom: 10px; text-align: center; font-size: 0.9rem;
        color: var(--text-color); background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    .chat-bubble { 
        padding: 10px; border-radius: 10px; margin-bottom: 5px; font-size: 0.95rem; line-height: 1.3;
        color: var(--text-color); background-color: var(--secondary-background-color);
    }
    .chat-user { font-weight: bold; color: #3498DB; }
    .chat-teacher { font-weight: bold; color: #E74C3C; }
    .chat-zavuch { font-weight: bold; color: #F1C40F; }
    
    .mobile-data-card {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.15);
        font-size: 0.85rem;
        line-height: 1.4;
        color: var(--text-color);
    }
    .hw-card { padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid rgba(128, 128, 128, 0.2); background-color: var(--background-color); }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- ФАЙЛЫ БАЗЫ ДАННЫХ И МЕДИА ---
DB_FILE = "school_journal.csv"
STUDENTS_FILE = "students_passwords.csv"
TEACHERS_FILE = "teachers_passwords.csv"
ASSIGNMENTS_FILE = "assignments.csv"
CHAT_FILE = "school_chat.csv"
HOMEWORK_FILE = "school_homework.csv"
MEDIA_DIR = "chat_media"

if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

if "password" in st.secrets:
    ZAVUCH_PASSWORD = st.secrets["password"]
else:
    ZAVUCH_PASSWORD = "Armanboss"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["Оценка"] = df["Оценка"].astype(str)
        if "Дата" not in df.columns: df["Дата"] = datetime.now().strftime("%Y-%m-%d")
        return df
    return pd.DataFrame(columns=["Ученик", "Предмет", "Оценка", "Замечание", "Учитель", "Дата"])

def load_students():
    if os.path.exists(STUDENTS_FILE): return pd.read_csv(STUDENTS_FILE)
    return pd.DataFrame(columns=["Ученик", "Пароль"])

def load_teachers():
    if os.path.exists(TEACHERS_FILE): return pd.read_csv(TEACHERS_FILE)
    return pd.DataFrame(columns=["Учитель", "Пароль"])

def load_assignments():
    if os.path.exists(ASSIGNMENTS_FILE): return pd.read_csv(ASSIGNMENTS_FILE)
    return pd.DataFrame(columns=["Предмет", "Учитель"])

def load_chat():
    if os.path.exists(CHAT_FILE): 
        df = pd.read_csv(CHAT_FILE)
        if "Медиа" not in df.columns: df["Медиа"] = ""
        return df
    return pd.DataFrame(columns=["Отправитель", "Роль", "Сообщение", "Медиа"])

def load_homework():
    if os.path.exists(HOMEWORK_FILE): return pd.read_csv(HOMEWORK_FILE)
    return pd.DataFrame(columns=["ID", "Предмет", "Учитель", "Задание", "Дедлайн", "Ученик", "Статус", "Ответ"])

if "journal" not in st.session_state: st.session_state.journal = load_data()
if "students_df" not in st.session_state: st.session_state.students_df = load_students()
if "teachers_df" not in st.session_state: st.session_state.teachers_df = load_teachers()
if "assignments" not in st.session_state: st.session_state.assignments = load_assignments()
if "chat_df" not in st.session_state: st.session_state.chat_df = load_chat()
if "homework_df" not in st.session_state: st.session_state.homework_df = load_homework()

# Инициализация базовых флагов
for key, default in [("auth_success", False), ("is_zavuch", False), ("is_teacher", False), ("current_user_name", ""), ("user_role_label", "Ученик"), ("chat_limit", "Безлимитно"), ("journal_limit", "Безлимитно")]:
    if key not in st.session_state: st.session_state[key] = default

if "last_viewed_chat_len" not in st.session_state:
    st.session_state.last_viewed_chat_len = len(st.session_state.chat_df)

# Пытаемся считать куки «вечного входа» с устройства пользователя
saved_user = cookie_manager.get("saved_user")
saved_role = cookie_manager.get("saved_role")

if saved_user and saved_role and not st.session_state.auth_success:
    st.session_state.auth_success = True
    st.session_state.current_user_name = saved_user
    st.session_state.user_role_label = saved_role
    if saved_role == "Завуч": st.session_state.is_zavuch = True
    elif saved_role == "Учитель": st.session_state.is_teacher = True

def show_chat_notification():
    current_len = len(st.session_state.chat_df)
    unread = current_len - st.session_state.last_viewed_chat_len
    if unread > 0: st.info(f"💬 В мессенджере {unread} новых сообщений!")

def render_school_chat():
    st.session_state.last_viewed_chat_len = len(st.session_state.chat_df)
    st.subheader("💬 Школьный мессенджер с Медиа")
    
    with st.form("chat_form", clear_on_submit=True):
        user_msg = st.text_input("Введите сообщение:")
        uploaded_file = st.file_uploader("Прикрепить фото или видео 📎", type=["png", "jpg", "jpeg", "mp4", "mov"])
        submit_msg = st.form_submit_button("🚀 Отправить")
        
        if submit_msg and (user_msg.strip() or uploaded_file is not None):
            media_path = ""
            if uploaded_file is not None:
                file_ext = os.path.splitext(uploaded_file.name)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                media_name = f"{timestamp}_{st.session_state.current_user_name}{file_ext}"
                media_path = os.path.join(MEDIA_DIR, media_name)
                with open(media_path, "wb") as f: f.write(uploaded_file.getbuffer())
            
            new_post = pd.DataFrame({"Отправитель": [st.session_state.current_user_name], "Роль": [st.session_state.user_role_label], "Сообщение": [user_msg.strip()], "Медиа": [media_path]})
            updated_chat = pd.concat([st.session_state.chat_df, new_post], ignore_index=True)
            if st.session_state.chat_limit != "Безлимитно":
                updated_chat = updated_chat.tail(int(st.session_state.chat_limit))
            st.session_state.chat_df = updated_chat
            st.session_state.chat_df.to_csv(CHAT_FILE, index=False)
            st.rerun()
    
    st.markdown("---")
    if st.session_state.chat_df.empty: st.caption("_Здесь пока пусто._")
    else:
        for idx, row in st.session_state.chat_df.iloc[::-1].iterrows():
            role = row["Роль"]
            sender = row["Отправитель"]
            msg = row["Сообщение"]
            media = row["Медиа"] if "Медиа" in row and pd.notna(row["Медиа"]) else ""
            if role == "Завуч": st.markdown(f"<div class='chat-bubble' style='border-left: 5px solid #F1C40F;'><span class='chat-zavuch'>👑 [Завуч]</span>: {msg}</div>", unsafe_allow_html=True)
            elif role == "Учитель": st.markdown(f"<div class='chat-bubble' style='border-left: 5px solid #E74C3C;'><span class='chat-teacher'>👓 Уч. {sender}</span>: {msg}</div>", unsafe_allow_html=True)
            else: st.markdown(f"<div class='chat-bubble' style='border-left: 5px solid #3498DB;'><span class='chat-user'>👤 {sender}</span>: {msg}</div>", unsafe_allow_html=True)
            if media and os.path.exists(media):
                ext = os.path.splitext(media).lower()
                if ext in [".png", ".jpg", ".jpeg"]: st.image(media, use_container_width=True)
                elif ext in [".mp4", ".mov"]: st.video(media)

# --- ИНТЕРФЕЙС БОКОВОЙ ПАНЕЛИ АВТОРИЗАЦИИ ---
st.sidebar.title("🔐 Авторизация")

if st.session_state.auth_success:
    st.sidebar.success(f"Вы вошли как: {st.session_state.current_user_name} ({st.session_state.user_role_label})")
    if st.sidebar.button("🚪 Выйти из аккаунта"):
        try:
            cookie_manager.delete("saved_user", key="delete_cookie_user")
        except Exception:
            pass
            
        try:
            cookie_manager.delete("saved_role", key="delete_cookie_role")
        except Exception:
            pass
            
        st.session_state.clear()
        time.sleep(0.3)
        st.rerun()
else:
    role_choice = st.sidebar.radio("Кто вы?", ["Ученик", "Учитель", "Завуч (Управление)"])

    if role_choice == "Завуч (Управление)":
        password = st.sidebar.text_input("Пароль Завуча", type="password")
        if password == ZAVUCH_PASSWORD:
            st.session_state.is_zavuch, st.session_state.is_teacher, st.session_state.auth_success = True, False, True
            st.session_state.current_user_name, st.session_state.user_role_label = "Завуч", "Завуч"
            # ИСПРАВЛЕНО: Добавлены уникальные ключи для записи куки завуча
            cookie_manager.set("saved_user", "Завуч", max_age=2592000, key="set_cookie_z_user")
            cookie_manager.set("saved_role", "Завуч", max_age=2592000, key="set_cookie_z_role")
            time.sleep(0.3)
            st.rerun()
        elif password != "": st.sidebar.error("Неверный пароль!")

    elif role_choice == "Учитель":
        list_teachers = st.session_state.teachers_df["Учитель"].tolist()
        if not list_teachers: st.sidebar.warning("Учителя еще не добавлены завучем.")
        else:
            teacher_sel = st.sidebar.selectbox("Выберите свое имя:", ["-- Выберите --"] + list_teachers)
            if teacher_sel != "-- Выберите --":
                t_password = st.sidebar.text_input("Введите личный пароль", type="password", key="t_pass")
                correct_pass = st.session_state.teachers_df[st.session_state.teachers_df["Учитель"] == teacher_sel]["Пароль"].values
                if len(correct_pass) > 0 and str(t_password) == str(correct_pass):
                    st.session_state.is_teacher, st.session_state.is_zavuch, st.session_state.auth_success = True, False, True
                    st.session_state.current_user_name, st.session_state.user_role_label = teacher_sel, "Учитель"
                    # ИСПРАВЛЕНО: Добавлены уникальные ключи для записи куки учителя
                    cookie_manager.set("saved_user", teacher_sel, max_age=2592000, key="set_cookie_t_user")
                    cookie_manager.set("saved_role", "Учитель", max_age=2592000, key="set_cookie_t_role")
                    time.sleep(0.3)
                    st.rerun()
                elif t_password != "": st.sidebar.error("Неверный пароль учителя!")

    else:
        list_students = st.session_state.students_df["Ученик"].tolist()
        if not list_students: st.sidebar.warning("В базе пока нет учеников.")
        else:
            student_sel = st.sidebar.selectbox("Выберите ваше имя:", ["-- Выберите --"] + list_students)
            if student_sel != "-- Выберите --":
                s_password = st.sidebar.text_input("Введите личный пароль ученика", type="password", key="s_pass")
                correct_s_pass = st.session_state.students_df[st.session_state.students_df["Ученик"] == student_sel]["Пароль"].values
                if len(correct_s_pass) > 0 and str(s_password) == str(correct_s_pass):
                    st.session_state.auth_success, st.session_state.is_zavuch, st.session_state.is_teacher = True, False, False
                    st.session_state.current_user_name, st.session_state.user_role_label = student_sel, "Ученик"
                    # ИСПРАВЛЕНО: Добавлены уникальные ключи для записи куки ученика
                    cookie_manager.set("saved_user", student_sel, max_age=2592000, key="set_cookie_s_user")
                    cookie_manager.set("saved_role", "Ученик", max_age=2592000, key="set_cookie_s_role")
                    time.sleep(0.3)
                    st.rerun()
                elif s_password != "": st.sidebar.error("Неверный пароль ученика!")



if st.session_state.is_zavuch and st.session_state.auth_success:
    st.title("👔 Кабинет Завуча")
    show_chat_notification()
    st.markdown("---")

    t1, t2, t3, t4, t5 = st.tabs(["⚙️ Структура", "📝 База", "✍️ Оценки", "📊 Аналитика учеников", "💬 Чат"])

    with t1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👤 Регистрация")
            p_type = st.selectbox("Кого добавить?", ["Ученик", "Учитель"])
            new_name = st.text_input("ФИО")
            new_pass = st.text_input("Пароль", type="password", key="reg_p")
            if st.button("Внести в списки"):
                if new_name.strip() and new_pass.strip():
                    if p_type == "Ученик" and new_name not in st.session_state.students_df["Ученик"].tolist():
                        st.session_state.students_df = pd.concat([st.session_state.students_df, pd.DataFrame({"Ученик": [new_name], "Пароль": [new_pass]})], ignore_index=True)
                        st.session_state.students_df.to_csv(STUDENTS_FILE, index=False)
                        st.toast("Ученик внесен!"); time.sleep(1); st.rerun()
                    elif p_type == "Учитель" and new_name not in st.session_state.teachers_df["Учитель"].tolist():
                        st.session_state.teachers_df = pd.concat([st.session_state.teachers_df, pd.DataFrame({"Учитель": [new_name], "Пароль": [new_pass]})], ignore_index=True)
                        st.session_state.teachers_df.to_csv(TEACHERS_FILE, index=False)
                        st.toast("Учитель добавлен!"); time.sleep(1); st.rerun()
        with col2:
            st.subheader("📚 Предметы")
            new_sub = st.text_input("Название предмета")
            list_teachers = st.session_state.teachers_df["Учитель"].tolist()
            assigned_teacher = st.selectbox("Учитель:", list_teachers) if list_teachers else None
            if st.button("Закрепить предмет"):
                if new_sub.strip() and assigned_teacher:
                    st.session_state.assignments = pd.concat([st.session_state.assignments, pd.DataFrame({"Предмет": [new_sub], "Учитель": [assigned_teacher]})], ignore_index=True)
                    st.session_state.assignments.to_csv(ASSIGNMENTS_FILE, index=False)
                    st.toast("Предмет создан!"); time.sleep(1); st.rerun()
        
        st.markdown("---")
        st.subheader("🧹 Оптимизация памяти (Лимиты очистки)")
        opt_limits = ["Безлимитно", "20", "50", "100", "200"]
        
        chosen_j_limit = st.selectbox("Автоочистка журнала (лимит оценок):", opt_limits, index=opt_limits.index(str(st.session_state.journal_limit)) if str(st.session_state.journal_limit) in opt_limits else 0)
        if chosen_j_limit != st.session_state.journal_limit:
            st.session_state.journal_limit = chosen_j_limit
            st.toast(f"Лимит оценок: {chosen_j_limit}")
            
        chosen_limit = st.selectbox("Автоочистка мессенджера (лимит сообщений):", opt_limits, index=opt_limits.index(str(st.session_state.chat_limit)) if str(st.session_state.chat_limit) in opt_limits else 0)
        if chosen_limit != st.session_state.chat_limit:
            st.session_state.chat_limit = chosen_limit
            st.toast(f"Лимит чата: {chosen_limit}")
            
        if st.button("🗑️ Стереть всю переписку и медиа"):
            st.session_state.chat_df = pd.DataFrame(columns=["Отправитель", "Роль", "Сообщение", "Медиа"])
            st.session_state.chat_df.to_csv(CHAT_FILE, index=False)
            if os.path.exists(MEDIA_DIR): shutil.rmtree(MEDIA_DIR); os.makedirs(MEDIA_DIR)
            st.toast("Чат полностью очищен! 🧹"); time.sleep(1); st.rerun()

    with t2:
        st.subheader("🔄 Редактирование")
        edit_type = st.radio("Что изменить?", ["Ученика", "Учителя"])
        if edit_type == "Ученика" and not st.session_state.students_df.empty:
            list_st = st.session_state.students_df["Ученик"].tolist()
            student_to_edit = st.selectbox("Выберите ученика:", list_st)
            old_s_pass = st.session_state.students_df[st.session_state.students_df["Ученик"] == student_to_edit]["Пароль"].values
            updated_name = st.text_input("Новое ФИО", value=student_to_edit)
            updated_pass = st.text_input("Новый пароль", value=str(old_s_pass[0]) if len(old_s_pass)>0 else "")
            if st.button("Сохранить ученика"):
                st.session_state.students_df.loc[st.session_state.students_df["Ученик"] == student_to_edit, ["Ученик", "Пароль"]] = [updated_name, updated_pass]
                st.session_state.students_df.to_csv(STUDENTS_FILE, index=False)
                st.session_state.journal.loc[st.session_state.journal["Ученик"] == student_to_edit, "Ученик"] = updated_name
                st.session_state.journal.to_csv(DB_FILE, index=False)
                st.toast("Обновлено!"); time.sleep(1); st.rerun()
        elif edit_type == "Учителя" and not st.session_state.teachers_df.empty:
            list_tch = st.session_state.teachers_df["Учитель"].tolist()
            teacher_to_edit = st.selectbox("Выберите учителя:", list_tch)
            old_t_pass = st.session_state.teachers_df[st.session_state.teachers_df["Учитель"] == teacher_to_edit]["Пароль"].values
            updated_t_name = st.text_input("Новое ФИО уч.", value=teacher_to_edit)
            updated_t_pass = st.text_input("Новый пароль уч.", value=str(old_t_pass[0]) if len(old_t_pass)>0 else "")
            if st.button("Сохранить учителя"):
                st.session_state.teachers_df.loc[st.session_state.teachers_df["Учитель"] == teacher_to_edit, ["Учитель", "Пароль"]] = [updated_t_name, updated_t_pass]
                st.session_state.teachers_df.to_csv(TEACHERS_FILE, index=False)
                st.toast("Учитель изменен!"); time.sleep(1); st.rerun()

    with t3:
        st.subheader("✍️ Выставление оценок Администрацией")
        list_all_subjects = st.session_state.assignments["Предмет"].tolist() if "Предмет" in st.session_state.assignments.columns else st.session_state.assignments["Predmet"].tolist()
        list_st = st.session_state.students_df["Ученик"].tolist()
        if list_st and list_all_subjects:
            z_col1, z_col2, z_col3 = st.columns(3)
            with z_col1: z_student = st.selectbox("Ученик", list_st, key="z_stu")
            with z_col2: z_subject = st.selectbox("Предмет", list_all_subjects, key="z_sub")
            with z_col3: z_grade = st.selectbox("Оценка", ["5", "4", "3", "2"], key="z_grd")
            z_date = st.date_input("Укажите дату:", datetime.now())
            z_comm = st.text_input("Замечание от Завуча", key="z_com")
            if st.button("Выставить оценку"):
                found_t = st.session_state.assignments[st.session_state.assignments["Предмет"] == z_subject]["Учитель"].values
                teacher_name = found_t[0] if len(found_t) > 0 else "Завуч"
                new_mark = pd.DataFrame({"Ученик": [z_student], "Предмет": [z_subject], "Оценка": [z_grade], "Замечание": [f"[Завуч] {z_comm}" if z_comm.strip() else "Выставлено администрацией"], "Учитель": [teacher_name], "Дата": [z_date.strftime("%Y-%m-%d")]})
                
                updated_journal = pd.concat([st.session_state.journal, new_mark], ignore_index=True)
                if st.session_state.journal_limit != "Безлимитно":
                    updated_journal = updated_journal.tail(int(st.session_state.journal_limit))
                st.session_state.journal = updated_journal
                st.session_state.journal.to_csv(DB_FILE, index=False)
                st.toast("Успешно добавлено!"); time.sleep(1); st.rerun()
                
    with t4:
        st.subheader("📊 Аналитика и Детальный поиск оценок")
        if st.session_state.journal.empty: st.info("В журнале еще нет оценок.")
        else:
            df_an = st.session_state.journal.copy()
            df_an["Оценка_Число"] = pd.to_numeric(df_an["Оценка"], errors="coerce")
            m1, m2, m3 = st.columns(3)
            m1.metric("📉 Средний балл", f"{df_an['Оценка_Число'].mean():.2f}")
            m2.metric("📋 Всего оценок", f"{len(df_an)} шт.")
            m3.metric("🚨 Двоек в базе", f"{(df_an['Оценка'] == '2').sum()} шт.")
            
            search_student = st.selectbox("Выберите ученика для фильтрации:", ["Все ученики"] + st.session_state.students_df["Ученик"].tolist())
            df_filtered = df_an.copy()
            if search_student != "Все ученики": df_filtered = df_filtered[df_filtered["Ученик"] == search_student]
            
            for _, row in df_filtered.sort_values(by="Дата", ascending=False).iterrows():
                st.markdown(f"<div class='mobile-data-card'>📅 <b>{row['Дата']}</b> | 👤 {row['Ученик']}<br>📖 <b>{row['Предмет']}</b>: <span class='grade-badge'>{row['Оценка']}</span><br>✍️ <i>Замечание: {row['Замечание']}</i><br>🎓 <i>Преподаватель: {row['Учитель']}</i></div>", unsafe_allow_html=True)
            
            sub_stats = df_an.groupby("Предмет")["Оценка_Число"].mean().reset_index().round(2)
            for _, row in sub_stats.iterrows():
                st.markdown(f"<div class='mobile-data-card'>📖 <b>{row['Предмет']}</b> <br>📊 Средний показатель успеваемости класса: <b>{row['Оценка_Число']}</b></div>", unsafe_allow_html=True)

    with t5: render_school_chat()

    if st.sidebar.button("🚨 Полный сброс всей школы"):
        for f in [DB_FILE, STUDENTS_FILE, TEACHERS_FILE, ASSIGNMENTS_FILE, CHAT_FILE, HOMEWORK_FILE]:
            if os.path.exists(f): os.remove(f)
        if os.path.exists(MEDIA_DIR): shutil.rmtree(MEDIA_DIR)
        cookie_manager.delete("saved_user")
        cookie_manager.delete("saved_role")
        st.session_state.clear(); st.rerun()
# --- ЭКРАН УЧИТЕЛЯ ---
elif st.session_state.is_teacher and st.session_state.auth_success:
    st.title(f"👓 Журнал преподавателя: {st.session_state.current_user_name}")
    show_chat_notification()
    st.markdown("---")
    t1, t2, t3 = st.tabs(["✍️ Журнал оценок", "📋 Выдать и проверить ДЗ", "💬 Чат школы"])
    
    with t1:
        my_subjects = st.session_state.assignments[st.session_state.assignments["Учитель"] == st.session_state.current_user_name]["Предмет"].tolist()
        list_st = st.session_state.students_df["Ученик"].tolist()
        if my_subjects and list_st:
            st.subheader("✍️ Выставление оценок")
            col1, col2, col3 = st.columns(3)
            with col1: s_student = st.selectbox("Ученик", list_st)
            with col2: s_subject = st.selectbox("Предмет", my_subjects)
            with col3: s_grade = st.selectbox("Оценка", ["5", "4", "3", "2"])
            s_date = st.date_input("Дата занятия:", datetime.now())
            s_comm = st.text_input("Замечание")
            if st.button("Записать в журнал"):
                new_mark = pd.DataFrame({"Ученик": [s_student], "Предмет": [s_subject], "Оценка": [s_grade], "Замечание": [s_comm.strip() if s_comm.strip() else "Нет замечаний"], "Учитель": [st.session_state.current_user_name], "Дата": [s_date.strftime("%Y-%m-%d")]})
                
                updated_journal = pd.concat([st.session_state.journal, new_mark], ignore_index=True)
                if st.session_state.journal_limit != "Безлимитно":
                    updated_journal = updated_journal.tail(int(st.session_state.journal_limit))
                st.session_state.journal = updated_journal
                st.session_state.journal.to_csv(DB_FILE, index=False)
                st.toast("Оценка выставлена! 📝"); time.sleep(1); st.rerun()

            st.markdown("---")
            st.markdown("### 📋 Мобильный лог выставленных вами оценок:")
            my_logged_marks = st.session_state.journal[st.session_state.journal["Учитель"] == st.session_state.current_user_name]
            if my_logged_marks.empty: st.caption("Вы еще не выставили ни одной оценки.")
            else:
                for _, row in my_logged_marks.sort_values(by="Дата", ascending=False).iterrows():
                    st.markdown(f"<div class='mobile-data-card'>📅 <b>{row['Дата']}</b> | Ученик: <b>{row['Ученик']}</b><br>📖 {row['Предмет']} -> <span class='grade-badge'>{row['Оценка']}</span><br>💬 <i>Выговор: {row['Замечание']}</i></div>", unsafe_allow_html=True)
    with t2:
        st.subheader("📋 Панель управления Домашними Заданиями")
        sub_tab1, sub_tab2 = st.tabs(["➕ Выдать новое ДЗ", "🔍 Проверка ответов учеников"])
        my_subjects = st.session_state.assignments[st.session_state.assignments["Учитель"] == st.session_state.current_user_name]["Предмет"].tolist()
        list_st = st.session_state.students_df["Ученик"].tolist()
        
        with sub_tab1:
            if my_subjects and list_st:
                hw_subj = st.selectbox("Выберите предмет:", my_subjects, key="hw_sub")
                hw_text = st.text_area("Текст домашнего задания:")
                hw_date = st.date_input("Срок сдачи (Дедлайн):", datetime.now())
                if st.button("Разослать домашку всему классу"):
                    if hw_text.strip():
                        new_hws = []
                        hw_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                        for s in list_st:
                            new_hws.append({"ID": hw_id, "Предмет": hw_subj, "Учитель": st.session_state.current_user_name, "Задание": hw_text.strip(), "Дедлайн": hw_date.strftime("%Y-%m-%d"), "Ученик": s, "Статус": "Не выполнено", "Ответ": ""})
                        st.session_state.homework_df = pd.concat([st.session_state.homework_df, pd.DataFrame(new_hws)], ignore_index=True)
                        st.session_state.homework_df.to_csv(HOMEWORK_FILE, index=False)
                        st.toast("Домашка отправлена классу! 🎒"); time.sleep(1); st.rerun()
                        
        with sub_tab2:
            st.markdown("### ⏳ Ответы на проверку:")
            pending_hw = st.session_state.homework_df[(st.session_state.homework_df["Учитель"] == st.session_state.current_user_name) & (st.session_state.homework_df["Статус"] == "На проверке")]
            if pending_hw.empty: st.caption("_Новых ответов от учеников пока нет._")
            else:
                for idx, row in pending_hw.iterrows():
                    with st.container():
                        st.markdown(f"<div class='hw-card'><b>Ученик:</b> {row['Ученик']}<br><b>Предмет:</b> {row['Предмет']}<br><b>Задание:</b> {row['Задание']}<br><b>💡 Ответ ученика:</b> <i>«{row['Ответ']}»</i></div>", unsafe_allow_html=True)
                        h_col1, h_col2 = st.columns(2)
                        if h_col1.button("🟢 Поставить 5 (Принять)", key=f"app_{idx}"):
                            st.session_state.homework_df.loc[idx, "Статус"] = "Выполнено (Оценка: 5)"
                            st.session_state.homework_df.to_csv(HOMEWORK_FILE, index=False)
                            new_mark = pd.DataFrame({"Ученик": [row['Ученик']], "Предмет": [row['Предмет']], "Оценка": ["5"], "Замечание": ["Отлично выполнено ДЗ!"], "Учитель": [st.session_state.current_user_name], "Дата": [datetime.now().strftime("%Y-%m-%d")]})
                            
                            updated_journal = pd.concat([st.session_state.journal, new_mark], ignore_index=True)
                            if st.session_state.journal_limit != "Безлимитно":
                                updated_journal = updated_journal.tail(int(st.session_state.journal_limit))
                            st.session_state.journal = updated_journal
                            st.session_state.journal.to_csv(DB_FILE, index=False)
                            st.toast("Задание зачтено, 5 выставлена!"); time.sleep(1); st.rerun()
                        if h_col2.button("🔴 Вернуть на доработку (Переделать)", key=f"rej_{idx}"):
                            st.session_state.homework_df.loc[idx, "Статус"] = "Не выполнено (Вернуть на доработку)"
                            st.session_state.homework_df.loc[idx, "Ответ"] = ""
                            st.session_state.homework_df.to_csv(HOMEWORK_FILE, index=False)
                            st.toast("Домашка возвращена ученику."); time.sleep(1); st.rerun()
    with t3: render_school_chat()
# --- ЭКРАН УЧЕНИКА / СТАРТОВЫЙ ЭКРАН ---
else:
    if not st.session_state.auth_success:
        st.title("🏫 Дневник Поведения")
        st.info("Пожалуйста, откройте боковое меню (полоски ☰ слева вверху), укажите роль и авторизуйтесь с паролем для вечного входа.")
    else:
        st.title(f"📱 Дневник ученика: {st.session_state.current_user_name}")
        show_chat_notification()
        st.markdown("---")
        tab_diary, tab_hw, tab_chat = st.tabs(["📊 Мой табель успеваемости", "📝 Моя домашка", "💬 Чат школы"])

        with tab_diary:
            if not st.session_state.journal.empty:
                df_l = st.session_state.journal.copy()
                st.markdown("### 🏆 Доска лидеров класса")
                l1, l2 = st.columns(2)
                f5 = df_l[df_l["Оценка"] == "5"]
                if not f5.empty:
                    b_st = f5["Ученик"].value_counts().idxmax()
                    l1.markdown(f"<div class='leaderboard-box'>🌟 <b>Сигма класса</b><br><span>{b_st}</span></div>", unsafe_allow_html=True)
                else: l1.markdown("<div class='leaderboard-box'>🌟 Отличник<br><i>Не определен</i></div>", unsafe_allow_html=True)
                f2 = df_l[df_l["Оценка"] == "2"]
                if not f2.empty:
                    w_st = f2["Ученик"].value_counts().idxmax()
                    l2.markdown(f"<div class='leaderboard-box'>🚨 <b>Хулиган недели</b><br><span>{w_st}</span></div>", unsafe_allow_html=True)
                else: l2.markdown("<div class='leaderboard-box'>🚨 Хулиган<br><i>Все ведут себя тихо</i></div>", unsafe_allow_html=True)

            my_data = st.session_state.journal[st.session_state.journal["Ученик"] == st.session_state.current_user_name].copy()
            if my_data.empty: st.success("🎉 У тебя идеальное поведение! Ни одного замечания.")
            else:
                my_data["Оценка_Число"] = pd.to_numeric(my_data["Оценка"], errors="coerce")
                st.markdown(f"<h3 class='report-card-header'>📊 Мой табель оценок (Всего: {len(my_data)} шт.)</h3>", unsafe_allow_html=True)
                for subj in my_data["Предмет"].unique():
                    sub_data = my_data[my_data["Предмет"] == subj]
                    g_list = ", ".join([f"{row['Оценка']} ({datetime.strptime(row['Дата'], '%Y-%m-%d').strftime('%d.%m')})" for _, row in sub_data.iterrows()])
                    raw_avg = sub_data["Оценка_Число"].mean()
                    s_avg = raw_avg if pd.notna(raw_avg) else 0.0
                    with st.expander(f"📖 {subj} (Средний балл: {s_avg:.2f})"):
                        st.markdown(f"Текущие оценки: <span class='grade-badge'>{g_list}</span>", unsafe_allow_html=True)
                        st.markdown("---")
                        st.markdown("📝 Комментарии и замечания:")
                        has_n = False
                        for _, row in sub_data.iterrows():
                            if pd.notna(row["Замечание"]) and str(row["Замечание"]).strip() and str(row["Замечание"]).lower() != "nan":
                                st.caption(f"• [{row['Дата']}] ({row['Учитель']}) Оценка {row['Оценка']}: «{row['Замечание'].strip()}»")
                                has_n = True
                        if not has_n: st.caption("*Замечания отсутствуют.*")

        with tab_hw:
            st.subheader("📝 Домашние задания для тебя")
            my_hws = st.session_state.homework_df[st.session_state.homework_df["Ученик"] == st.session_state.current_user_name]
            
            active_hws = my_hws[~my_hws["Статус"].str.contains("Выполнено", na=False)]
            completed_hws = my_hws[my_hws["Статус"].str.contains("Выполнено", na=False)]
            
            if active_hws.empty: st.success("🎉 Текущих заданий нет! Вся домашка выполнена.")
            else:
                for idx, row in active_hws.iterrows():
                    status_emoji = "❌" if "Не выполнено" in row["Статус"] else "⏳"
                    with st.expander(f"{status_emoji} {row['Предмет']} | До: {row['Дедлайн']} ({row['Статус']})"):
                        st.markdown(f"**Задание:** {row['Задание']}")
                        st.caption(f"Выдал учитель: {row['Учитель']}")
                        
                        if "Не выполнено" in row["Статус"]:
                            ans_text = st.text_input("Напишите ответ или ссылку на выполнение:", key=f"ans_{idx}")
                            if st.button("📢 Сдать на проверку", key=f"btn_{idx}"):
                                if ans_text.strip():
                                    st.session_state.homework_df.loc[idx, "Ответ"] = ans_text.strip()
                                    st.session_state.homework_df.loc[idx, "Статус"] = "На проверке"
                                    st.session_state.homework_df.to_csv(HOMEWORK_FILE, index=False)
                                    st.toast("Домашка улетела учителю!"); time.sleep(1); st.rerun()
                        else:
                            st.markdown(f"**Твой ответ на проверке:** *«{row['Ответ']}»*")
            
            if not completed_hws.empty:
                st.markdown("---")
                with st.expander("📦 Архив выполненных заданий"):
                    for _, row in completed_hws.iterrows():
                        st.markdown(f"🟢 **{row['Предмет']}** (Выполнено)<br><b>Задание:</b> {row['Задание']}<br>📝 <i>Ваш ответ: «{row['Ответ']}»</i><hr>", unsafe_allow_html=True)

        with tab_chat: render_school_chat()
