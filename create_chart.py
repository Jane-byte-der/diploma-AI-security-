import matplotlib.pyplot as plt
import numpy as np

# Данные
categories = ['Время обнаружения (часы)', 'Ложные срабатывания (%)']
before = [4.5, 94]
after = [0.5, 67]

x = np.arange(len(categories))
width = 0.35

# График
fig, ax = plt.subplots(figsize=(10, 6))
bars1 = ax.bar(x - width/2, before, width, label='До внедрения ИИ', color='#ff9999')
bars2 = ax.bar(x + width/2, after, width, label='После внедрения ИИ', color='#66b3ff')

# Настройки
ax.set_title('Сравнение эффективности', fontsize=16)
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()

# Цифры
for bar in bars1:
    height = bar.get_height()
    ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(0, 3), textcoords="offset points", ha='center')
for bar in bars2:
    height = bar.get_height()
    ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(0, 3), textcoords="offset points", ha='center')

plt.savefig('comparison_chart.png', dpi=150)
print("✅ График создан!")
