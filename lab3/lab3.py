import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

def load_vhi_data(directory):
    all_data = []

    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)

            with open(filepath, "r", encoding="utf-8") as file:
                first_line = file.readline().strip()
                region_name = first_line.split(":")[-1].split(",")[0].strip()

            df = pd.read_csv(filepath, skiprows=2, header=0, usecols=[0, 1, 2, 3, 4, 5, 6], skip_blank_lines=True)
            df.columns = ["Year", "Week", "SMN", "SMT", "VCI", "TCI", "VHI"]

            region_index = filename.split("_")[1]
            df["Region"] = int(region_index)
            df["Region_Name"] = region_name

            all_data.append(df)

    df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    df = df.dropna(subset=["Year"]) 
    return df

def update_region_indices(df):
    region_mapping = {
    1:22, 2:24, 3:23, 4:25, 5:3, 6:4, 7:8, 8:19, 9:20, 10:21, 11:9, 12:26, 
    13:10, 14:11, 15:12, 16:13, 17: 14, 18:15, 19:16, 20:27, 21:17, 22:18, 
    23:6, 24:1, 25:2, 26:7, 27:5
    }

    df["Region"] = df["Region"].map(region_mapping)
    return df

data_folder = 'vhi_data' # Директорія, де знаходяться csv файли
vhi_df = load_vhi_data(data_folder)
vhi_df = update_region_indices(vhi_df)

st.title("Аналіз ступеня здоров’я рослинності України по областях")
st.sidebar.title("Фільтри")

# Ініціалізація значень у session_state, якщо вони ще не встановлені
if "selected_index" not in st.session_state:
    st.session_state.selected_index = "VCI"

if "selected_region" not in st.session_state:
    st.session_state.selected_region = "Вінницька"

if "week_range" not in st.session_state:
    st.session_state.week_range = (1, 52)

if "year_range" not in st.session_state:
    st.session_state.year_range = (int(vhi_df['Year'].min()), int(vhi_df['Year'].max()))



# 1. dropdown список, який дозволить обрати ряд VCI, TCI, VHI 
selected_index = st.sidebar.selectbox("Оберіть індекс для відображення", ["VCI", "TCI", "VHI"], 
                              index=["VCI", "TCI", "VHI"].index(st.session_state.selected_index),
                              key="selected_index")

# 2. dropdown список, який дозволить вибрати область, для якої буде виконуватись аналіз
regions = {
    "Вінницька": 1, "Волинська": 2, "Дніпропетровська": 3, "Донецька": 4, "Житомирська": 5, "Закарпатська": 6, 
    "Запорізька": 7, "Івано-Франківська": 8, "Київська": 9, "Кіровоградська": 10, "Луганська": 11, "Львівська": 12, 
    "Миколаївська": 13, "Одеська": 14, "Полтавська": 15, "Рівненська": 16, "Сумська": 17, "Тернопільська": 18, 
    "Харківська": 19, "Херсонська": 20, "Хмельницька": 21, "Черкаська": 22, "Чернівецька": 23, 
    "Чернігівська": 24, "Крим": 25, "м. Київ": 26, "м. Севастополь": 27
}

selected_region = st.sidebar.selectbox("Оберіть область:", list(regions.keys()), 
                               index=list(regions.keys()).index(st.session_state.selected_region),
                               key="selected_region")

# 3. slider, який дозволить зазначити інтервал тижнів, за які відбираються дані
st.sidebar.slider("Оберіть інтервал тижнів", 1, 52, key="week_range")

# 4. slider, який дозволить зазначити інтервал років, за які відбираються дані
st.sidebar.slider("Оберіть інтервал років", int(vhi_df['Year'].min()), int(vhi_df['Year'].max()), key="year_range")

# 5. button для скидання всіх фільтрів і повернення до початкового стану даних
def reset_filters():
    for key in ["selected_index", "selected_region", "week_range", "year_range"]:
        if key in st.session_state:
            del st.session_state[key]  
    st.rerun() 

# Кнопка для скидання фільтрів
if st.sidebar.button("Скинути фільтри"):
    reset_filters()
    st.rerun()

# 6. Створіть три вкладки для відображення таблиці з відфільтрованими даними, відповідного до неї графіка та графіка порівняння даних по областях.
tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік", "Порівняння"])

region_id = regions[selected_region]

filtered_data = vhi_df[
    (vhi_df["Region"] == region_id) &
    (vhi_df["Week"].between(*st.session_state.week_range)) &
    (vhi_df["Year"].between(*st.session_state.year_range)) &
    (vhi_df["VHI"] >= 0) # очищаємо додаткові артефакти у вигляді VHI = -1
]

with tab1:
    if filtered_data.empty:
        st.warning("Немає даних для відображення. Спробуйте змінити фільтри.")
    else:
        st.write("### Відфільтровані дані")
        sort_asc = st.checkbox("Сортувати за зростанням", key="sort_asc")
        sort_desc = st.checkbox("Сортувати за спаданням", key="sort_desc")
        if sort_asc and sort_desc:
            st.warning("Оберіть лише один варіант сортування.")
        elif sort_asc:
            filtered_data = filtered_data.sort_values(by=selected_index, ascending=True)
        elif sort_desc:
            filtered_data = filtered_data.sort_values(by=selected_index, ascending=False)
        st.dataframe(filtered_data[["Year", "Week", selected_index, "Region_Name"]])

with tab2:
    st.write(f"### {selected_index} за діапазон років, що обмежений обраним інтервалом тижнів для {selected_region} область")

    if filtered_data.empty:
        st.warning("Немає даних для відображення. Спробуйте змінити фільтри.")
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(filtered_data["Year"] - 1 + filtered_data["Week"] / 52, filtered_data[selected_index], marker="o", linestyle="-", label=selected_index)

        ax.set_xlabel("Рік")
        ax.set_ylabel(selected_index)
        ax.set_title(f"{selected_index} у {selected_region} область")
        ax.grid(True)

        st.pyplot(fig)

with tab3:
    if filtered_data.empty:
        st.warning("Немає даних для відображення. Спробуйте змінити фільтри.")
    else:
        st.write("### Порівняння VHI між областями за обраний проміжок часу")
        comparison_data = vhi_df[(vhi_df["Year"].between(*st.session_state.year_range)) & (vhi_df["Week"].between(*st.session_state.week_range))]
        region_means = comparison_data.groupby("Region_Name")[selected_index].mean().sort_values()

        fig, ax = plt.subplots()
        region_means.plot(kind='bar', ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel(selected_index)
        st.pyplot(fig)

