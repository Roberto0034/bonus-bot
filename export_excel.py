import sqlite3
from openpyxl import Workbook


def export_users_to_excel():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            u.full_name,
            u.phone,
            u.city,
            u.birth_date,
            u.username,
            u.telegram_id,
            r.receipt_number,
            r.status,
            r.created_at
        FROM users u
        LEFT JOIN receipts r
        ON u.telegram_id = r.telegram_id
        ORDER BY r.created_at DESC
    """)

    users = cursor.fetchall()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Клієнти"

    sheet.append([
        "ПІБ",
        "Телефон",
        "Місто",
        "Дата народження",
        "Username",
        "Telegram ID",
        "Номер чека",
        "Статус",
        "Дата додавання"
    ])

    for user in users:
        sheet.append(user)

    workbook.save("clients.xlsx")

    conn.close()

    print("✅ Excel файл створено!")


if __name__ == "__main__":
    export_users_to_excel()