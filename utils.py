import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import MAIL_ADDRESS, MAIL_PASSWORD


def get_items_from_paginated_result(endpoint) -> list:
    result: dict = endpoint()
    items: list = result["items"]
    if result["totalPage"] > 1:
        for page_number in range(2, result["totalPage"] + 1):
            items.extend(endpoint(currentPage=page_number)["items"])
    return items


def send_mail(to_address: str, text: str, logger) -> None:
    try:
        server = smtplib.SMTP_SSL("smtp.mail.ru", 465)
        server.login(MAIL_ADDRESS, MAIL_PASSWORD)
        msg = MIMEMultipart()
        msg["Subject"] = "Trading bot"
        msg.attach(MIMEText(text, "plain"))
        server.sendmail(MAIL_ADDRESS, to_address, msg.as_string())
        server.quit()
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
