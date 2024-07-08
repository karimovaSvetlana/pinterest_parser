import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import urllib.request
import json
import ssl
import time
import os
from tqdm.auto import tqdm

conf = json.load(open("config.json", "r"))

# Инициализация логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Инициализация WebDriver и настройка SSL
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
ssl._create_default_https_context = ssl._create_unverified_context


def delete_files(path_to: str, listnames: list):
    """Удаляет файлы и директории из списка listnames по указанному пути path_to."""
    for filename in listnames:
        file_path = os.path.join(path_to, filename)
        try:
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    os.system(f"rm -rf {file_path}")
                logger.info(f"File or directory '{filename}' has been deleted")
            else:
                logger.info(f"File or directory '{filename}' does not exist")
        except Exception as e:
            logger.error(f"Failed to delete '{filename}': {e}")


def log_in(email: str, password: str):
    """Логин в Pinterest с использованием указанных email и password."""
    try:
        driver.implicitly_wait(10)
        driver.get("https://ru.pinterest.com/login/")
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        logger.info("Successfully logged in to Pinterest")
    except Exception as e:
        logger.error(f"Failed to login: {e}")


def create_folder(path_to: str, search_names: list):
    """Создает папки по списку search_names в директории path_to."""
    for name_path in search_names:
        try:
            os.mkdir(os.path.join(path_to, name_path))
            logger.info(f"Folder '{name_path}' created")
        except FileExistsError:
            logger.info(f"Folder '{name_path}' already exists")
        except Exception as e:
            logger.error(f"Failed to create folder '{name_path}': {e}")


def main(number_of_photo: int, path_to: str, search_names: list):
    """Основная функция для загрузки фотографий по запросам из списка search_names."""
    for idx, name in enumerate(tqdm(search_names, desc="Loading queries")):
        folder_path = os.path.join(path_to, name)
        try:
            current_photos = len(os.listdir(folder_path))
            if current_photos >= number_of_photo:
                logger.info(f"Skipping '{name}' as it already has {current_photos} photos")
                continue

            search_box = driver.find_element(By.XPATH, "//input[@name='searchBoxInput']")
            search_box.clear()
            search_box.send_keys(name, Keys.ENTER)
            time.sleep(5)

            while len(os.listdir(folder_path)) < number_of_photo:
                for image in range(1, len(driver.find_elements(By.XPATH, f"(//img[@loading='auto'])"))):
                    if len(os.listdir(folder_path)) >= number_of_photo:
                        break  # Если достигли нужного числа фото, выходим из цикла

                    try:
                        img_element = driver.find_element(By.XPATH, f"(//img[@loading='auto'])[{image}]")
                        if not img_element.get_attribute("srcset"):
                            name_image = img_element.get_attribute("src")
                        else:
                            srcset = img_element.get_attribute("srcset").split(" ")
                            name_image = srcset[-2] if len(srcset) != 1 else srcset[0]

                        img_filename = f"{os.path.basename(name_image).split('?')[0]}"
                        img_path = os.path.join(folder_path, img_filename)
                        urllib.request.urlretrieve(name_image, img_path)
                        logger.info(f"Downloaded photo '{img_filename}' for query '{name}'")
                    except Exception as e:
                        logger.error(f"Failed download photo: {e}")

                driver.execute_script("window.scrollBy({top: 1000, left: 0, behavior: 'smooth'});")
                time.sleep(2)

            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.DELETE)

        except Exception as e:
            logger.error(f"Error processing '{name}': {e}")


if __name__ == "__main__":
    path_to = os.path.abspath("photo")+"/"
    try:
        delete_files(path_to, conf["delete_files"])
        create_folder(path_to, conf["search_names"])
        log_in(conf["email"], conf["password"])
        main(conf["number_of_photo"], path_to, conf["search_names"])

        # Проверка количества загруженных файлов
        for name in conf["search_names"]:
            num_photos = len(os.listdir(os.path.join(path_to, name)))
            logger.info(f"{name} - {num_photos}")

    finally:
        driver.quit()  # Всегда завершаем WebDriver после завершения работы
