from functools import lru_cache
from email.mime.image import MIMEImage
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from loguru import logger


class EmailService:
    
    @classmethod
    def build_message(cls, email: str, topik: str, template_name: str = None, context: dict = None, text_content: str = ""):

        message = EmailMultiAlternatives(
            subject=topik,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )

        if template_name is not None:
            body = render_to_string(template_name, context)
            message.mixed_subtype = 'related'
            message.attach_alternative(body, "text/html")

        return message
    
    @classmethod
    def send(cls, message: EmailMultiAlternatives, fail_silently: bool = False):
        try:
            result = message.send(fail_silently)
        except Exception as err:
            logger.error(f"Error while sending email: {str(err)}")
            if not fail_silently:
                raise err

        return result

    @classmethod
    @lru_cache()
    def get_attach_data(cls, static_path: str, header_name: str, header_value: str):
        with open(finders.find(static_path), 'rb') as f:
            attach_data = f.read()

        attach = MIMEImage(attach_data)
        attach.add_header(header_name, header_value)
        return attach
