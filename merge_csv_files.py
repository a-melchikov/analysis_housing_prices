import os
import pandas as pd


def merge_csv_files(input_dir, filenames):
    filepaths = [os.path.join(input_dir, filename) for filename in filenames]

    for filepath in filepaths:
        if not os.path.isfile(filepath):
            print(f"Файл не найден: {filepath}")
            return None

    dataframes = [pd.read_csv(filepath) for filepath in filepaths]

    # Объединение всех DataFrame в один
    combined_df = pd.concat(dataframes, ignore_index=True)

    return combined_df


def filter_and_save_columns(df, columns, output_file):
    # Оставление только нужных колонок
    filtered_df = df[columns]

    filtered_df.to_csv(output_file, index=False)
    print(f"Фильтрованные данные сохранены в {output_file}")


def filter_filled_rows(df, columns):
    # Оставить только те строки, в которых все указанные столбцы заполнены
    filtered_df = df.dropna(subset=columns)
    return filtered_df


def transform_columns(df):
    # Создаем копию DataFrame для безопасного преобразования
    df = df.copy()

    # Преобразование данных в столбцах с использованием .loc
    df["Комнат"] = df["Комнат"].astype(int)

    df["Цена"] = df["Цена"].str.replace("₽", "").str.replace(",", "").astype(float)
    df.rename(columns={"Цена": "Цена ₽"}, inplace=True)

    df["Площадь"] = (
        df["Площадь"].str.replace(" м2", "").str.replace(",", ".").astype(float)
    )
    df.rename(columns={"Площадь": "Общая площадь м²"}, inplace=True)

    df["Жилая"] = df["Жилая"].str.replace(" м2", "").str.replace(",", ".").astype(float)
    df.rename(columns={"Жилая": "Жилая площадь м²"}, inplace=True)

    df["Цена за квадрат"] = (
        df["Цена за квадрат"].str.replace("₽/м²", "").str.replace(",", "").astype(float)
    )
    df.rename(columns={"Цена за квадрат": "Цена за квадрат ₽/м²"}, inplace=True)

    df["Год постройки"] = df["Год постройки"].astype(int)
    df["Количество этажей"] = df["Количество этажей"].astype(int)

    return df


if __name__ == "__main__":
    input_dir = "data"

    filenames = [
        "дзержинский_apartments_data.csv",
        "ленинский_apartments_data.csv",
        "промышленный_apartments_data.csv",
        "центральный_apartments_data.csv",
    ]

    columns = [
        "Ссылка",
        "Комнат",
        "Цена",
        "Площадь",
        "Жилая",
        "Цена за квадрат",
        "Район",
        "Ремонт",
        "Этаж",
        "Год постройки",
        "Количество этажей",
        "Материал стен",
    ]

    output_file = "data/combined_apartments_data.csv"

    combined_df = merge_csv_files(input_dir, filenames)

    if combined_df is not None:
        filtered_df = combined_df[columns]

        filtered_filled_df = filter_filled_rows(filtered_df, columns)

        transformed_df = transform_columns(filtered_filled_df)

        filter_and_save_columns(transformed_df, transformed_df.columns, output_file)
    else:
        print("Объединение файлов не удалось.")
