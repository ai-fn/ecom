from ._jwt import MyTokenObtainPairView
from ._jwt import MyTokenRefreshView
from .brand import BrandView
from .category import CategoryViewSet
from .characteristic_value import CharacteristicValueViewSet
from .characteristic import CharacteristicViewSet
from .city_group import CityGroupViewSet
from .city import CityViewSet
from .promo import PromoViewSet
from .data_export import DataExportView
from .price import PriceViewSet
from .product import ProductViewSet
from .products_in_order import ProductsInOrderViewSet
from .review import ReviewViewSet
from .setting import SettingViewSet, RobotsTxtView
from .confirm_register import (
    SendSMSView,
    VerifyConfirmCode
)
from .footer_settings import FooterItemViewSet
from .feeds import FeedsView
from .products_by_list import ProductsById
from .similar_products import SimilarProducts
from .main_page_slide_image import MainPageSliderImageViewSet
from .main_page_category_bar_item import MainPageCategoryBarItemViewSet
from .sidebar_menu_item import SideBarMenuItemViewSet
from .metadata import MetadataViewSet
from .update_index import UpdateIndex
from .search_history import SearchHistoryViewSet
from .rebuild_category_tree import RebuildCategoryTreeAPIView
from .address_autocomplete import AddressAutocompleate
from .favorite_product import FavoriteProductViewSet
from .productfile import ProductFileViewSet
from .productimage import ProductImageViewSet
from .feedback import FeedbackViewSet
from .page import PageViewSet