from crm_integration.actions import BaseWebhookHandler


class ValidateRequestAction(BaseWebhookHandler):

    def handle(self, request):
        ## Метод валидации запроса вебхука
        # TODO реализловать алгоритм проверки запроса

        return True
