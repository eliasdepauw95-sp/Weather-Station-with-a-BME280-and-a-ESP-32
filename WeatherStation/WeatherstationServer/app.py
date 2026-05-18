import sqlite3
import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

app.config["SECRET_KEY"] = "Smoke weed evryday"


def get_db_connection():
    conn = sqlite3.connect("sql/weerstation.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_temp_data():
    conn = get_db_connection()
    temps = conn.execute(
        "SELECT * FROM temperatuur ORDER BY id DESC LIMIT 120"
    ).fetchall()
    conn.close()
    return temps


def get_druk_data():
    conn = get_db_connection()
    drukken = conn.execute(
        "SELECT * FROM luchtdruk ORDER BY id DESC LIMIT 120"
    ).fetchall()
    conn.close()
    return drukken


def get_vocht_data():
    conn = get_db_connection()
    vocht = conn.execute(
        "SELECT * FROM luchtvochtigheid ORDER BY id DESC LIMIT 120"
    ).fetchall()
    conn.close()
    return vocht


def get_time_data():
    conn = get_db_connection()
    time = conn.execute(
        "SELECT * FROM time ORDER BY id DESC LIMIT 120"
    ).fetchall()
    conn.close()
    return time


def limit_db_rows():
    conn = get_db_connection()

    conn.execute("""
        DELETE FROM temperatuur
        WHERE id NOT IN (
            SELECT id FROM temperatuur
            ORDER BY id DESC
            LIMIT 120
        )
    """)

    conn.execute("""
        DELETE FROM luchtvochtigheid
        WHERE id NOT IN (
            SELECT id FROM luchtvochtigheid
            ORDER BY id DESC
            LIMIT 120
        )
    """)

    conn.execute("""
        DELETE FROM luchtdruk
        WHERE id NOT IN (
            SELECT id FROM luchtdruk
            ORDER BY id DESC
            LIMIT 120
        )
    """)

    conn.execute("""
        DELETE FROM time
        WHERE id NOT IN (
            SELECT id FROM time
            ORDER BY id DESC
            LIMIT 120
        )
    """)

    conn.commit()
    conn.close()


def insert_to_db(temp, druk, vocht, date):
    conn = get_db_connection()

    conn.execute(
        "INSERT INTO temperatuur (waarde) VALUES (?)",
        (temp,)
    )

    conn.execute(
        "INSERT INTO luchtvochtigheid (waarde) VALUES (?)",
        (vocht,)
    )

    conn.execute(
        "INSERT INTO luchtdruk (waarde) VALUES (?)",
        (druk,)
    )

    conn.execute("""
        INSERT INTO time (
            tijdstip,
            temperatuur_id,
            luchtvochtigheid_id,
            luchtdruk_id
        )
        VALUES (
            ?,
            (SELECT id FROM temperatuur ORDER BY id DESC LIMIT 1),
            (SELECT id FROM luchtvochtigheid ORDER BY id DESC LIMIT 1),
            (SELECT id FROM luchtdruk ORDER BY id DESC LIMIT 1)
        )
    """, (date,))

    conn.commit()
    conn.close()

    limit_db_rows()


@app.route("/")
def index():
    temp = get_temp_data()
    druk = get_druk_data()
    vocht = get_vocht_data()
    time = get_time_data()

    return render_template(
        "index.html",
        temps=temp,
        drukken=druk,
        vochtigheid=vocht,
        tijden=time
    )


@app.route("/bme280", methods=["POST"])
def bme280():
    temp = request.form.get("temperature")
    druk = request.form.get("pressure")
    vocht = request.form.get("humidity")

    date = datetime.datetime.now().replace(microsecond=0)
    date = date.strftime("%H:%M:%S %d-%m-%Y")

    insert_to_db(temp, druk, vocht, date)

    return "ok", 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9090)
