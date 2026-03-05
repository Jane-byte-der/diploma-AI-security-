# Дипломная работа: Разработка методических рекомендаций по интеграции технологий искусственного интеллекта в систему управления информационной безопасностью

Jupyter Notebook с анализом данных и обнаружением аномалий.

## Файлы
- `analysis_diploma.ipynb` — основной код и визуализация

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

## 📌 О работе

**Институт информационных наук**  
**Кафедра международной информационной безопасности**  
**Направление подготовки: 10.03.01 — Информационная безопасность**

Данный репозиторий создан в рамках выполнения выпускной квалификационной работы на тему *"Разработка методических рекомендаций по интеграции технологий искусственного интеллекта в систему управления информационной безопасностью"* (МГЛУ, 2026).

Автор: Воробьева Евгения Александровна



# Development of Methodological Recommendations for the Integration of Artificial Intelligence Technologies into an Information Security Management System

This repository contains the supplementary materials for a thesis on integrating AI into Information Security Management Systems (ISMS). The core component is a Jupyter Notebook designed for data analysis and anomaly detection in privileged user behavior.

## 🔬 Research Overview
- **Objective:** Develop a novel methodology for integrating AI into security operations.
- **Approach:** Behavioral profiling of privileged users using unsupervised machine learning techniques.
- **Key Findings:**
    - **27% reduction in false positives** compared to traditional SIEM rules.
    - **89% faster incident detection time**, enabling more rapid response to potential threats.

## 📊 Key Results
![Comparison of traditional SIEM rules vs. the proposed AI-based methodology, showing a 27% reduction in false positives.](comparison_chart.png)

## 🛠 Implementation & Tech Stack
- **Core Analysis:** Python (pandas, numpy, matplotlib, scikit-learn)
- **Environment:** Jupyter Notebook for interactive exploration and reproducibility.
- **Data:** Synthetic dataset mimicking privileged user behavior to ensure transparency and easy experimentation.

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