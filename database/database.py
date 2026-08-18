import sqlite3


def add_missing_columns(cursor, table_name, columns):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cursor.fetchall()}

    for column_name, column_type in columns.items():
        if column_name not in existing_columns:
            cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            )


def create_table():
    conn = sqlite3.connect("data/face_analysis.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT,
            person_id INTEGER,
            mp_yaw REAL,
            gt_yaw REAL,
            mp_pitch REAL,
            gt_pitch REAL,
            mp_roll REAL,
            gt_roll REAL,
            mp_is_frontal INTEGER,

            height_to_width_ratio REAL,

            upper_ratio REAL,
            middle_ratio REAL,
            lower_ratio REAL,

            jaw_to_cheekbone_width_ratio REAL,

            chin_angle REAL,
            left_jaw_angle REAL,
            right_jaw_angle REAL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contour_measurements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            face_measurement_id INTEGER,
            region TEXT,
            point_index INTEGER,
            angle REAL,

            FOREIGN KEY (face_measurement_id)
                REFERENCES face_measurements(id)
                ON DELETE CASCADE
            )
    """)

    add_missing_columns(
        cursor,
        "face_measurements",
        {
            "person_id": "INTEGER",
            "mp_yaw": "REAL",
            "gt_yaw": "REAL",
            "mp_pitch": "REAL",
            "gt_pitch": "REAL",
            "mp_roll": "REAL",
            "gt_roll": "REAL",
            "mp_is_frontal": "INTEGER",
        },
    )

    conn.commit()
    conn.close()


def save_face_measurement(
    image_path,
    person_id,
    gt_yaw,
    gt_pitch,
    gt_roll,
    frontality_result,
    face_measurements,
):
    conn = sqlite3.connect("data/face_analysis.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO face_measurements (
            image_path,
            person_id,
            mp_yaw,
            gt_yaw,
            mp_pitch,
            gt_pitch,
            mp_roll,
            gt_roll, 
            mp_is_frontal,
            height_to_width_ratio,
            upper_ratio,
            middle_ratio,
            lower_ratio,
            jaw_to_cheekbone_width_ratio,
            chin_angle,
            left_jaw_angle,
            right_jaw_angle
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        image_path,
        person_id,
        frontality_result.pose.yaw_deg,
        gt_yaw,
        frontality_result.pose.pitch_deg,
        gt_pitch,
        frontality_result.pose.roll_deg,
        gt_roll,
        int(frontality_result.is_frontal),

        face_measurements.height_to_width_ratio,

        face_measurements.vertical_ratios.upper,
        face_measurements.vertical_ratios.middle,
        face_measurements.vertical_ratios.lower,

        face_measurements.jaw.jaw_to_cheekbone_width_ratio,

        face_measurements.jaw.chin_angle_deg,
        face_measurements.jaw.left_jaw_angle_deg,
        face_measurements.jaw.right_jaw_angle_deg,
    ))


    face_measurement_id = cursor.lastrowid
    for point_index, angle in enumerate(
        face_measurements.jaw.chin_contour_angles_deg
    ):
        cursor.execute("""
            INSERT INTO contour_measurements(
                face_measurement_id,
                region,
                point_index,
                angle
            )
            VALUES (?, ?, ?, ?)
        """, (
        face_measurement_id,
        "chin",
        point_index,
        angle))

    for point_index, angle in enumerate(
        face_measurements.jaw.right_jaw_contour_angles_deg
    ):
        cursor.execute("""
            INSERT INTO contour_measurements(
                face_measurement_id,
                region,
                point_index,
                angle
            )
            VALUES (?, ?, ?, ?)
            """, (
        face_measurement_id,
        "right_jaw",
        point_index,
        angle))

    for point_index, angle in enumerate(
        face_measurements.jaw.left_jaw_contour_angles_deg
    ):
        cursor.execute("""
            INSERT INTO contour_measurements(
                face_measurement_id,
                region,
                point_index,
                angle
            )
            VALUES (?, ?, ?, ?)
            """, (
        face_measurement_id,
        "left_jaw",
        point_index,
        angle))



    conn.commit()
    conn.close()

def print_all_measurements():
    conn = sqlite3.connect("data/face_analysis.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM face_measurements")

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()

def delete_face_measurement(ids):
    conn = sqlite3.connect("data/face_analysis.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    for face_id in ids:
        cursor.execute(
            "DELETE FROM face_measurements WHERE id = ?",
            (face_id,)
        ) 
    
    conn.commit()
    conn.close()

def delete_all_face_measurements():
    conn = sqlite3.connect("data/face_analysis.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM face_measurements")

    conn.commit()
    conn.close()

def face_measurement_exists(image_path):
    conn = sqlite3.connect("data/face_analysis.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM face_measurements
        WHERE image_path = ?
        LIMIT 1
        """,
        (image_path,)
    )

    exists = cursor.fetchone() is not None

    conn.close()
    return exists
