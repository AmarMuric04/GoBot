import itertools
import os
import re
import sys
import threading
import time

import pyperclip
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()


def spinner(message):
    return
    for c in itertools.cycle(["|", "/", "-", "\\"]):
        if not spin:
            break
        sys.stdout.write(f"\r{message}... {c}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r")


EMAIL = os.getenv("GOVAULT_EMAIL")
PASSWORD = os.getenv("GOVAULT_PASSWORD")

user_email = EMAIL
user_password = PASSWORD


def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)


def is_valid_password(password):
    return (
        len(password) >= 8
        and re.search(r"\d", password)
        and re.search(r"[!@#$%^\\;`&*(),.?\":{}|<>]", password)
    )


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--disable-logging")

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://govault.vercel.app/generate")

driver.maximize_window()

password = driver.find_element(By.CSS_SELECTOR, "input")


while not is_valid_email(user_email):
    user_email = input("Enter a valid email: ")


# while not is_valid_password(user_password):
#     option = input(
#         "\n\nYour password does not meet the requirements!\nUse a GoVault generated password? (Y/N): "
#     )

#     if option.lower() == "y":
#         user_password = password.get_attribute("value")
#     else:
#         user_password = input(
#             "\n\nPassword must have:\n8 Characters\nat least 1 special character\nAt least 1 number\nEnter a valid password: "
#         )
#     if is_valid_password(user_password):
#         pyperclip.copy(user_password)
#         stop_process = input(
#             "\n\nThe password was copied to your clipboard!\nTake a second to save it to your .env file.\n* If you don't do this, you'll need to go to @ https://govault.vercel.app/reset-password to reset it.\n\nWhen you save the password, press Enter to continue!"
#         )


def signin():
    email_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")

    email_input.send_keys(user_email)
    password_input.send_keys(user_password)

    signin_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#signin"))
    )

    signin_button.click()

    try:
        no_account_message = WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#error"))
        )

        signup()
    except:
        pass


def signup():
    create_account_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#create-one"))
    )

    create_account_link.click()

    create_account_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#authenticate"))
    )

    email_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")

    email_input.send_keys(user_email)
    password_input.send_keys(user_password)

    create_account_button.click()

    time.sleep(3)

    driver.get("https://govault.vercel.app/generate")

    try:
        already_exists = WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#error"))
        )

        print(
            "We detected that a user with this email already exists.\nRe-run the program with valid credentials."
        )
        global spin
        spin = False
        loading_thread.join()
        sys.exit()
    except:
        pass


source = input(
    "\n\n* Required — What do you want to save this password for? (Google, Amazon, ...): "
)

while not source:
    source = input(
        "* Required — What do you want to save this password for? (Google, Amazon, ...): "
    )

notes = input("* Optional — Add notes for this password (You can leave this empty): ")

spin = True
loading_thread = threading.Thread(target=spinner, args=["Saving password"])
loading_thread.start()


save_to_vault_button = driver.find_element(By.CSS_SELECTOR, "#save-to-vault")


save_to_vault_button.click()


signin()


password = driver.find_element(By.CSS_SELECTOR, "input")

if user_password == password.get_attribute("value"):
    regenerate_password = driver.find_element(By.CSS_SELECTOR, "#regenerate")
    regenerate_password.click()

    try:
        password = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input"))
        )
    except Exception as e:
        print("Failed to reload password input after regenerating:", e)


avatar = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "/html/body/main/main/header/div"))
)

save_to_vault_button = driver.find_element(By.CSS_SELECTOR, "#save-to-vault")


save_to_vault_button.click()


source_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "source"))
)
notes_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "notes"))
)

source_input.send_keys(source)
notes_input.send_keys(notes)

submit_button = driver.find_element(By.CSS_SELECTOR, "#submit")

submit_button.click()

spin = False
loading_thread.join()

pyperclip.copy(password.get_attribute("value"))


print(
    f"\n\nPassword stored successfully\nFor security purposes, we can't show you the password, but it was added to your copy clipboard.\nYou can view all of your passwords @ https://govault.vercel.app/vault\n\nThanks for using GoVault!"
)

driver.quit()
