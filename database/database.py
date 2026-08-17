import sqlite3


def create_table():
    conn = sqlite3.connect("data/face_analysis.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT,

            yaw REAL,
            pitch REAL,
            roll REAL,
            is_frontal INTEGER,

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


    conn.commit()
    conn.close()


def save_face_measurement(
    image_path,
    frontality_result,
    face_measurements,
):
    conn = sqlite3.connect("data/face_analysis.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO face_measurements (
            image_path,
            yaw,
            pitch,
            roll,
            is_frontal,
            height_to_width_ratio,
            upper_ratio,
            middle_ratio,
            lower_ratio,
            jaw_to_cheekbone_width_ratio,
            chin_angle,
            left_jaw_angle,
            right_jaw_angle
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        image_path,

        frontality_result.pose.yaw_deg,
        frontality_result.pose.pitch_deg,
        frontality_result.pose.roll_deg,
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

