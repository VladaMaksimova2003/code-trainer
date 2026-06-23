import logging
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from shared.config import SmtpSettings, get_settings
from shared.exceptions import EmailDeliveryError

logger = logging.getLogger(__name__)


def _mail_settings() -> SmtpSettings:
    return get_settings().smtp


def send_verification_code_email(*, to_email: str, code: str, purpose: str) -> None:
    """Send verification code to the address the user entered (register / change email)."""
    subject = "Код подтверждения — Code Trainer"
    if purpose == "register":
        body = f"Ваш код для регистрации: {code}\nКод действует 10 минут."
    elif purpose == "reset_password":
        subject = "Сброс пароля — Code Trainer"
        body = f"Ваш код для сброса пароля: {code}\nКод действует 10 минут."
    else:
        body = f"Ваш код для смены email: {code}\nКод действует 10 минут."

    smtp = _mail_settings()
    from_email = (smtp.from_email or smtp.user or "noreply@code-trainer.local").strip()

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = formataddr(("Code Trainer", from_email))
    message["To"] = to_email

    try:
        with smtplib.SMTP(smtp.host, smtp.port, timeout=30) as server:
            server.ehlo()
            if smtp.use_tls:
                server.starttls()
                server.ehlo()
            if smtp.user and smtp.password:
                server.login(smtp.user, smtp.password)
            server.send_message(message)
    except Exception as exc:
        logger.exception("Failed to send verification email to %s", to_email)
        raise EmailDeliveryError("Не удалось отправить письмо с кодом. Попробуйте позже.") from exc

    logger.info("Verification email sent to %s (purpose=%s)", to_email, purpose)
