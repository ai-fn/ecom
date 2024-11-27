import urllib.error
import urllib.request
from loguru import logger
from django.conf import settings
from functools import lru_cache
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.staticfiles.storage import staticfiles_storage


class EmailService:
    """
    Сервис для отправки email сообщений с поддержкой HTML-формата и вложений.
    """

    @classmethod
    def build_message(
        cls,
        email: str,
        topik: str,
        template_name: str = None,
        context: dict = None,
        text_content: str = "",
    ) -> EmailMultiAlternatives:
        """
        Создает объект сообщения EmailMultiAlternatives.

        :param email: Email получателя.
        :type email: str
        :param topik: Тема сообщения.
        :type topik: str
        :param template_name: Имя шаблона для генерации HTML-контента письма.
        :type template_name: str, optional
        :param context: Контекст для рендера шаблона.
        :type context: dict, optional
        :param text_content: Текстовое содержимое письма.
        :type text_content: str
        :return: Объект EmailMultiAlternatives.
        :rtype: EmailMultiAlternatives
        """
        message = EmailMultiAlternatives(
            subject=topik,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )

        if template_name:
            body = render_to_string(template_name, context)
            message.mixed_subtype = "related"
            message.attach_alternative(body, "text/html")

        return message

    @classmethod
    def send(cls, message: EmailMultiAlternatives, fail_silently: bool = False) -> int:
        """
        Отправляет email сообщение.

        :param message: Сообщение для отправки.
        :type message: EmailMultiAlternatives
        :param fail_silently: Флаг, определяющий, подавлять ли ошибки при отправке.
        :type fail_silently: bool
        :return: Количество успешно отправленных сообщений.
        :rtype: int
        """
        try:
            result = message.send(fail_silently)
            return result
        except Exception as err:
            logger.error(f"Ошибка при отправке email: {str(err)}")
            if not fail_silently:
                raise err

    @classmethod
    @lru_cache()
    def get_attach_data(cls, static_path: str, header_name: str, header_value: str) -> MIMEImage | None:
        """
        Загружает файл из статики и добавляет его как вложение.

        :param static_path: Путь к статическому файлу.
        :type static_path: str
        :param header_name: Имя заголовка вложения.
        :type header_name: str
        :param header_value: Значение заголовка вложения.
        :type header_value: str
        :return: Объект MIMEImage для вложения или None при ошибке.
        :rtype: MIMEImage | None
        """
        url = staticfiles_storage.url(static_path)
        try:
            with urllib.request.urlopen(url) as response:
                attach_data = response.read()
        except urllib.error.HTTPError as err:
            logger.error(f"Ошибка при получении статического файла: {str(err)}")
            return None

        attach = MIMEImage(attach_data)
        attach.add_header(header_name, header_value)
        return attach
