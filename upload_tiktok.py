import time
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def upload_to_tiktok(video_path, caption, cookie_path="tiktok_cookies.pkl"):
    options = uc.ChromeOptions()
    options.add_argument("--disable-notifications")
    driver = uc.Chrome(options=options)

    driver.get("https://www.tiktok.com/upload?lang=en")
    time.sleep(5)

    # Load saved cookies
    if Path(cookie_path).exists():
        import pickle
        for cookie in pickle.load(open(cookie_path, "rb")):
            driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(5)
    else:
        input("⚠️ Log in to TikTok manually, then press Enter to save cookies...")
        pickle.dump(driver.get_cookies(), open(cookie_path, "wb"))
        driver.refresh()
        time.sleep(5)

    # Upload video
    upload = driver.find_element(By.XPATH, '//input[@type="file"]')
    upload.send_keys(str(video_path.resolve()))
    time.sleep(10)

    # Caption
    textarea = driver.find_element(By.XPATH, '//textarea')
    textarea.send_keys(caption)
    time.sleep(2)

    # Post
    post_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Post')]")
    post_btn.click()
    print("✅ TikTok uploaded.")
    time.sleep(15)
    driver.quit()
