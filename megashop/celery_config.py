import csv
import os
import subprocess

from django.db import transaction
from celery import Celery, shared_task

from account.models import City

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megashop.settings.local')

app = Celery('megashop')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.enable_utc = False
app.conf.timezone = "Europe/Moscow"

app.autodiscover_tasks()


@shared_task
def update_cities():
    # Clone the git repository
    repo_url = "https://github.com/hflabs/city.git"
    repo_dir = "city_repo"

    try:
        subprocess.run(['git', 'clone', repo_url, repo_dir], check=True)
        print("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return

    # Open city.csv and extract city names
    city_csv_path = os.path.join(repo_dir, "city.csv")

    try:
        with open(city_csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            city_names = []
            for row in reader:
                
                if row["city"] != "":
                    city_names.append(row["city"])
                elif row["region_type"] == "г":
                    city_names.append(row["region"])
                elif row["area_type"] == "г":
                    city_names.append(row["area"])

        print("City names extracted successfully:")
        # print(city_names) 
    except FileNotFoundError:
        print("city.csv not found.")
    except Exception as e:
        print("Error occurred while extracting city names:", e)
    finally:
        # Clean up: delete the cloned repository directory
        try:
            subprocess.run(['rm', '-rf', repo_dir], check=True)
        except subprocess.CalledProcessError as e:
            print("Error cleaning up:", e)

    current_cities = City.objects.values_list("name", flat=True)
    diff = set(city_names).difference(set(current_cities))

    if len(diff) > 0:
        with transaction.atomic():
            for c in diff:
                City.objects.create(name=c)
        print("Cities successfully created")
