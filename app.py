import os
import time
import pandas as pd
import streamlit as st

# Настройка интерфейса под мобильные экраны
st.set_page_config(
    page_title="Электронный Журнал", page_icon="🏫", layout="centered"
)

# --- АДАПТИВНЫЙ SMARTPHONE СТИЛЬ (ИСПРАВЛЕННЫЙ) ---
st.markdown(
    """
    <style>
    #GithubIcon { visibility: hidden !important; display: none !important; }
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK { display: none !important; }
    /* Исправлено для мобильных: убран display:none, ломавший кнопку меню */
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
STUDENTS_FILE = "students_passwords.csv"
TEACHERS_FILE = "teachers_passwords.csv"
ASSIGNMENTS_FILE = "assignments.csv"
CHAT_FILE = "school_chat.csv"

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
# Инициализация сессий (Фикс сброса авторизации)
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

if "auth_success" not in st.session_state:
    st.session_state.auth_success = False
if "is_zavuch" not in st.session_state:
    st.session_state.is_zavuch = False
if "is_teacher" not in st.session_state:
    st.session_state.is_teacher = False
if "current_user_name" not in st.session_state:
    st.session_state.current_user_name = ""
if "user_role_label" not in st.session_state:
    st.session_state.user_role_label = "Ученик"

# Функция чата, вынесенная отдельно для стабильности вкладок
def render_school_chat():
    st.subheader("💬 Школьный мессенджер")
    with st.form("chat_form", clear_on_submit=True):
        user_msg = st.text_input("Введите сообщение:")
        submit_msg = st.form_submit_button("🚀 Отправить")
        
        if submit_msg and user_msg.strip():
            new_post = pd.DataFrame({
                "Отправитель": [st.session_state.current_user_name],
                "Роль": [st.session_state.user_role_label],
                "Сообщение": [user_msg.strip()]
            })
            st.session_state.chat_df = pd.concat([st.session_state.chat_df, new_post], ignore_index=True)
            st.session_state.chat_df.to_csv(CHAT_FILE, index=False)
            st.rerun()
    
    st.markdown("---")
    if st.session_state.chat_df.empty:
        st.caption("_Здесь пока никто не писал._")
    else:
        for idx, row in st.session_state.chat_df.iloc[::-1].iterrows():
            role = row["Роль"]
            sender = row["Отправитель"]
            msg = row["Сообщение"]
            
            if role == "Завуч":
                st.markdown(f"<div class='chat-bubble' style='background-color: #FEF9E7; border-left: 5px solid #F39C12;'><span class='chat-zavuch'>👑 [Завуч]</span>: {msg}</div>", unsafe_allow_html=True)
            elif role == "Учитель":
                st.markdown(f"<div class='chat-bubble' style='background-color: #FDF2F4; border-left: 5px solid #D9534F;'><span class='chat-teacher'>👓 Уч. {sender}</span>: {msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble' style='background-color: #F4F6F7; border-left: 5px solid #1E3A8A;'><span class='chat-user'>👤 {sender}</span>: {msg}</div>", unsafe_allow_html=True)
# --- АВТОРИЗАЦИЯ ОСТАВЛЕНА В СИДБАРЕ (НО ТЕПЕРЬ ОНА НЕ ЗАКРЫВАЕТСЯ САМА) ---
st.sidebar.title("🔐 Авторизация")
role_choice = st.sidebar.radio("Кто вы?", ["Ученик", "Учитель", "Завуч (Управление)"])

if role_choice == "Завуч (Управление)":
    password = st.sidebar.text_input("Пароль Завуча", type="password")
    if password == ZAVUCH_PASSWORD:
        st.session_state.is_zavuch = True
        st.session_state.is_teacher = False
        st.session_state.auth_success = True
        st.session_state.current_user_name = "Завуч"
        st.session_state.user_role_label = "Завуч"
    elif password != "":
        st.sidebar.error("Неверный пароль!")

elif role_choice == "Учитель":
    list_teachers = st.session_state.teachers_df["Учитель"].tolist()
    if not list_teachers:
        st.sidebar.warning("Учителя еще не добавлены завучем.")
    else:
        teacher_sel = st.sidebar.selectbox("Выберите свое имя:", ["-- Выберите --"] + list_teachers)
        if teacher_sel != "-- Выберите --":
            t_password = st.sidebar.text_input("Введите личный пароль", type="password", key="t_pass")
            correct_pass = st.session_state.teachers_df[st.session_state.teachers_df["Учитель"] == teacher_sel]["Пароль"].values
            if len(correct_pass) > 0 and str(t_password) == str(correct_pass[0]):
                st.session_state.is_teacher = True
                st.session_state.is_zavuch = False
                st.session_state.auth_success = True
                st.session_state.current_user_name = teacher_sel
                st.session_state.user_role_label = "Учитель"
            elif t_password != "":
                st.sidebar.error("Неверный пароль учителя!")

else:
    list_students = st.session_state.students_df["Ученик"].tolist()
    if not list_students:
        st.sidebar.warning("В базе пока нет учеников.")
    else:
        student_sel = st.sidebar.selectbox("Выберите ваше имя:", ["-- Выберите --"] + list_students)
        if student_sel != "-- Выберите --":
            s_password = st.sidebar.text_input("Введите личный пароль ученика", type="password", key="s_pass")
            correct_s_pass = st.session_state.students_df[st.session_state.students_df["Ученик"] == student_sel]["Пароль"].values
            if len(correct_s_pass) > 0 and str(s_password) == str(correct_s_pass[0]):
                st.session_state.auth_success = True
                st.session_state.is_zavuch = False
                st.session_state.is_teacher = False
                st.session_state.current_user_name = student_sel
                st.session_state.user_role_label = "Ученик"
            elif s_password != "":
                st.sidebar.error("Неверный пароль ученика!")
# --- ЭКРАН ЗАВУЧА ---
if st.session_state.is_zavuch and st.session_state.auth_success:
    st.title("👔 Главный Кабинет Завуча")
    st.markdown("---")

    t1, t2, t3, t4, t5 = st.tabs(["⚙️ Создание структуры", "📝 Редактирование базы", "✍️ Выставить оценки", "📊 Улучшенная аналитика", "💬 Чат школы"])

    with t1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👤 Регистрация людей")
            p_type = st.selectbox("Ккого добавить?", ["Ученик", "Учитель"])
            new_name = st.text_input("ФИО человека")
            new_pass = st.text_input("Задать личный пароль", type="password", key="reg_p")
            
            if st.button("Внести в списки"):
                if new_name.strip() and new_pass.strip():
                    if p_type == "Ученик" and new_name not in st.session_state.students_df["Ученик"].tolist():
                        new_student_row = pd.DataFrame({"Ученик": [new_name], "Пароль": [new_pass]})
                        st.session_state.students_df = pd.concat([st.session_state.students_df, new_student_row], ignore_index=True)
                        st.session_state.students_df.to_csv(STUDENTS_FILE, index=False)
                        st.toast("Ученик успешно зачислен! 🎉")
                        time.sleep(1)
                        st.rerun()
                    elif p_type == "Учитель" and new_name not in st.session_state.teachers_df["Учитель"].tolist():
                        new_teacher_row = pd.DataFrame({"Учитель": [new_name], "Пароль": [new_pass]})
                        st.session_state.teachers_df = pd.concat([st.session_state.teachers_df, new_teacher_row], ignore_index=True)
                        st.session_state.teachers_df.to_csv(TEACHERS_FILE, index=False)
                        st.toast("Учитель успешно нанят! 👓")
                        time.sleep(1)
                        st.rerun()

        with col2:
            st.subheader("📚 Создание Предметов")
            new_sub = st.text_input("Название нового предмета")
            list_teachers = st.session_state.teachers_df["Учитель"].tolist()
            assigned_teacher = st.selectbox("Назначить ведущего учителя:", list_teachers) if list_teachers else None

            if st.button("Утвердить дисциплину"):
                if new_sub.strip() and assigned_teacher:
                    if new_sub not in st.session_state.assignments["Предмет"].values.tolist():
                        new_assign = pd.DataFrame({"Предмет": [new_sub], "Учитель": [assigned_teacher]})
                        st.session_state.assignments = pd.concat([st.session_state.assignments, new_assign], ignore_index=True)
                        st.session_state.assignments.to_csv(ASSIGNMENTS_FILE, index=False)
                        st.toast("Предмет закреплен! 📚")
                        time.sleep(1)
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
                old_pass_val = str(old_s_pass[0]) if len(old_s_pass) > 0 else ""
                
                updated_student_name = st.text_input("Новое ФИО ученика", value=student_to_edit)
                updated_student_pass = st.text_input("Новый пароль ученика", value=old_pass_val)
                
                if st.button("Сохранить данные ученика"):
                    st.session_state.students_df.loc[st.session_state.students_df["Ученик"] == student_to_edit, ["Ученик", "Пароль"]] = [updated_student_name, updated_student_pass]
                    st.session_state.students_df.to_csv(STUDENTS_FILE, index=False)
                    st.session_state.journal.loc[st.session_state.journal["Ученик"] == student_to_edit, "Ученик"] = updated_student_name
                    st.session_state.journal.to_csv(DB_FILE, index=False)
                    st.toast("Данные ученика обновлены!")
                    time.sleep(1)
                    st.rerun()
                        
        elif edit_type == "Изменить данные Учителя":
            list_teachers = st.session_state.teachers_df["Учитель"].tolist()
            if not list_teachers:
                st.caption("Учителей пока нет.")
            else:
                teacher_to_edit = st.selectbox("Выберите учителя для изменения:", list_teachers)
                old_pass = st.session_state.teachers_df[st.session_state.teachers_df["Учитель"] == teacher_to_edit]["Пароль"].values
                old_t_pass_val = str(old_pass[0]) if len(old_pass) > 0 else ""
                
                updated_teacher_name = st.text_input("Новое ФИО учителя", value=teacher_to_edit)
                updated_teacher_pass = st.text_input("Новый пароль учителя", value=old_t_pass_val)
                
                if st.button("Сохранить данные учителя"):
                    st.session_state.teachers_df.loc[st.session_state.teachers_df["Учитель"] == teacher_to_edit, ["Учитель", "Пароль"]] = [updated_teacher_name, updated_teacher_pass]
                    st.session_state.teachers_df.to_csv(TEACHERS_FILE, index=False)
                    st.session_state.assignments.loc[st.session_state.assignments["Учитель"] == teacher_to_edit, "Учитель"] = updated_teacher_name
                    st.session_state.assignments.to_csv(ASSIGNMENTS_FILE, index=False)
                    st.session_state.journal.loc[st.session_state.journal["Учитель"] == teacher_to_edit, "Учитель"] = updated_teacher_name
                    st.session_state.journal.to_csv(DB_FILE, index=False)
                    st.toast("Данные учителя переписаны!")
                    time.sleep(1)
                    st.rerun()

    with t3:
        st.subheader("✍️ Выставление оценок Администрацией")
        list_all_subjects = st.session_state.assignments["Предмет"].tolist()
        list_st = st.session_state.students_df["Ученик"].tolist()
        
        if not list_st or not list_all_subjects:
            st.info("ℹ️ Добавьте учеников и предметы.")
        else:
            z_col1, z_col2, z_col3 = st.columns(3)
            with z_col1: z_student = st.selectbox("Ученик", list_st, key="z_stu")
            with z_col2: z_subject = st.selectbox("Предмет", list_all_subjects, key="z_sub")
            with z_col3: z_grade = st.selectbox("Оценка", ["5", "4", "3", "2"], key="z_grd")
                
            z_comm = st.text_input("Замечание от Завуча", key="z_com")
            if st.button("Выставить оценку от Администрации"):
                found_teacher_arr = st.session_state.assignments[st.session_state.assignments["Предмет"] == z_subject]["Учитель"].values
                found_teacher = found_teacher_arr[0] if len(found_teacher_arr) > 0 else "Завуч"
                new_mark = pd.DataFrame({
                    "Ученик": [z_student], "Предмет": [z_subject], "Оценка": [z_grade],
                    "Замечание": [f"[Завуч] {z_comm}" if z_comm.strip() else "Выставлено администрацией"],
                    "Учитель": [found_teacher]
                })
                st.session_state.journal = pd.concat([st.session_state.journal, new_mark], ignore_index=True)
                st.session_state.journal.to_csv(DB_FILE, index=False)
                st.toast("Оценка успешно внесена!")
                time.sleep(1)
                st.rerun()
    with t4:
        st.subheader("📊 Мониторинг успеваемости школы")
        if st.session_state.journal.empty:
            st.info("В журнале еще нет оценок для аналитики.")
        else:
            df_an = st.session_state.journal.copy()
            df_an["Оценка_Число"] = pd.to_numeric(df_an["Оценка"], errors="coerce")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("📉 Средний балл школы", f"{df_an['Оценка_Число'].mean():.2f}")
            m2.metric("📋 Выставлено оценок", f"{len(df_an)} шт.")
            m3.metric("🚨 Всего двоек", f"{(df_an['Оценка'] == '2').sum()} шт.")
            
            st.markdown("### 📚 Успеваемость по предметам:")
            sub_stats = df_an.groupby("Предмет")["Оценка_Число"].mean().reset_index().round(2)
            sub_stats.columns = ["Дисциплина", "Средний балл успеваемости"]
            st.dataframe(sub_stats, use_container_width=True, hide_index=True)
            
            st.markdown("### 📊 Общая картина оценок:")
            grade_counts = df_an["Оценка"].value_counts().reset_index()
            grade_counts.columns = ["Оценка", "Количество"]
            st.bar_chart(data=grade_counts, x="Оценка", y="Количество")

    with t5:
        render_school_chat()

    if st.sidebar.button("🚨 Полный сброс всей школы"):
        for f in [DB_FILE, STUDENTS_FILE, TEACHERS_FILE, ASSIGNMENTS_FILE, CHAT_FILE]:
            if os.path.exists(f): os.remove(f)
        st.session_state.clear()
        st.rerun()
# --- ЭКРАН УЧИТЕЛЯ ---
elif st.session_state.is_teacher and st.session_state.auth_success:
    st.title(f"👓 Журнал преподавателя: {st.session_state.current_user_name}")
    st.markdown("---")

    t1, t2 = st.tabs(["✍️ Журнал оценок", "💬 Чат школы"])

    with t1:
        my_subjects = st.session_state.assignments[st.session_state.assignments["Учитель"] == st.session_state.current_user_name]["Предмет"].tolist()
        list_st = st.session_state.students_df["Ученик"].tolist()

        if not my_subjects: st.warning("За вами не закреплено предметов!")
        elif not list_st: st.warning("В базе данных пока нет учеников.")
        else:
            st.subheader("✍️ Выставление оценок")
            col1, col2, col3 = st.columns(3)
            with col1: s_student = st.selectbox("Ученик", list_st)
            with col2: s_subject = st.selectbox("Предмет", my_subjects)
            with col3: s_grade = st.selectbox("Оценка", ["5", "4", "3", "2"])

            s_comm = st.text_input("Комментарий / Замечание")
            if st.button("Записать в журнал"):
                new_mark = pd.DataFrame({
                    "Ученик": [s_student], "Предмет": [s_subject], "Оценка": [s_grade],
                    "Замечание": [s_comm.strip() if s_comm.strip() else "Нет замечаний"],
                    "Учитель": [st.session_state.current_user_name]
                })
                st.session_state.journal = pd.concat([st.session_state.journal, new_mark], ignore_index=True)
                st.session_state.journal.to_csv(DB_FILE, index=False)
                st.toast("Оценка выставлена! 📝")
                time.sleep(1)
                st.rerun()

            st.markdown("---")
            my_logged_marks = st.session_state.journal[st.session_state.journal["Учитель"] == st.session_state.current_user_name]
            if my_logged_marks.empty: st.caption("Вы еще не выставили ни одной оценки.")
            else: st.dataframe(my_logged_marks[["Ученик", "Предмет", "Оценка", "Замечание"]], use_container_width=True, hide_index=True)

    with t2:
        render_school_chat()

# --- ЭКРАН УЧЕНИКА / СТАРТОВЫЙ ЭКРАН ---
else:
    if not st.session_state.auth_success:
        st.title("🏫 Дневник Поведения")
        st.markdown("### 🪧 Информационная доска")
        st.info("Пожалуйста, откройте меню в левом верхнем углу (стрелочка или полоски ☰), выберите роль, найдите себя в списке и введите пароль.")
    else:
        st.title(f"📱 Дневник ученика: {st.session_state.current_user_name}")
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

            my_data = st.session_state.journal[st.session_state.journal["Ученик"] == st.session_state.current_user_name].copy()

            if my_data.empty:
                # Фикс: Шарики убраны ради защиты мобильного браузера от фризов
                st.success("🎉 У тебя идеальное поведение! Ни одного выговора или двойки.")
            else:
                my_data["Оценка_Число"] = pd.to_numeric(my_data["Оценка"], errors="coerce")
                st.markdown(f"<h3 class='report-card-header'>📊 Мой табель оценок (Всего: {len(my_data)} шт.)</h3>", unsafe_allow_html=True)

                for subj in my_data["Предмет"].unique():
                    sub_data = my_data[my_data["Предмет"] == subj]
                    g_list = ", ".join(sub_data["Оценка"].astype(str).tolist())
                    
                    raw_avg = sub_data["Оценка_Число"].mean()
                    s_avg = raw_avg if pd.notna(raw_avg) else 0.0
                    avg_text = f"{s_avg:.2f}" if s_avg > 0 else "Нет оценок"

                    with st.expander(f"📖 {subj} (Средний балл: {avg_text})"):
                        st.markdown(f"Текущие оценки: <span class='grade-badge'>{g_list}</span>", unsafe_allow_html=True)
                        st.markdown("---")
                        st.markdown("📝 Комментарии и замечания:")
                        has_n = False
                        for _, row in sub_data.iterrows():
                            if pd.notna(row["Замечание"]) and str(row["Замечание"]).strip() and str(row["Замечание"]).lower() != "nan":
                                st.caption(f"• ({row['Учитель']}) Оценка {row['Оценка']}: «{row['Замечание'].strip()}»")
                                has_n = True
                        if not has_n: st.caption("*Замечания отсутствуют.*")

        with tab_chat:
            render_school_chat()
