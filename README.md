# Дипломная работа: Разработка методических рекомендаций по интеграции технологий искусственного интеллекта в систему управления информационной безопасностью

Данный репозиторий содержит вспомогательные материалы к дипломной работе по интеграции искусственного интеллекта в системы управления информационной безопасностью (СУИБ). Основной компонент — Jupyter Notebook, предназначенный для анализа данных и обнаружения аномалий в поведении привилегированных пользователей.

## 📁 Структура репозитория
- `analysis_diploma.ipynb` — основной Jupyter Notebook с полным анализом данных
- `requirements.txt` — список зависимостей Python
- `.gitignore` — служебный файл Git
- `comparison_chart.png` — график сравнения эффективности до и после внедрения ИИ
- `jupyter_analysis.png` — дополнительные графики из анализа
- `create_chart.py` — скрипт для генерации графика сравнения

## Запуск
```bash
pip install pandas matplotlib numpy
```
## 📊 Результаты внедрения

В таблице представлено сравнение эффективности работы системы информационной безопасности до и после внедрения разработанных методических рекомендаций (на основе данных из параграфа 3.3.2 дипломной работы).

| Показатель | До внедрения ИИ | После внедрения ИИ | Изменение |
|------------|-----------------|-------------------|-----------|
| **Количество инцидентов в месяц** | 47 | 52 | ▲ +10% |
| **Выявлено внутренних нарушителей** | 3 | 8 | ▲ +166% |
| **Среднее время обнаружения** | 4.5 часа | 0.5 часа | ▼ -89% |
| **Доля ложных срабатываний** | 94% | 67% | ▼ -27% |
| **Инциденты, выявленные только благодаря ИИ** | — | 6 | +6 |

## 📈 Визуализация результатов

![Сравнение до и после](comparison_chart.png)

## 📊 Пример данных (таблица 3.2)

Фрагмент синтетического датасета, использованного для анализа:

| Timestamp      | User_ID     | User_Role     | Event_Type  | Resource                         | IP_Address    | Data_Size_KB | Is_Anomaly |
|----------------|-------------|---------------|-------------|----------------------------------|---------------|--------------|------------|
| 10.02.2026 09:15 | IVANOV_ADM  | Администратор | LOGIN       | DC-01                            | 10.10.1.5     |              | 0          |
| 10.02.2026 09:23 | PETROV_BUH  | Бухгалтер     | FILE_ACCESS | \\fs\\finance\\report.docx       | 10.10.2.10    | 120.0        | 0          |
| 10.02.2026 10:01 | SIDOROV_DEV | Разработчик   | DB_QUERY    | test_db                          | 10.10.3.15    | 45.0         | 0          |
| 10.02.2026 03:02 | IVANOV_ADM  | Администратор | LOGIN       | DC-01                            | 185.124.33.12 |              | 1          |
| 10.02.2026 03:15 | IVANOV_ADM  | Администратор | DB_QUERY    | customer_db                      | 185.124.33.12 | 150000.0     | 1          |
| 11.02.2026 14:30 | PETROV_BUH  | Бухгалтер     | FILE_ACCESS | \\fs\\develop\\source_code        | 10.10.2.10    | 5.0          | 1          |
| 11.02.2026 09:45 | SMIRNOV_MGR | Менеджер      | WEB_ACCESS  | cloud-storage.ru/upload          | 10.10.5.20    | 25000.0      | 1          |
| 11.02.2026 16:20 | IVANOV_ADM  | Администратор | FILE_ACCESS | \\fs\\backup                      | 10.10.1.5     | 500.0        | 0          |
| 11.02.2026 22:10 | PETROV_BUH  | Бухгалтер     | LOGIN       | FS-01                            | 10.10.2.10    |              | 0          |
| 12.02.2026 08:55 | SIDOROV_DEV | Разработчик   | FILE_ACCESS | \\fs\\finance\\salaries.xlsx      | 10.10.3.15    | 2100.0       | 1          |

## 📌 О работе

**Институт информационных наук**  
**Кафедра международной информационной безопасности**  
**Направление подготовки: 10.03.01 — Информационная безопасность**

Данный репозиторий создан в рамках выполнения выпускной квалификационной работы на тему *"Разработка методических рекомендаций по интеграции технологий искусственного интеллекта в систему управления информационной безопасностью"* (МГЛУ, 2026).

Автор: Воробьева Евгения Александровна

<br>
<br>

# Development of Methodological Recommendations for the Integration of Artificial Intelligence Technologies into an Information Security Management System

This repository contains the supplementary materials for a thesis on integrating AI into Information Security Management Systems (ISMS). The core component is a Jupyter Notebook designed for data analysis and anomaly detection in privileged user behavior.

## 🔬 Research Overview
- **Objective:** Develop a novel methodology for integrating AI into security operations.
- **Approach:** Behavioral profiling of privileged users using unsupervised machine learning techniques.
- **Key Findings:**
    - **27% reduction in false positives** compared to traditional SIEM rules.
    - **89% faster incident detection time**, enabling more rapid response to potential threats.

