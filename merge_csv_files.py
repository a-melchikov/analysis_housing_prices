import pandas as pd
import os


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

        filter_and_save_columns(filtered_filled_df, columns, output_file)
    else:
        print("Объединение файлов не удалось.")
