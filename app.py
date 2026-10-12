import os
import pandas as pd
import streamlit as st

# Настройка интерфейса под мобильные экраны
st.set_page_config(
    page_title="Электронный Журнал", page_icon="🏫", layout="centered"
)

# --- АДАПТИВНЫЙ SMARTPHONE СТИЛЬ + СКРЫТИЕ GITHUB ---
st.markdown(
    """
    <style>
    #GithubIcon { visibility: hidden !important; display: none !important; }
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stSidebar"] { min-width: 250px; max-width: 280px; }
    .report-card-header { margin-top: 15px; margin-bottom: 10px; color: #1E3A8A; font-weight: bold; font-size: 1.2rem; }
    .grade-badge { font-size: 18px; letter-spacing: 2px; color: #2C3E50; font-weight: bold; background-color: #F8F9FA; padding: 3px 8px; border-radius: 5px; border: 1px solid #E2E8F0; }
    .leaderboard-box { padding: 10px; border-radius: 8px; margin-bottom: 10px; text-align: center; font-size: 0.9rem; }
    .chat-bubble { padding: 10px; border-radius: 10px; margin-bottom: 5px; font-size: 0.95rem; line-height: 1.3; }
    .chat-user { font-weight: bold; color: #1E3A8A; }
    .chat-teacher { font-weight: bold; color: #D9534F; }
    .chat-zavuch { font-weight: bold; color: #F39C12; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- ФАЙЛЫ БАЗЫ ДАННЫХ ---
DB_FILE = "school_journal.csv"
STUDENTS_FILE = "students_passwords.csv"  # ТЕПЕРЬ CSV: хранит учеников и их пароли
TEACHERS_FILE = "teachers_passwords.csv"
ASSIGNMENTS_FILE = "assignments.csv"
CHAT_FILE = "school_chat.csv"

# 🔒 БЕЗОПАСНОСТЬ ЗАВУЧА
if "password" in st.secrets:
    ZAVUCH_PASSWORD = st.secrets["password"]
else:
    ZAVUCH_PASSWORD = "Armanboss"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["Оценка"] = df["Оценка"].astype(str)
        return df
    return pd.DataFrame(columns=["Ученик", "Предмет", "Оценка", "Замечание", "Учитель"])

def load_students():
    if os.path.exists(STUDENTS_FILE):
        return pd.read_csv(STUDENTS_FILE)
    return pd.DataFrame(columns=["Ученик", "Пароль"])

def load_teachers():
    if os.path.exists(TEACHERS_FILE):
        return pd.read_csv(TEACHERS_FILE)
    return pd.DataFrame(columns=["Учитель", "Пароль"])

def load_assignments():
    if os.path.exists(ASSIGNMENTS_FILE):
        return pd.read_csv(ASSIGNMENTS_FILE)
    return pd.DataFrame(columns=["Предмет", "Учитель"])

def load_chat():
    if os.path.exists(CHAT_FILE):
        return pd.read_csv(CHAT_FILE)
    return pd.DataFrame(columns=["Отправитель", "Роль", "Сообщение"])

# Инициализация сессий
if "journal" not in st.session_state:
    st.session_state.journal = load_data()
if "students_df" not in st.session_state:
    st.session_state.students_df = load_students()
if "teachers_df" not in st.session_state:
    st.session_state.teachers_df = load_teachers()
if "assignments" not in st.session_state:
    st.session_state.assignments = load_assignments()
if "chat_df" not in st.session_state:
    st.session_state.chat_df = load_chat()

# --- ВХОД В СИСТЕМУ С ПАРОЛЯМИ ---
st.sidebar.title("🔐 Авторизация")
role_choice = st.sidebar.radio("Кто вы?", ["Ученик", "Учитель", "Завуч (Управление)"])

is_zavuch = False
is_teacher = False
current_user_name = ""
auth_success = False
user_role_label = "Ученик"

if role_choice == "Завуч (Управление)":
    password = st.sidebar.text_input("Пароль Завуча", type="password")
    if password == ZAVUCH_PASSWORD:
        is_zavuch = True
        auth_success = True
        current_user_name = "Завуч"
        user_role_label = "Завуч"
        st.sidebar.success("Доступ в Главное Управление!")
    elif password != "":
        st.sidebar.error("Неверный пароль!")

elif role_choice == "Учитель":
    list_teachers = st.session_state.teachers_df["Учитель"].tolist()
    if not list_teachers:
        st.sidebar.warning("Учителя еще не добавлены завучем.")
    else:
        current_user_name = st.sidebar.selectbox("Выберите свое имя:", ["-- Выберите из списка --"] + list_teachers)
        if current_user_name != "-- Выберите из списка --":
            t_password = st.sidebar.text_input("Введите личный пароль", type="password", key="t_pass")
            correct_pass = st.session_state.teachers_df[st.session_state.teachers_df["Учитель"] == current_user_name]["Пароль"].values
            if len(correct_pass) > 0 and str(t_password) == str(correct_pass[0]):
                is_teacher = True
                auth_success = True
                user_role_label = "Учитель"
                st.sidebar.success("Журнал открыт!")
            elif t_password != "":
                st.sidebar.error("Неверный личный пароль!")

else:
    list_students = st.session_state.students_df["Ученик"].tolist()
    if not list_students:
        st.sidebar.warning("В базе пока нет учеников.")
    else:
        current_user_name = st.sidebar.selectbox("Выберите ваше имя:", ["-- Выберите из списка --"] + list_students)
        if current_user_name != "-- Выберите из списка --":
            s_password = st.sidebar.text_input("Введите личный пароль ученика", type="password", key="s_pass")
            correct_s_pass = st.session_state.students_df[st.session_state.students_df["Ученик"] == current_user_name]["Пароль"].values
            if len(correct_s_pass) > 0 and str(s_password) == str(correct_s_pass[0]):
                auth_success = True
                user_role_label = "Ученик"
                st.sidebar.success("Добро пожаловать!")
            elif s_password != "":
                st.sidebar.error("Неверный личный пароль!")
# --- ЭКРАН ЗАВУЧА (ГЛАВНОЕ УПРАВЛЕНИЕ) ---
if is_zavuch and auth_success:
    st.title("👔 Главный Кабинет Завуча")
    st.markdown("---")

    t1, t2, t3, t4, t5 = st.tabs(["⚙️ Создание структуры", "📝 Редактирование базы", "✍️ Выставить оценки", "📊 Улучшенная аналитика", "💬 Чат школы"])

    with t1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👤 Регистрация людей")
            p_type = st.selectbox("Кого добавить?", ["Ученик", "Учитель"])
            new_name = st.text_input("ФИО человека")
            new_pass = st.text_input("Задать личный пароль для входа", type="password", key="reg_p")
            
            if st.button("Внести в списки"):
                if new_name.strip() and new_pass.strip():
                    if p_type == "Ученик" and new_name not in st.session_state.students_df["Ученик"].tolist():
                        new_student_row = pd.DataFrame({"Ученик": [new_name], "Пароль": [new_pass]})
                        st.session_state.students_df = pd.concat([st.session_state.students_df, new_student_row], ignore_index=True)
                        st.session_state.students_df.to_csv(STUDENTS_FILE, index=False)
                        st.success(f"Ученик зачислен!")
                        st.rerun()
                    elif p_type == "Учитель" and new_name not in st.session_state.teachers_df["Учитель"].tolist():
                        new_teacher_row = pd.DataFrame({"Учитель": [new_name], "Пароль": [new_pass]})
                        st.session_state.teachers_df = pd.concat([st.session_state.teachers_df, new_teacher_row], ignore_index=True)
                        st.session_state.teachers_df.to_csv(TEACHERS_FILE, index=False)
                        st.success(f"Учитель нанят!")
                        st.rerun()
                elif not new_pass.strip():
                    st.error("Пароль не может быть пустым!")

        with col2:
            st.subheader("📚 Создание Предметов")
            new_sub = st.text_input("Название нового предмета")
            list_teachers = st.session_state.teachers_df["Учитель"].tolist()
            
            if list_teachers:
                assigned_teacher = st.selectbox("Назначить ведущего учителя:", list_teachers)
            else:
                assigned_teacher = None
                st.caption("_Сначала добавьте хотя бы одного учителя!_")

            if st.button("Утвердить дисциплину"):
                if new_sub.strip() and assigned_teacher:
                    if new_sub not in st.session_state.assignments["Предмет"].values.tolist():
                        new_assign = pd.DataFrame({"Предмет": [new_sub], "Учитель": [assigned_teacher]})
                        st.session_state.assignments = pd.concat([st.session_state.assignments, new_assign], ignore_index=True)
                        st.session_state.assignments.to_csv(ASSIGNMENTS_FILE, index=False)
                        st.success(f"Предмет '{new_sub}' закреплен!")
                        st.rerun()

    with t2:
        st.subheader("🔄 Редактирование личных данных")
        edit_type = st.radio("Что хотите изменить?", ["Изменить данные Ученика", "Изменить данные Учителя"])
        
        if edit_type == "Изменить данные Ученика":
            list_st = st.session_state.students_df["Ученик"].tolist()
            if not list_st:
                st.caption("Учеников пока нет.")
            else:
                student_to_edit = st.selectbox("Выберите ученика для изменения:", list_st)
                old_s_pass = st.session_state.students_df[st.session_state.students_df["Ученик"] == student_to_edit]["Пароль"].values
                
                updated_student_name = st.text_input("Новое ФИО ученика", value=student_to_edit)
                updated_student_pass = st.text_input("Новый пароль ученика", value=str(old_s_pass[0]))
                
                if st.button("Сохранить данные ученика"):
                    if updated_student_name.strip() and updated_student_pass.strip():
                        st.session_state.students_df.loc[st.session_state.students_df["Ученик"] == student_to_edit, ["Ученик", "Пароль"]] = [updated_student_name, updated_student_pass]
                        st.session_state.students_df.to_csv(STUDENTS_FILE, index=False)
                        st.session_state.journal.loc[st.session_state.journal["Ученик"] == student_to_edit, "Ученик"] = updated_student_name
                        st.session_state.journal.to_csv(DB_FILE, index=False)
                        st.success("Данные ученика успешно обновлены!")
                        st.rerun()
                        
        elif edit_type == "Изменить данные Учителя":
            list_teachers = st.session_state.teachers_df["Учитель"].tolist()
            if not list_teachers:
                st.caption("Учителей пока нет.")
            else:
                teacher_to_edit = st.selectbox("Выберите учителя для изменения:", list_teachers)
                old_pass = st.session_state.teachers_df[st.session_state.teachers_df["Учитель"] == teacher_to_edit]["Пароль"].values
                
                updated_teacher_name = st.text_input("Новое ФИО учителя", value=teacher_to_edit)
                updated_teacher_pass = st.text_input("Новый пароль учителя", value=str(old_pass[0]))
                
                if st.button("Сохранить данные учителя"):
                    if updated_teacher_name.strip() and updated_teacher_pass.strip():
                        st.session_state.teachers_df.loc[st.session_state.teachers_df["Учитель"] == teacher_to_edit, ["Учитель", "Пароль"]] = [updated_teacher_name, updated_teacher_pass]
                        st.session_state.teachers_df.to_csv(TEACHERS_FILE, index=False)
                        st.session_state.assignments.loc[st.session_state.assignments["Учитель"] == teacher_to_edit, "Учитель"] = updated_teacher_name
                        st.session_state.assignments.to_csv(ASSIGNMENTS_FILE, index=False)
                        st.session_state.journal.loc[st.session_state.journal["Учитель"] == teacher_to_edit, "Учитель"] = updated_teacher_name
                        st.session_state.journal.to_csv(DB_FILE, index=False)
                        st.success("Данные учителя успешно переписаны!")
                        st.rerun()
    with t3:
        st.subheader("✍️ Выставление оценок от лица Администрации")
        list_all_subjects = st.session_state.assignments["Предмет"].tolist()
        list_st = st.session_state.students_df["Ученик"].tolist()
        
        if not list_st or not list_all_subjects:
            st.info("ℹ️ Добавьте учеников и предметы во вкладке 'Создание структуры'.")
        else:
            z_col1, z_col2, z_col3 = st.columns(3)
            with z_col1:
                z_student = st.selectbox("Ученик", list_st, key="z_stu")
            with z_col2:
                z_subject = st.selectbox("Предмет", list_all_subjects, key="z_sub")
            with z_col3:
                z_grade = st.selectbox("Оценка", ["5", "4", "3", "2"], key="z_grd")
                
            z_comm = st.text_input("Замечание / Комментарий от Завуча", key="z_com")
            
            if st.button("Выставить оценку от Администрации"):
                found_teacher_arr = st.session_state.assignments[st.session_state.assignments["Предмет"] == z_subject]["Учитель"].values
                found_teacher = found_teacher_arr[0] if len(found_teacher_arr) > 0 else "Завуч"
                new_mark = pd.DataFrame({
                    "Ученик": [z_student],
                    "Предмет": [z_subject],
                    "Оценка": [z_grade],
                    "Замечание": [f"[Завуч] {z_comm}" if z_comm.strip() else "Выставлено администрацией"],
                    "Учитель": [found_teacher]
                })
                st.session_state.journal = pd.concat([st.session_state.journal, new_mark], ignore_index=True)
                st.session_state.journal.to_csv(DB_FILE, index=False)
                st.success("Оценка успешно внесена!")
                st.rerun()

    with t4:
        st.subheader("📊 Мониторинг успеваемости школы")
        if st.session_state.journal.empty:
            st.info("В журнале еще нет оценок для аналитики.")
        else:
            df_an = st.session_state.journal.copy()
            df_an["Оценка_Число"] = pd.to_numeric(df_an["Оценка"], errors="coerce")
            
            # ВИДЖЕТЫ ГЛАВНЫХ ПОКАЗАТЕЛЕЙ
            m1, m2, m3 = st.columns(3)
            m1.metric("📉 Средний балл школы", f"{df_an['Оценка_Число'].mean():.2f}")
            m2.metric("📋 Выставлено оценок", f"{len(df_an)} шт.")
            
            twos_count = (df_an["Оценка"] == "2").sum()
            m3.metric("🚨 Всего двоек", f"{twos_count} шт.")
            
            # Сводная таблица по предметам
            st.markdown("### 📚 Успеваемость по предметам:")
            sub_stats = df_an.groupby("Предмет")["Оценка_Число"].mean().reset_index().round(2)
            sub_stats.columns = ["Дисциплина", "Средний балл успеваемости"]
            st.dataframe(sub_stats, use_container_width=True, hide_index=True)
            
            # График распределения
            st.markdown("### 📊 Общая картина выданных оценок:")
            grade_counts = df_an["Оценка"].value_counts().reset_index()
            grade_counts.columns = ["Оценка", "Количество"]
            st.bar_chart(data=grade_counts, x="Оценка", y="Количество")

    if st.sidebar.button("🚨 Полный сброс всей школы"):
        for f in [DB_FILE, STUDENTS_FILE, TEACHERS_FILE, ASSIGNMENTS_FILE, CHAT_FILE]:
            if os.path.exists(f):
                os.remove(f)
        st.session_state.clear()
        st.rerun()

# --- ЭКРАН УЧИТЕЛЯ ---
elif is_teacher and auth_success:
    st.title(f"👓 Журнал преподавателя: {current_user_name}")
    st.markdown("---")

    t1, t2 = st.tabs(["✍️ Журнал оценок", "💬 Чат школы"])

    with t1:
        my_subjects = st.session_state.assignments[st.session_state.assignments["Учитель"] == current_user_name]["Permanent" if "Permanent" in st.session_state.assignments.columns else "Предмет"].tolist()
        list_st = st.session_state.students_df["Ученик"].tolist()

        if not my_subjects:
            st.warning("Завуч еще не закрепил за вами предметов!")
        elif not list_st:
            st.warning("В базе данных пока нет учеников.")
        else:
            st.subheader("✍️ Выставление оценок")
            col1, col2, col3 = st.columns(3)
            with col1:
                s_student = st.selectbox("Ученик", list_st)
            with col2:
                s_subject = st.selectbox("Предмет", my_subjects)
            with col3:
                s_grade = st.selectbox("Оценка", ["5", "4", "3", "2"])

            s_comm = st.text_input("Комментарий / Замечание")

            if st.button("Записать в журнал"):
                new_mark = pd.DataFrame({
                    "Ученик": [s_student],
                    "Предмет": [s_subject],
                    "Оценка": [s_grade],
                    "Замечание": [s_comm],
                    "Учитель": [current_user_name]
                })
                st.session_state.journal = pd.concat([st.session_state.journal, new_mark], ignore_index=True)
                st.session_state.journal.to_csv(DB_FILE, index=False)
                st.success("Оценка выставлена!")
                st.rerun()

            st.markdown("---")
            st.subheader("📋 История выставленных вами оценок")
            my_logged_marks = st.session_state.journal[st.session_state.journal["Учитель"] == current_user_name]
            if my_logged_marks.empty:
                st.caption("Вы еще не выставили ни одной оценки.")
            else:
                st.dataframe(my_logged_marks[["Ученик", "Предмет", "Оценка", "Замечание"]], use_container_width=True, hide_index=True)
# --- ЭКРАН УЧЕНИКА / СТАРТОВЫЙ ЭКРАН ---
else:
    if not auth_success:
        st.title("🏫 Дневник Поведения")
        st.markdown("### 🪧 Информационная доска")
        st.info("Пожалуйста, нажмите на стрелочку или кнопку меню (☰) в левом верхнем углу, выберите роль ученика/учителя и введите ваш персональный пароль для входа.")
    else:
        st.title(f"📱 Дневник ученика: {current_user_name}")
        st.markdown("---")

        tab_diary, tab_chat = st.tabs(["📊 Мой табель успеваемости", "💬 Чат школы"])

        with tab_diary:
            if not st.session_state.journal.empty:
                df_l = st.session_state.journal.copy()
                st.markdown("### 🏆 Доска лидеров класса")
                l1, l2 = st.columns(2)

                f5 = df_l[df_l["Оценка"] == "5"]
                if not f5.empty:
                    b_st = f5["Ученик"].value_counts().idxmax()
                    l1.markdown(f"<div class='leaderboard-box' style='background-color: #E8F8F5; border: 1px solid #A3E4D7;'>🌟 <b>Сигма класса</b><br><span style='color: #117864;'>{b_st}</span></div>", unsafe_allow_html=True)
                else:
                    l1.markdown("<div class='leaderboard-box' style='background-color: #F2F4F4;'>🌟 Отличник<br><i>Не определен</i></div>", unsafe_allow_html=True)

                f2 = df_l[df_l["Оценка"] == "2"]
                if not f2.empty:
                    w_st = f2["Ученик"].value_counts().idxmax()
                    l2.markdown(f"<div class='leaderboard-box' style='background-color: #FDEDEC; border: 1px solid #F5B7B1;'>🚨 <b>Хулиган недели</b><br><span style='color: #78281F;'>{w_st}</span></div>", unsafe_allow_html=True)
                else:
                    l2.markdown("<div class='leaderboard-box' style='background-color: #F2F4F4;'>🚨 Хулиган<br><i>Все ведут себя тихо</i></div>", unsafe_allow_html=True)

            my_data = st.session_state.journal[st.session_state.journal["Ученик"] == current_user_name].copy()

            if my_data.empty:
                st.balloons()
                st.success("У тебя идеальное поведение! Ни одного выговора или двойки.")
            else:
                my_data["Оценка_Число"] = pd.to_numeric(my_data["Оценка"], errors="coerce")
                total_m = len(my_data)

                st.markdown(f"<h3 class='report-card-header'>📊 Мой табель оценок (Всего: {total_m} шт.)</h3>", unsafe_allow_html=True)

                for subj in my_data["Предмет"].unique():
                    sub_data = my_data[my_data["Предмет"] == subj]
                    g_list = ", ".join(sub_data["Оценка"].astype(str).tolist())
                    s_avg = sub_data["Оценка_Число"].mean()

                    if s_avg >= 4.5:
                        col_s = "#2ECC71"
                    elif s_avg >= 3.6:
                        col_s = "#F39C12"
                    else:
                        col_s = "#E74C3C"

                    with st.expander(f"📖 {subj} (Средний балл: {s_avg:.2f})"):
                        st.markdown(f"Текущие оценки: <span class='grade-badge'>{g_list}</span>", unsafe_allow_html=True)
                        st.markdown("---")
                        st.markdown("📝 Комментарии и замечания:")
                        has_n = False
                        for _, row in sub_data.iterrows():
                            if pd.notna(row["Замечание"]) and str(row["Замечание"]).strip() and str(row["Замечание"]).lower() != "nan":
                                st.caption(f"• ({row['Учитель']}) Оценка {row['Оценка']}: «{row['Замечание'].strip()}»")
                                has_n = True
                        if not has_n:
                            st.caption("*Замечания отсутствуют.*")

# --- ОБЩИЙ ДВИЖОК МЕССЕНДЖЕРА ДЛЯ ВСЕХ ВКЛАДОК ЧАТА ---
if auth_success:
    target_tab = None
    if is_zavuch: target_tab = t5
    elif is_teacher: target_tab = t2
    else: target_tab = tab_chat
    
    if target_tab:
        with target_tab:
            st.subheader("💬 Школьная курилка (Общий мессенджер)")
            
            with st.form("chat_form", clear_on_submit=True):
                user_msg = st.text_input("Введите сообщение для всей школы:")
                submit_msg = st.form_submit_button("🚀 Отправить")
                
                if submit_msg and user_msg.strip():
                    new_post = pd.DataFrame({
                        "Отправитель": [current_user_name],
                        "Row" if "Row" in st.session_state.chat_df.columns else "Роль": [user_role_label],
                        "Сообщение": [user_msg.strip()]
                    })
                    st.session_state.chat_df = pd.concat([st.session_state.chat_df, new_post], ignore_index=True)
                    st.session_state.chat_df.to_csv(CHAT_FILE, index=False)
                    st.rerun()
            
            st.markdown("---")
            if st.session_state.chat_df.empty:
                st.caption("_Здесь пока никто не писал. Будь первым!_")
            else:
                for idx, row in st.session_state.chat_df.iloc[::-1].iterrows():
                    role = row["Row" if "Row" in st.session_state.chat_df.columns else "Роль"]
                    sender = row["Отправитель"]
                    msg = row["Сообщение"]
                    
                    if role == "Завуч":
                        st.markdown(f"<div class='chat-bubble' style='background-color: #FEF9E7; border-left: 5px solid #F39C12;'><span class='chat-zavuch'>👑 [Завуч]</span>: {msg}</div>", unsafe_allow_html=True)
                    elif role == "Учитель":
                        st.markdown(f"<div class='chat-bubble' style='background-color: #FDF2F4; border-left: 5px solid #D9534F;'><span class='chat-teacher'>👓 Уч. {sender}</span>: {msg}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='chat-bubble' style='background-color: #F4F6F7; border-left: 5px solid #1E3A8A;'><span class='chat-user'>👤 {sender}</span>: {msg}</div>", unsafe_allow_html=True)
