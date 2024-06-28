import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/combined_apartments_data.csv", sep=";")

df.info()

print(df.head())

print(df.tail())

# Основная статистическая информация о числовых столбцах
print(df.describe())

print("Среднее арифметическое для всех столбцов:")
print(df.mean())

print("Среднее арифметическое для цены квартиры и общей площади:")
print(df[["Цена ₽", "Общая площадь м²"]].mean())

print("Медиана для всех столбцов:")
print(df.median())

print("Медиана для цены квартиры и общей площади:")
print(df[["Цена ₽", "Общая площадь м²"]].median())

print("Мода для всех столбцов:")
print(df.mode())

print("Мода для цены квартиры и общей площади:")
print(df[["Цена ₽", "Общая площадь м²"]].mode())

print("Стандартное отклонение для всех столбцов:")
print(df.std())

print("Стандартное отклонение для цены квартиры:")
print(df["Цена ₽"].std())

print("Стандартное отклонение для общей площади:")
print(df["Общая площадь м²"].std())

print("Максимальное значение для цены квартиры:")
print(df["Цена ₽"].max())

print("Минимальное значение для цены квартиры:")
print(df["Цена ₽"].min())

print("Размах выборки для цены квартиры:")
print(df["Цена ₽"].max() - df["Цена ₽"].min())

print("Квартили для цены квартиры:")
print(df["Цена ₽"].quantile([0.25, 0.5, 0.75]))

print("Квартили для общей площади:")
print(df["Общая площадь м²"].quantile([0.25, 0.5, 0.75]))

df["Цена ₽"].hist(bins=20, figsize=(10, 6))
plt.xlabel("Цена ₽")
plt.ylabel("Частота")
plt.title("Распределение цен на квартиры")
plt.show()

df["Общая площадь м²"].hist(bins=20, figsize=(10, 6))
plt.xlabel("Общая площадь м²")
plt.ylabel("Частота")
plt.title("Распределение общей площади квартир")
plt.show()

df["Цена ₽"].plot(kind="box", figsize=(8, 6))
plt.xlabel("Цена ₽")
plt.title("Диаграмма размаха цен на квартиры")
plt.show()

df["Общая площадь м²"].plot(kind="box", figsize=(8, 6))
plt.xlabel("Общая площадь м²")
plt.title("Диаграмма размаха общей площади квартир")
plt.show()
