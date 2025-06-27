import time
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def upload_to_youtube(video_path, title, cookie_path="youtube_cookies.pkl"):
    options = uc.ChromeOptions()
    options.add_argument("--disable-notifications")
    driver = uc.Chrome(options=options)

    driver.get("https://studio.youtube.com")
    time.sleep(5)

    # Load cookies
    if Path(cookie_path).exists():
        import pickle
        for cookie in pickle.load(open(cookie_path, "rb")):
            driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(5)
    else:
        input("⚠️ Log in to YouTube Studio manually, then press Enter to save cookies...")
        pickle.dump(driver.get_cookies(), open(cookie_path, "wb"))
        driver.refresh()
        time.sleep(5)

    # Upload video
    driver.get("https://studio.youtube.com")
    time.sleep(5)
    driver.find_element(By.XPATH, "//ytcp-button[@id='create-icon']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//tp-yt-paper-item[@test-id='upload-beta']").click()
    time.sleep(3)
    upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    upload_input.send_keys(str(video_path.resolve()))
    time.sleep(10)

    # Title field
    title_box = driver.find_element(By.ID, 'textbox')
    title_box.clear()
    title_box.send_keys(title)
    time.sleep(2)

    # Next x 3 → Publish
    for _ in range(3):
        next_btn = driver.find_element(By.ID, "next-button")
        next_btn.click()
        time.sleep(2)
    driver.find_element(By.ID, "done-button").click()
    print("✅ YouTube video uploaded.")
    time.sleep(10)
    driver.quit()
