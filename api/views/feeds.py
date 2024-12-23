from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from django.http import HttpResponse, FileResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.files.storage import default_storage

from shop.models import Product
from account.models import City
from shop.services import FeedsService
from api.serializers.setting import SettingSerializer


@extend_schema(
    tags=["Settings"],
    description="Получение xml фидов",
    summary="Получение xml фидов",
    parameters=[OpenApiParameter(
        "city_domain",
        type=str,
        required=True,
        description="Домен города"
    )],
    examples=[
        OpenApiExample(
            name="Response Example",
            value="""<yml_catalog date="2024-07-16">
<shop>
    <name>КровМаркет</name>
    <company>alta-profil</company>
    <url>https://domain.com/</url>
    <offers>
        <offer id="6" available="true">
            <name>Гидро-ветрозащитая диффузионная мембрана ТехноНИКОЛЬ Альфа ВЕНТ 130 ТПУ</name>
            <url>catalog/gidro-vetrozashchitaia-diffuzionnaia-membrana-tekhnonikol-al-fa-vent-130-tpu/gidro-vetrozashchitaia-diffuzionnaia-membrana-tekhnonikol-al-fa-vent-130-tpu-6</url>
            <categoryId>7</categoryId>
            <picture>Ссылка на изображение</picture>
            <vendor>ТЕХНОНИКОЛЬ</vendor>
            <description>Диффузионная мембрана ТЕХНОНИКОЛЬ АЛЬФА ВЕНТ ТПУ 130 – трёхслойный материал с функциональным слоем из паропроницаемого покрытия - термопластичного полиуретана, защищённого с двух сторон полотном из нетканого полипропилена. Воздухонепроницаемая и водонепроницаемая поверхность создает надежную защиту от конвективных потерь тепла и намокания слоя утеплителя. Устойчива к воздействию плесени, бактерий и УФ-излучению.</description>
            <sales_notes>Минимальная партия заказа - 1 шт.</sales_notes>
            <vendorCode>070534</vendorCode>
            <country_of_origin>Россия</country_of_origin>
            <barcode>barcode</barcode>
            <weight>0.5</weight>
            <dimensions>10.0/20.0/30.0</dimensions>
            <cpa>1</cpa>
            <manufacturer_warranty>true</manufacturer_warranty>
            <pickup>true</pickup>
            <store>true</store>
            <outlets>
                <outlet id="Москва" instock="true" price="1131.00">
                <city>Москва</city>
                <address>Адрес магазина</address>
                <oldprice>1131.00</oldprice>
                <currencyId>RUB</currencyId>
                </outlet>
            </outlets>
        </offer>
    </offers>
</shop>
</yml_catalog>
""",
            response_only=True,
        )
    ],
)
class FeedsView(APIView):

    queryset = Product.objects.all()
    serializer_class = SettingSerializer

    # @method_decorator(cache_page(120 * 60))
    def get(self, request):
        city_domain = request.query_params.get("city_domain")
        c = City.objects.filter(domain=city_domain).first()
        if not c:
            return JsonResponse({"error": "City with provided domain not found."}, status=400)

        file_path = FeedsService.get_feed_path(c.name)

        try:
            with default_storage.open(file_path, "rb") as file:
                response = FileResponse(file, content_type='application/xml')
                response['Content-Disposition'] = 'attachment; filename="feed.xml"'
                return response
        except FileNotFoundError:
            return HttpResponse(status=404)
