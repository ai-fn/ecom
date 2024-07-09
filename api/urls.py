from django.urls import include, path, re_path
from rest_framework import routers
from api.views import (
    BrandView,
    CategoryViewSet,
    CharacteristicValueViewSet,
    CharacteristicViewSet,
    CityGroupViewSet,
    CityViewSet,
    DataExportView,
    MyTokenObtainPairView,
    MyTokenRefreshView,
    ProductsById,
    PriceViewSet,
    ProductViewSet,
    ProductsInOrderViewSet,
    ReviewViewSet,
    SettingViewSet,
    VerifyConfirmCode,
    XlsxFileUploadView,
    RobotsTxtView,
    FooterItemViewSet,
    MainPageSliderImageViewSet,
    MainPageCategoryBarItemViewSet,
    MetadataViewSet,
    UpdateIndex,
    SearchHistoryViewSet,
    RebuildCategoryTreeAPIView,
    AddressAutocompleate,
    FavoriteProductViewSet,
    ProductFileViewSet,
    ProductImageViewSet,
    HTMLMetaTagsViewSet,
)
from api.views import (
    SendSMSView,
    PromoViewSet,
    SideBarMenuItemViewSet
)
from api.views.general_search import GeneralSearchView

router = routers.DefaultRouter()

router.register(r"products", ProductViewSet, basename="products")
router.register(r"productfiles", ProductFileViewSet)
router.register(r"reviews", ReviewViewSet)
router.register(r"favorite-product", FavoriteProductViewSet)
router.register(r"metadata", MetadataViewSet)
router.register(r"characteristics", CharacteristicViewSet)
router.register(r"characteristics-values", CharacteristicValueViewSet)
router.register(r"prices", PriceViewSet)
router.register(r"settings", SettingViewSet)
router.register(r"cities", CityViewSet)
router.register(r"cities-groups", CityGroupViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"products-in-order", ProductsInOrderViewSet)
router.register(r"brands", BrandView)
router.register(r"footer-items", FooterItemViewSet)
router.register(r"main-page-slider-image", MainPageSliderImageViewSet)
router.register(r"promos", PromoViewSet, basename="promo")
router.register(r"category-bar-item", MainPageCategoryBarItemViewSet)
router.register(r"sidebar-menu-item", SideBarMenuItemViewSet)
router.register(r"search-history", SearchHistoryViewSet)
router.register(r"product-images", ProductImageViewSet)
router.register(r"html-meta-tags", HTMLMetaTagsViewSet)

app_name= "api"

urlpatterns = [
    path("", include(router.urls)),
    path("shop/", include(("shop.urls", "shop"), namespace="shop")),
    path("cart/", include("cart.urls", namespace="cart")),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", MyTokenRefreshView.as_view(), name="token_refresh"),
    re_path(
        r"^upload/(?P<filename>[^/]+)$",
        XlsxFileUploadView.as_view(),
        name="upload_products",
    ),
    path("get_robots_txt", RobotsTxtView.as_view(), name="get_robots_txt"),
    path("send_verify_sms/", SendSMSView.as_view(), name="send_verify_sms"),
    path("verify_confirmation_code/", VerifyConfirmCode.as_view(), name="verify_confirmation_code"),
    re_path(r"^export", DataExportView.as_view()),
    path("search/", GeneralSearchView.as_view(), name="general-search"),
    path("products_by_id_list/", ProductsById.as_view(), name="products_bu_id_list"),
    path("update_index/", UpdateIndex.as_view(), name="update_index"),
    path("rebuild_category_tree/", RebuildCategoryTreeAPIView.as_view(), name="rebuild_category_tree"),
    path("address_autocomplete/", AddressAutocompleate.as_view(), name="address_autocomplete")
]
