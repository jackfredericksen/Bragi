import time
import pickle
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def upload_to_youtube(video_path, title, cookie_path="youtube_cookies.pkl"):
    """Upload video to YouTube Shorts with session persistence"""
    driver = None
    
    try:
        # Setup Chrome options
        options = uc.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        
        driver = uc.Chrome(options=options)
        driver.maximize_window()
        
        print("📺 Opening YouTube Studio...")
        driver.get("https://studio.youtube.com")
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
            # Look for create button to see if we're logged in
            create_button = driver.find_element(By.XPATH, "//ytcp-button[@id='create-icon']")
            print("✅ Already logged in to YouTube!")
        except:
            # Need to log in
            print("🔑 Please log in to YouTube Studio manually...")
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

        # Start upload process
        print("📤 Starting upload process...")
        
        # Click Create button
        try:
            create_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='create-icon']"))
            )
            create_button.click()
            time.sleep(2)
            
            # Click Upload videos
            upload_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-item[@test-id='upload-beta']"))
            )
            upload_option.click()
            time.sleep(3)
            
            print("✅ Upload dialog opened")
            
        except Exception as e:
            print(f"⚠️ Could not open upload dialog: {e}")
            return

        # Upload video file
        print("📹 Uploading video file...")
        try:
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
            )
            upload_input.send_keys(str(Path(video_path).resolve()))
            print("✅ Video file selected")
            
            # Wait for upload to process
            print("⏳ Waiting for video to upload...")
            time.sleep(15)
            
        except Exception as e:
            print(f"❌ Video upload failed: {e}")
            return

        # Set title
        print("📝 Setting video title...")
        try:
            title_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='textbox']"))
            )
            title_input.clear()
            title_input.send_keys(f"{title} #Shorts")
            print("✅ Title set")
            
        except Exception as e:
            print(f"⚠️ Could not set title: {e}")

        # Add description
        try:
            description_xpath = "//div[@id='description-container']//div[@id='textbox']"
            description_input = driver.find_element(By.XPATH, description_xpath)
            description_input.send_keys(f"{title}\n\n#esoteric #consciousness #philosophy #alanwatts #shorts")
            print("✅ Description added")
        except Exception as e:
            print(f"⚠️ Could not set description: {e}")

        # Navigate through upload steps
        print("➡️ Proceeding through upload steps...")
        
        # Click Next button 3 times to get to publish
        for i in range(3):
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='next-button']"))
                )
                next_button.click()
                time.sleep(2)
                print(f"   Step {i+1}/3 completed")
                
            except Exception as e:
                print(f"⚠️ Step {i+1} failed: {e}")

        # Publish the video
        print("🚀 Publishing video...")
        try:
            publish_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='done-button']"))
            )
            publish_button.click()
            print("✅ YouTube video published successfully!")
            
            # Wait for confirmation
            time.sleep(10)
            
        except Exception as e:
            print(f"⚠️ Could not publish video: {e}")
            print("   You may need to click Publish manually")

    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        
    finally:
        # Clean up browser
        if driver:
            try:
                driver.quit()
            except:
                pass  # Ignore cleanup errors