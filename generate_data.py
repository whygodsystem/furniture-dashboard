import pandas as pd
import numpy as np

np.random.seed(42)
dates = pd.date_range(start='2024-01-01', end='2025-06-01', freq='D')
categories = ['Кухни', 'Шкафы', 'Столы', 'Стулья', 'Кровати']
data = []

for date in dates:
    for category in categories:
        revenue = np.random.randint(50000, 300000)
        cost = revenue * np.random.uniform(0.5, 0.85)
        profit = revenue - cost
        orders = np.random.randint(1, 10)
        data.append([date, category, revenue, cost, profit, orders])

df = pd.DataFrame(data, columns=['date', 'category', 'revenue', 'cost', 'profit', 'orders_count'])
df.to_csv('furniture_data.csv', index=False)
print("✅ Данные сгенерированы в furniture_data.csv")