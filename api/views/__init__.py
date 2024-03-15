from ._jwt import MyTokenObtainPairView
from .brand import BrandView
from .category import CategoryViewSet
from .category_metadata import CategoryMetaDataViewSet
from .characteristic_value import CharacteristicValueViewSet
from .characteristic import CharacteristicViewSet
from .city_group import CityGroupViewSet
from .city import CityViewSet
from .data_export import DataExportView
from .file_upload import XlsxFileUploadView
from .order import OrderViewSet
from .price import PriceViewSet
from .product import ProductViewSet
from .products_in_order import ProductsInOrderViewSet
from .review import ReviewViewSet
from .setting import SettingViewSet
from .user import UserRegistrationView
from .confirm_register import (
    SendConfirmSMS,
    VerifyConfirmCode
)
from .products_by_list import ProductsById
from .similar_products import SimilarProducts