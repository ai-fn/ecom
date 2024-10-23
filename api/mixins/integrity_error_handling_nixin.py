from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
APIView.dispatch


class IntegrityErrorHandlingMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as err:
            response = Response({"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if isinstance(response, Response):
                if not getattr(request, 'accepted_renderer', None):
                    neg = super().perform_content_negotiation(request, force=True)
                    request.accepted_renderer, request.accepted_media_type = neg

            response.accepted_renderer = request.accepted_renderer
            response.accepted_media_type = request.accepted_media_type
            response.renderer_context = super().get_renderer_context()
            return response
