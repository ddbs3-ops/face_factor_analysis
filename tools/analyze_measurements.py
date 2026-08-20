import sqlite3
import pandas as pd


DB_PATH = "data/face_analysis_v1_1.db"


def load_measurements():
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        height_to_width_ratio,
        upper_ratio,
        middle_ratio,
        lower_ratio,
        jaw_to_cheekbone_width_ratio,
        chin_angle,
        left_jaw_angle,
        right_jaw_angle
    FROM face_measurements
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def main():
    df = load_measurements()

    print(df["height_to_width_ratio"].describe())


if __name__ == "__main__":
    main()