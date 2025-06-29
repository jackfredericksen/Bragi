import time
import pickle
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def upload_to_tiktok(video_path, caption, cookie_path="tiktok_cookies.pkl"):
    """Upload video to TikTok with session persistence"""
    driver = None
    
    try:
        # Setup Chrome options
        options = uc.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        
        driver = uc.Chrome(options=options)
        driver.maximize_window()
        
        print("🎬 Opening TikTok upload page...")
        driver.get("https://www.tiktok.com/upload?lang=en")
        time.sleep(5)

        # Load saved cookies if they exist
        cookie_file = Path(cookie_path)
        if cookie_file.exists():
            print("🍪 Loading saved cookies...")
            try:
                with open(cookie_file, "rb") as f:
                    cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except Exception:
                        # Skip invalid cookies
                        pass
                
                driver.refresh()
                time.sleep(5)
                print("✅ Cookies loaded successfully")
                
            except Exception as e:
                print(f"⚠️ Could not load cookies: {e}")
        
        # Check if we need to log in
        try:
            # Look for upload elements to see if we're logged in
            upload_element = driver.find_element(By.XPATH, '//input[@type="file"]')
            print("✅ Already logged in!")
        except:
            # Need to log in
            print("🔑 Please log in to TikTok manually...")
            input("   After logging in, press Enter to save cookies and continue...")
            
            # Save cookies after login
            try:
                cookies = driver.get_cookies()
                with open(cookie_file, "wb") as f:
                    pickle.dump(cookies, f)
                print("✅ Cookies saved for future use")
            except Exception as e:
                print(f"⚠️ Could not save cookies: {e}")
            
            driver.refresh()
            time.sleep(5)

        # Upload video
        print("📤 Uploading video...")
        try:
            upload_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
            )
            upload_element.send_keys(str(Path(video_path).resolve()))
            print("✅ Video file selected")
            
            # Wait for upload to process
            print("⏳ Waiting for video to process...")
            time.sleep(15)  # Give video time to upload and process
            
            # Add caption
            print("📝 Adding caption...")
            try:
                caption_area = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
                )
                caption_area.clear()
                caption_area.send_keys(caption)
                print("✅ Caption added")
            except Exception as e:
                print(f"⚠️ Could not add caption: {e}")
            
            time.sleep(3)

            # Post the video
            print("🚀 Publishing video...")
            try:
                post_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Post')]"))
                )
                post_button.click()
                print("✅ TikTok video posted successfully!")
                
                # Wait a bit to ensure it processes
                time.sleep(10)
                
            except Exception as e:
                print(f"⚠️ Could not find or click Post button: {e}")
                print("   You may need to click Post manually")
                time.sleep(5)
            
        except Exception as e:
            print(f"❌ Upload process failed: {e}")
            
    except Exception as e:
        print(f"❌ TikTok upload failed: {e}")
        
    finally:
        # Clean up browser
        if driver:
            try:
                driver.quit()
            except:
                pass  # Ignore cleanup errors