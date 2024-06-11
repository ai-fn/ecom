import csv
import os
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from account.models import CustomUser

class UploadProductsTests(APITestCase):

    def setUp(self):
        self.temp_files_path = '/code/media/tmp/'
        self.basename = "output.xlsx"
        self.admin_user = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword",
            username="adminuser",
            is_staff=True
        )
        
        self.user1 = CustomUser.objects.create(
            email="dummy1@gmail.com",
            password="dummy",
            username="dummy-users1",
            is_staff=False,
        )
        self.upload_url = reverse("api:upload_products", args=[self.basename])
        
        self.create_test_csv_file(self.temp_files_path, self.basename)

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def create_test_csv_file(self, path="/code/media/tmp/", name="output.xlsx"):
        full_path = os.path.join(path, name)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        with open(full_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Заголовок", "Категории", "Описание", "Применение", "Сертификаты URL", "Сертификаты Названия", 
                "Артикул", "Бренд", "Страна происхождения", "Вид кровли", "Изображения", "Назначение", 
                "Размер", "Цвет", "Материал", "Вес материала", "Температурный режим использования", 
                "Армирование", "Состав", "Наличие самоклеящихся полос"
            ])
            writer.writerow([
                "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                "Гидро-ветрозащита и пароизоляция || Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ L самоклеящаяся (10 штук в коробке)",
                "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания",
                "Применяется с уличной стороны с подкровельными гидроветрозащитными мембранами или с внутренней стороны с пароизоляционными пленками. Размер отверстия манжеты позволяет её использовать с кабелем разных диаметров, от 5 до 12мм. Манжета оснащена клеевым слоем для удобства и простоты монтажа",
                "Tehnicheskij_list_68189_1.pdf", "Технический лист", "68189", "ТЕХНОНИКОЛЬ", "Россия", "", 
                "Uplotnitel_naja_manzheta_TEHNONIKOL__AL_FA_PROTEKT_L_samoklejaschajasja__10_shtuk_v_korobke__68189_1.png", 
                "", "147х147 мм", "", "", "", "от -40°С до +80°С", "Нет", "EPDM-каучук и нетканое полипропиленовое полотно", "Да"
            ])
            writer.writerow([
                "Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ XL самоклеящаяся (10 штук в коробке)",
                "Гидро-ветрозащита и пароизоляция || Уплотнительная манжета ТЕХНОНИКОЛЬ АЛЬФА ПРОТЕКТ XL самоклеящаяся (10 штук в коробке)",
                "Уплотнительная манжета из EPDM-каучука и нетканого полипропиленового полотна с растягивающимся эластичным отверстием предназначена для быстрой и долговечной изоляции мест вывода кабеля, гофры/трубы через воздухонепроницаемую оболочку здания.",
                "Применяется с уличной стороны с подкровельными гидроветрозащитными мембранами или с внутренней стороны с пароизоляционными пленками. Размер отверстия манжеты позволяет её использовать с гофрой/трубой размером от 15 до 30 мм. Манжета оснащена клеевым слоем для удобства и простоты монтажа",
                "Tehnicheskij_list_68190_1.pdf", "Технический лист", "068190", "ТЕХНОНИКОЛЬ", "Россия", "", 
                "Uplotnitel_naja_manzheta_TEHNONIKOL__AL_FA_PROTEKT_XL_samoklejaschajasja__10_shtuk_v_korobke__68190_1.png", 
                "", "147х147 мм", "", "", "", "от -40°С до +80°С", "Нет", "EPDM-каучук и нетканое полипропиленовое полотно", "Да"
            ])
            writer.writerow([
                "Гидро-ветрозащитная диффузионная  мембрана ТЕХНОНИКОЛЬ АЛЬФА ВЕНТ 150 (1,5 x 50 м)",
                "Гидро-ветрозащита и пароизоляция || Гидро-ветрозащитная диффузионная  мембрана ТЕХНОНИКОЛЬ АЛЬФА ВЕНТ 150 (1,5 x 50 м)",
                "Супердиффузионная мембрана ТЕХНОНИКОЛЬ АЛЬФА ВЕНТ – трехслойный материал повышенной прочности, состоящий из функционального микропористого водонепроницаемого слоя, скрепленного с двух сторон нетканым полипропиленовым полотном. Оснащена клеевой полосой для удобства и простоты монтажа. Устойчива к воздействию плесени, бактерий и УФ-излучения. Высокая паропроницаемости способствует выходу из строительных конструкций излишней влаги. Ограниченная воздухопроницаемость защищает утеплитель от конвективных потерь тепла.",
                "Применяется для защиты теплоизоляционного слоя в системах скатных кровель, вентилируемых фасадов и стен каркасной конструкции от вредного воздействия воды, ветра, пыли. Используется в конструкциях с однослойной вентиляцией, укладывается непосредственно на утеплитель или сплошной настил",
                "Tehnicheskij_list_644439_2_1.pdf || Deklaratsija_o_sootvetstvii_644439_2.pdf || Tablitsa_vybora_plenok_file_1910_3.pdf || Garantijnyj_sertifikat___web_2_4.pdf || Sertifikat_sootvetstvija__RU_5.PDF", 
                "Технический лист || Декларация о соответствии || Таблица выбора пленок || Гарантийный сертификат || Сертификат соответствия", 
                "644439", "ТЕХНОНИКОЛЬ", "Россия", "", 
                "Gidro_vetrozaschitnaja_diffuzionnaja__membrana_TEHNONIKOL__AL_FA_VENT_150__1_5_x_50_m__644439_1.png", 
                "Гидро-ветрозащитные", "1,5 x 50 м", "", "", "от -40°C до +80°C", "Нет", "Микропористый водонепроницаемый слой скрепленный с двух сторон нетканым полипропиленовым полотном", "Да"
            ])


    def test_upload_products_only_for_staff(self):
        file_path = os.path.join(self.temp_files_path, self.basename)
        
        with open(file_path, "rb") as file_obj:
            token = self.get_token(self.user1)
            self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
            response = self.client.put(self.upload_url, {"file": file_obj})
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        token = self.get_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        with open(file_path, "rb") as file_obj:
            response = self.client.put(self.upload_url, {"file": file_obj})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
