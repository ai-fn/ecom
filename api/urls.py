from django.urls import include, path
from rest_framework import routers
from api.views import (
    BrandView,
    CategoryViewSet,
    CharacteristicValueViewSet,
    CharacteristicViewSet,
    CityGroupViewSet,
    CityViewSet,
    MyTokenObtainPairView,
    MyTokenRefreshView,
    ProductsById,
    PriceViewSet,
    ProductViewSet,
    ProductsInOrderViewSet,
    ReviewViewSet,
    SettingViewSet,
    RobotsTxtView,
    FooterItemViewSet,
    BannerViewSet,
    SliderViewSet,
    MainPageCategoryBarItemViewSet,
    MetadataViewSet,
    UpdateIndex,
    SearchHistoryViewSet,
    RebuildCategoryTreeAPIView,
    AddressAutocompleate,
    FavoriteProductViewSet,
    ProductFileViewSet,
    ProductImageViewSet,
    PageViewSet,
    ProductGroupViewSet,
    ItemSetViewSet,
    ItemSetElementViewSet,
    CategoryTagViewSet,
    ConfirmCodesViewSet,
    FeedsView,
    PromoViewSet,
    SideBarMenuItemViewSet
)
from shop.views import SitemapView
from api.views.general_search import GeneralSearchView


router = routers.DefaultRouter()

router.register(r"brands", BrandView)
router.register(r"pages", PageViewSet)
router.register(r"cities", CityViewSet)
router.register(r"prices", PriceViewSet)
router.register(r"reviews", ReviewViewSet)
router.register(r"banners", BannerViewSet)
router.register(r"settings", SettingViewSet)
router.register(r"itemsets", ItemSetViewSet)
router.register(r"metadata", MetadataViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"footer-items", FooterItemViewSet)
router.register(r"cities-groups", CityGroupViewSet)
router.register(r"productfiles", ProductFileViewSet)
router.register(r"category-tags", CategoryTagViewSet)
router.register(r"confirm-codes", ConfirmCodesViewSet)
router.register(r"product-images", ProductImageViewSet)
router.register(r"product-groups", ProductGroupViewSet)
router.register(r"search-history", SearchHistoryViewSet)
router.register(r"main-page-slider-image", SliderViewSet)
router.register(r"promos", PromoViewSet, basename="promo")
router.register(r"characteristics", CharacteristicViewSet)
router.register(r"itemset-elements", ItemSetElementViewSet)
router.register(r"favorite-product", FavoriteProductViewSet)
router.register(r"sidebar-menu-item", SideBarMenuItemViewSet)
router.register(r"products-in-order", ProductsInOrderViewSet)
router.register(r"products", ProductViewSet, basename="products")
router.register(r"category-bar-item", MainPageCategoryBarItemViewSet)
router.register(r"characteristics-values", CharacteristicValueViewSet)


app_name= "api"

urlpatterns = [
    path("", include(router.urls)),
    path("webhooks/", include("api.webhook_handlers")),
    path("cart/", include("cart.urls", namespace="cart")),
    path("blog/", include("blog.urls", namespace="blog")),
    path("account/", include("account.urls", namespace="account")),
    path("shop/", include(("shop.urls", "shop"), namespace="shop")),
    path("import-app/", include(("import_app.urls", "import_app"), namespace="import_app")),
    path("export-app/", include(("export_app.urls", "export_app"), namespace="export_app")),

    path("feeds.xml/", FeedsView.as_view(), name="product_feed"),
    path("update_index/", UpdateIndex.as_view(), name="update_index"),
    path("search/", GeneralSearchView.as_view(), name="general-search"),
    path("get_robots_txt", RobotsTxtView.as_view(), name="get_robots_txt"),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", MyTokenRefreshView.as_view(), name="token_refresh"),
    path("custom/sitemap.xml", view=SitemapView.as_view(), name="custom-sitemap"),
    path("products_by_id_list/", ProductsById.as_view(), name="products_bu_id_list"),
    path("address_autocomplete/", AddressAutocompleate.as_view(), name="address_autocomplete"),
    path("rebuild_category_tree/", RebuildCategoryTreeAPIView.as_view(), name="rebuild_category_tree"),
]