## 🛠 Implementation & Tech Stack
- **Core Analysis:** Python (pandas, numpy, matplotlib, scikit-learn)
- **Environment:** Jupyter Notebook for interactive exploration and reproducibility.
- **Data:** Synthetic dataset mimicking privileged user behavior to ensure transparency and easy experimentation.

## 📊 Implementation Results

Comparison of information security system performance before and after the implementation of the developed methodological recommendations (based on data from Section 3.3.2 of the thesis).

| Metric | Before AI | After AI | Change |
|--------|-----------|----------|--------|
| **Number of incidents per month** | 47 | 52 | ▲ +10% |
| **Insider threats detected** | 3 | 8 | ▲ +166% |
| **Average detection time** | 4.5 hours | 0.5 hours | ▼ -89% |
| **False positive rate** | 94% | 67% | ▼ -27% |
| **Incidents detected only by AI** | — | 6 | +6 |

## 📋 Sample Data (Table 3.2)

A fragment of the synthetic dataset used for the analysis:

| Timestamp      | User_ID     | User_Role     | Event_Type  | Resource                         | IP_Address    | Data_Size_KB | Is_Anomaly |
|----------------|-------------|---------------|-------------|----------------------------------|---------------|--------------|------------|
| 10.02.2026 09:15 | IVANOV_ADM  | Administrator | LOGIN       | DC-01                            | 10.10.1.5     |              | 0          |
| 10.02.2026 09:23 | PETROV_BUH  | Accountant    | FILE_ACCESS | \\fs\\finance\\report.docx       | 10.10.2.10    | 120.0        | 0          |
| 10.02.2026 10:01 | SIDOROV_DEV | Developer     | DB_QUERY    | test_db                          | 10.10.3.15    | 45.0         | 0          |
| 10.02.2026 03:02 | IVANOV_ADM  | Administrator | LOGIN       | DC-01                            | 185.124.33.12 |              | 1          |
| 10.02.2026 03:15 | IVANOV_ADM  | Administrator | DB_QUERY    | customer_db                      | 185.124.33.12 | 150000.0     | 1          |
| 11.02.2026 14:30 | PETROV_BUH  | Accountant    | FILE_ACCESS | \\fs\\develop\\source_code        | 10.10.2.10    | 5.0          | 1          |
| 11.02.2026 09:45 | SMIRNOV_MGR | Manager       | WEB_ACCESS  | cloud-storage.ru/upload          | 10.10.5.20    | 25000.0      | 1          |
| 11.02.2026 16:20 | IVANOV_ADM  | Administrator | FILE_ACCESS | \\fs\\backup                      | 10.10.1.5     | 500.0        | 0          |
| 11.02.2026 22:10 | PETROV_BUH  | Accountant    | LOGIN       | FS-01                            | 10.10.2.10    |              | 0          |
| 12.02.2026 08:55 | SIDOROV_DEV | Developer     | FILE_ACCESS | \\fs\\finance\\salaries.xlsx      | 10.10.3.15    | 2100.0       | 1          |

## 🚀 Web Application

This project now includes a **fully functional web interface** for real-time anomaly detection in security logs.

### Local Setup

```bash
# Clone the repository
git clone https://github.com/Jane-byte-der/diploma-AI-security-.git
cd diploma-AI-security-/ai-security-platform

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 backend/app.py

## 🧠 Methodology Highlights

This research includes both theoretical development and practical validation:

- **Developed and validated** UEBA-based methodology for privileged user anomaly detection
- **Created comprehensive anomaly typology** with 5 key types:
  - *Temporal* — unusual working hours
  - *Spatial* — access from unexpected locations
  - *Resource* — access to unauthorized systems
  - *Intensity* — abnormal data volumes
  - *Behavioral* — unusual action sequences
- **Experimental validation** on realistic enterprise dataset (Integra-Soft LLC)
- **48 references** (2023-2026) including Russian and international research, GOST R ISO/IEC 27001 standards

## 📁 Repository Structure
- `analysis_diploma.ipynb` - The main Jupyter Notebook containing the full data analysis pipeline, model training, and evaluation.
- `requirements.txt` - A list of Python dependencies required to run the notebook.
- `create_chart.py` - A standalone Python script to regenerate the comparison chart.
- `comparison_chart.png` - The generated comparison chart image used in this README.
- `jupyter_analysis.png` - Additional plots and visualizations from the analysis.
- `.gitignore` - Specifies intentionally untracked files to ignore.

## 🚀 Getting Started

Follow these steps to run the analysis on your local machine.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Jane-byte-der/diploma-AI-security-.git
    cd diploma-AI-security-
    ```

2.  **Install the required dependencies:**
    It is highly recommended to do this within a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Launch Jupyter Notebook:**
    ```bash
    jupyter notebook analysis_diploma.ipynb
    ```

## 🎯 Why This Matters

This research addresses the critical cybersecurity challenge of detecting insider threats and unknown attacks—sophisticated threats that often bypass traditional, signature-based security systems like SIEM. By leveraging AI for behavioral analysis, this work provides a pathway to more proactive and effective security monitoring.

## 📄 Thesis

The full thesis (in Russian) is available here: [link to PDF]

## 📌 About

This repository was created as part of the final qualification work at Moscow State Linguistic University (MSLU), 2026.

**Author:** Evgeniia Vorobeva