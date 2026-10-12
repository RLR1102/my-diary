import os
import pandas as pd
import streamlit as st

# Настройка интерфейса под мобильные экраны
st.set_page_config(
    page_title="Электронный Журнал", page_icon="🏫", layout="centered"
)

# --- АДАПТИВНЫЙ SMARTPHONE-FRIENDLY СТИЛЬ ---
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { min-width: 250px; max-width: 280px; }
    .report-card-header { margin-top: 15px; margin-bottom: 10px; color: #1E3A8A; font-weight: bold; font-size: 1.2rem; }
    .grade-badge { font-size: 18px; letter-spacing: 2px; color: #2C3E50; font-weight: bold; background-color: #F8F9FA; padding: 3px 8px; border-radius: 5px; border: 1px solid #E2E8F0; }
    .leaderboard-box { padding: 10px; border-radius: 8px; margin-bottom: 10px; text-align: center; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- ФАЙЛЫ БАЗЫ ДАННЫХ ---
DB_FILE = "school_journal.csv"
STUDENTS_FILE = "students.txt"
TEACHERS_FILE = "teachers_passwords.csv"
ASSIGNMENTS_FILE = "assignments.csv"
ZAVUCH_PASSWORD = "Armanboss"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["Оценка"] = df["Оценка"].astype(str)
        return df
    return pd.DataFrame(columns=["Ученик", "Предмет", "Оценка", "Замечание", "Учитель"])

def load_list(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

def save_list(filename, current_list):
    with open(filename, "w", encoding="utf-8") as f:
        for item in current_list:
            f.write(f"{item}\n")

def load_teachers():
    if os.path.exists(TEACHERS_FILE):
        return pd.read_csv(TEACHERS_FILE)
    return pd.DataFrame(columns=["Учитель", "Пароль"])

def load_assignments():
    if os.path.exists(ASSIGNMENTS_FILE):
        return pd.read_csv(ASSIGNMENTS_FILE)
    return pd.DataFrame(columns=["Предмет", "Учитель"])

# Инициализация сессий
if "journal" not in st.session_state:
    st.session_state.journal = load_data()
if "students" not in st.session_state:
    st.session_state.students = load_list(STUDENTS_FILE)
if "teachers_df" not in st.session_state:
    st.session_state.teachers_df = load_teachers()
if "assignments" not in st.session_state:
    st.session_state.assignments = load_assignments()

# --- ВХОД В СИСТЕМУ ---
st.sidebar.title("🔐 Авторизация")
role_choice = st.sidebar.radio(
    "Кто вы?", ["Ученик", "Учитель", "Завуч (Управление)"]
)

is_zavuch = False
is_teacher = False
current_user_name = ""

if role_choice == "Завуч (Управление)":
    password = st.sidebar.text_input("Пароль Завуча", type="password")
    if password == ZAVUCH_PASSWORD:
        is_zavuch = True
        st.sidebar.success("Доступ в Главное Управление!")
    elif password != "":
        st.sidebar.error("Неверный пароль!")

elif role_choice == "Учитель":
    list_teachers = st.session_state.teachers_df["Учитель"].tolist()
    if not list_teachers:
        st.sidebar.warning("Учителя еще не добавлены завучем.")
    else:
        current_user_name = st.sidebar.selectbox("Выберите свое имя:", list_teachers)
        t_password = st.sidebar.text_input("Введите личный пароль", type="password", key="t_pass")
        
        correct_pass = st.session_state.teachers_df[st.session_state.teachers_df["Учитель"] == current_user_name]["Пароль"].values
        if len(correct_pass) > 0 and str(t_password) == str(correct_pass[0]):
            is_teacher = True
            st.sidebar.success("Журнал открыт!")
        elif t_password != "":
            st.sidebar.error("Неверный личный пароль!")

else:
    if not st.session_state.students:
        st.sidebar.warning("В базе пока нет учеников.")
    else:
        current_user_name = st.sidebar.selectbox("Выберите ваше имя:", st.session_state.students)
# --- ЭКРАН ЗАВУЧА (ГЛАВНОЕ УПРАВЛЕНИЕ) ---
if is_zavuch:
    st.title("👔 Главный Кабинет Завуча")
    st.markdown("---")

    t1, t2, t3 = st.tabs(["⚙️ Управление школой", "✍️ Выставить оценки как Завуч", "📊 Аналитика школы"])

    with t1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👤 Регистрация людей")
            p_type = st.selectbox("Кого добавить?", ["Ученик", "Учитель"])
            new_name = st.text_input("ФИО человека")
            
            if p_type == "Учитель":
                new_t_pass = st.text_input("Задать личный пароль для учителя", type="password", key="new_t_p")
            
            if st.button("Внести в списки"):
                if new_name.strip():
                    if p_type == "Ученик" and new_name not in st.session_state.students:
                        st.session_state.students.append(new_name)
                        save_list(STUDENTS_FILE, st.session_state.students)
                        st.success(f"Ученик {new_name} зачислен!")
                        st.rerun()
                    elif p_type == "Учитель" and new_name not in st.session_state.teachers_df["Учитель"].tolist():
                        if new_t_pass.strip():
                            new_teacher_row = pd.DataFrame({"Учитель": [new_name], "Пароль": [new_t_pass]})
                            st.session_state.teachers_df = pd.concat([st.session_state.teachers_df, new_teacher_row], ignore_index=True)
                            st.session_state.teachers_df.to_csv(TEACHERS_FILE, index=False)
                            st.success(f"Учитель {new_name} нанят с личным паролем!")
                            st.rerun()
                        else:
                            st.error("Учителю обязательно нужен пароль!")

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
                        st.success(f"Предмет '{new_sub}' закреплен за {assigned_teacher}!")
                        st.rerun()

        st.markdown("---")
        st.subheader("📋 Список зарегистрированных учителей")
        if not st.session_state.teachers_df.empty:
            st.dataframe(st.session_state.teachers_df[["Учитель"]], use_container_width=True)

    with t2:
        st.subheader("✍️ Панель Завуча: Выставление оценок")
        list_all_subjects = st.session_state.assignments["Предмет"].tolist()
        
        if not st.session_state.students or not list_all_subjects:
            st.info("ℹ️ Добавьте учеников и предметы во вкладке 'Управление школой'.")
        else:
            z_col1, z_col2, z_col3 = st.columns(3)
            with z_col1:
                z_student = st.selectbox("Ученик", st.session_state.students, key="z_stu")
            with z_col2:
                z_subject = st.selectbox("Предмет", list_all_subjects, key="z_sub")
            with z_col3:
                z_grade = st.selectbox("Оценка", ["5", "4", "3", "2"], key="z_grd")
                
            z_comm = st.text_input("Замечание / Комментарий от Завуча", key="z_com")
            
            if st.button("Выставить оценку от лица Администрации"):
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

    with t3:
        st.subheader("📈 Успеваемость учебных дисциплин")
        if st.session_state.journal.empty:
            st.info("В журнале еще нет оценок для аналитики.")
        else:
            df_an = st.session_state.journal.copy()
            df_an["Оценка_Число"] = pd.to_numeric(df_an["Оценка"], errors="coerce")

            sub_stats = df_an.groupby("Предмет")["Оценка_Число"].mean().reset_index().round(2)
            sub_stats.columns = ["Название предмета", "Средний балл школы"]
            st.table(sub_stats)

            st.markdown("**Количество выданных оценок каждого типа:**")
            grade_counts = df_an["Оценка"].value_counts().reset_index()
            grade_counts.columns = ["Оценка", "Количество"]
            st.bar_chart(data=grade_counts, x="Оценка", y="Количество")

    if st.sidebar.button("🚨 Полный сброс всей школы"):
        for f in [DB_FILE, STUDENTS_FILE, TEACHERS_FILE, ASSIGNMENTS_FILE]:
            if os.path.exists(f):
                os.remove(f)
        st.session_state.clear()
        st.rerun()

# --- ЭКРАН УЧИТЕЛЯ ---
elif is_teacher:
    st.title(f"👓 Журнал преподавателя: {current_user_name}")
    st.markdown("---")

    my_subjects = st.session_state.assignments[st.session_state.assignments["Учитель"] == current_user_name]["Предмет"].tolist()

    if not my_subjects:
        st.warning("Завуч еще не закрепил за вами ни одного предмета!")
    elif not st.session_state.students:
        st.warning("В школе пока нет учеников для выставления оценок.")
    else:
        st.subheader("✍️ Выставление текущих оценок")
        col1, col2, col3 = st.columns(3)

        with col1:
            s_student = st.selectbox("Ученик", st.session_state.students)
        with col2:
            s_subject = st.selectbox("Ваш предмет", my_subjects)
        with col3:
            s_grade = st.selectbox("Оценка", ["5", "4", "3", "2"])

        s_comm = st.text_input("Комментарий к оценке / Замечание")

        if st.button("Записать в электронный журнал"):
            new_mark = pd.DataFrame({
                "Ученик": [s_student],
                "Предмет": [s_subject],
                "Оценка": [s_grade],
                "Замечание": [s_comm],
                "Учитель": [current_user_name]
            })
            st.session_state.journal = pd.concat([st.session_state.journal, new_mark], ignore_index=True)
            st.session_state.journal.to_csv(DB_FILE, index=False)
            st.success("Оценка успешно внесена!")
            st.rerun()

        st.markdown("---")
        st.subheader("📋 История выставленных вами оценок")
        my_logged_marks = st.session_state.journal[st.session_state.journal["Учитель"] == current_user_name]
        if my_logged_marks.empty:
            st.caption("Вы еще не выставили ни одной оценки.")
        else:
            st.dataframe(my_logged_marks[["Ученик", "Предмет", "Оценка", "Замечание"]], use_container_width=True)
# --- ЭКРАН УЧЕНИКА (ИСПРАВЛЕНА ШАПКА!) ---
else:
    if not current_user_name:
        st.title("🏫 Мой Дневник")
        st.info("Добро пожаловать! База данных пуста. Войдите как Завуч слева и настройте структуру классов.")
    else:
        # ЗАГОЛОВОК ТЕПЕРЬ ПОЯВЛЯЕТСЯ СТРОГО ТУТ И ТОЛЬКО ДЛЯ ВЫБРАННОГО УЧЕНИКА
        st.title(f"📱 Дневник ученика: {current_user_name}")
        st.markdown("---")

        # Доска почета/позора школы
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

        # Личные оценки ученика
        my_data = st.session_state.journal[st.session_state.journal["Ученик"] == current_user_name].copy()

        if my_data.empty:
            st.balloons()
            st.success("У тебя идеальное поведение! Ни одного выговора или двойки.")
        else:
            my_data["Оценка_Число"] = pd.to_numeric(my_data["Оценка"], errors="coerce")
            total_m = len(my_data)

            st.markdown(f"<h3 class='report-card-header'>📊 Мой табель успеваемости (Всего оценок: {total_m} шт.)</h3>", unsafe_allow_html=True)

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
                    st.markdown("📝 Комментарии и замечания к оценкам:")
                    has_n = False
                    for _, row in sub_data.iterrows():
                        if pd.notna(row["Замечание"]) and str(row["Замечание"]).strip() and str(row["Замечание"]).lower() != "nan":
                            st.caption(f"• ({row['Учитель']}) Оценка {row['Оценка']}: «{row['Замечание'].strip()}»")
                            has_n = True
                    if not has_n:
                        st.caption("*Замечания отсутствуют.*")
