import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable

from config import MAIL_ADDRESS, MAIL_PASSWORD


def get_items_from_paginated_result(endpoint) -> list:
    result: dict = endpoint()
    items: list = result["items"]
    if result["totalPage"] > 1:
        for page_number in range(2, result["totalPage"] + 1):
            items.extend(endpoint(currentPage=page_number)["items"])
    return items


def send_mail(to_address: str | Iterable[str], text: str, logger=None, subject: str = "Trading bot") -> None:
    try:
        server = smtplib.SMTP_SSL("smtp.mail.ru", 465)
        server.login(MAIL_ADDRESS, MAIL_PASSWORD)
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg.attach(MIMEText(text, "plain"))
        if isinstance(to_address, str):
            to_address = [to_address]
        for address in to_address:
            server.sendmail(MAIL_ADDRESS, address, msg.as_string())
        server.quit()
    except Exception as e:
        if logger:
            logger.error(f"Failed to send message: {e}")
