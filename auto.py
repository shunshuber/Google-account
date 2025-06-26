import os
import random
import string
import time
import platform
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Генерация случайных данных пользователя
def generate_user_data():
    first_names = ["Alex", "James", "Emma", "Olivia", "Liam", "Noah", "Ava", "Isabella"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    username = f"{first_name.lower()}{last_name.lower()}{random.randint(100, 999)}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    recovery_email = f"{username}@outlook.com"
    birth_year = random.randint(1980, 2000)
    birth_day = random.randint(1, 28)
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "password": password,
        "recovery_email": recovery_email,
        "birth_year": birth_year,
        "birth_day": birth_day
    }

# Инициализация драйвера Chrome
def init_driver():
    chrome_options = Options()
    
    # Настройки для Linux/Windows
    if platform.system() == "Linux":
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")  # Режим без GUI
    
    # Общие настройки
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Настройки для обхода детекта
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90,110)}.0.0.0 Safari/537.36")
    
    # Определение пути к драйверу
    driver_path = "./chromedriver"
    if platform.system() == "Windows":
        driver_path = "./chromedriver.exe"
    
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Эмуляция человеческого поведения
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

# Процесс создания аккаунта
def create_account(driver, user_data):
    try:
        driver.get("https://accounts.google.com/signup")
        
        # Шаг 1: Основная информация
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "firstName"))).send_keys(user_data["first_name"])
        driver.find_element(By.ID, "lastName").send_keys(user_data["last_name"])
        driver.find_element(By.ID, "username").send_keys(user_data["username"])
        driver.find_element(By.NAME, "Passwd").send_keys(user_data["password"])
        driver.find_element(By.NAME, "ConfirmPasswd").send_keys(user_data["password"])
        
        # Человеческая задержка перед кликом
        time.sleep(random.uniform(0.5, 1.5))
        driver.find_element(By.ID, "accountDetailsNext").click()
        
        # Шаг 2: Пропуск телефона
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Пропустить') or contains(text(),'Skip')]"))).click()
        
        # Шаг 3: Резервная почта
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "recoveryEmailId"))).send_keys(user_data["recovery_email"])
        time.sleep(random.uniform(0.3, 0.8))
        driver.find_element(By.ID, "recoveryEmailNext").click()
        
        # Шаг 4: Дата рождения
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "day"))).send_keys(str(user_data["birth_day"]))
        driver.find_element(By.ID, "year").send_keys(str(user_data["birth_year"]))
        
        # Выбор месяца
        driver.find_element(By.ID, "month").click()
        months = driver.find_elements(By.XPATH, "//select[@id='month']/option")
        if len(months) > 1:
            random.choice(months[1:]).click()
        
        # Выбор пола
        driver.find_element(By.ID, "gender").click()
        genders = driver.find_elements(By.XPATH, "//select[@id='gender']/option")
        if len(genders) > 1:
            random.choice(genders[1:]).click()
        
        time.sleep(random.uniform(0.5, 1.2))
        driver.find_element(By.ID, "personalDetailsNext").click()
        
        # Шаг 5: Пропуск верификации
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Пропустить') or contains(text(),'Skip')]"))).click()
        
        # Шаг 6: Принятие условий
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='termsofserviceNext']"))).click()
        
        # Проверка успешности
        WebDriverWait(driver, 15).until(EC.url_contains("myaccount.google.com"))
        return True
        
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Ошибка на шаге: {str(e)}")
        return False

# Главная функция
def main():
    print("=== Google Account Creator ===")
    print("Инициализация драйвера...")
    
    # Создаем папку для результатов
    os.makedirs("accounts", exist_ok=True)
    
    try:
        driver = init_driver()
        accounts_to_create = 5  # Начните с малого количества для теста
        success_count = 0
        
        for i in range(accounts_to_create):
            print(f"\nСоздание аккаунта #{i+1}/{accounts_to_create}")
            user_data = generate_user_data()
            
            if create_account(driver, user_data):
                success_count += 1
                # Сохраняем данные
                with open(f"accounts/account_{success_count}.txt", "w") as f:
                    f.write(f"Email: {user_data['username']}@gmail.com\n")
                    f.write(f"Password: {user_data['password']}\n")
                    f.write(f"Recovery Email: {user_data['recovery_email']}\n")
                    f.write(f"Name: {user_data['first_name']} {user_data['last_name']}\n")
                
                print(f"УСПЕХ! Аккаунт создан: {user_data['username']}@gmail.com")
            else:
                print("Не удалось создать аккаунт")
            
            # Очистка куки и кэша
            driver.delete_all_cookies()
            time.sleep(random.uniform(10, 20))  # Длительная пауза
            
        print(f"\nИтог: Успешно создано {success_count}/{accounts_to_create} аккаунтов")
        
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()
        print("Процесс завершен")

if __name__ == "__main__":
    main()
