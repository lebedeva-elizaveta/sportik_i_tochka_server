from flask import render_template
from flask_mail import Mail, Message
import random

from app.exceptions.exceptions import ActionIsNotAvailableException

mail = Mail()


def generate_confirmation_code():
    return str(random.randint(100000, 999999))


def send_email(email):
    msg_title = "Подтверждение email"
    sender = "sportikitochka@gmail.com"
    confirmation_code = generate_confirmation_code()
    msg_body = f"Ваш код подтверждения: {confirmation_code}"

    data = {
        'app_name': "Спортик и точка",
        'title': msg_title,
        'body': msg_body,
        'code': confirmation_code
    }

    msg = Message(msg_title, sender=sender, recipients=[email])
    msg.body = msg_body
    msg.html = render_template("email.html", data=data)

    try:
        mail.send(msg)
        return confirmation_code
    except Exception as e:
        raise ActionIsNotAvailableException(str(e))

