from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import OpenApiParameter


class CustomAutoSchema(AutoSchema):
    global_params = [
        OpenApiParameter(
            "X-Api-Key",
            type=str,
            required=True,
            location=OpenApiParameter.HEADER,
            description="Ключ для доступа к API",
        )
    ]

    def get_override_parameters(self):
        params = super().get_override_parameters()
        return params + self.global_params
