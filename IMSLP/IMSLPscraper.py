from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import os
import requests
import urllib.parse

def download_imslp_pdfs():
    try:
        # Create a directory to save PDFs if it doesn't exist
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            print(f"Created download directory: {download_dir}")
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")  # Start with maximized browser window
        
        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to the IMSLP page
        url = "https://imslp.org/wiki/Special:DiffPage/DiffMain/1"
        print(f"Opening URL: {url}")
        driver.get(url)
        
        # Wait for the page to load completely
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("Page loaded successfully!")
        
        # Find the dropdown menu and set it to 500 rows
        try:
            # Find the dropdown with class "fnxtnumrows"
            dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "fnxtnumrows"))
            )
            
            # Create a Select object
            select = Select(dropdown)
            
            # Select the option with value "500" or text "500"
            try:
                select.select_by_value("500")
            except:
                try:
                    select.select_by_visible_text("500")
                except:
                    # If 500 is not available, try to find the maximum available option
                    options = select.options
                    max_value = 0
                    max_option = None
                    
                    for option in options:
                        try:
                            value = int(option.text.strip())
                            if value > max_value:
                                max_value = value
                                max_option = option
                        except:
                            continue
                    
                    if max_option:
                        print(f"500 option not found. Selecting maximum available: {max_value}")
                        select.select_by_visible_text(max_option.text.strip())
                    else:
                        print("Could not set rows to 500. Using default.")
            
            # Wait for the page to reload after changing the dropdown
            time.sleep(3)
            print("Set number of rows successfully!")
            
        except Exception as e:
            print(f"Error setting rows to 500: {e}")
        
        # Find all elements with class "difficultyfilewidth"
        file_elements = driver.find_elements(By.CLASS_NAME, "difficultyfilewidth")
        
        if not file_elements:
            print("No elements with class 'difficultyfilewidth' found.")
            print("Keeping browser open for 5 minutes for inspection...")
            time.sleep(300)  # 5 minutes
            driver.quit()
            return
            
        print(f"Found {len(file_elements)} difficultyfilewidth elements")
        
        # Extract all links from difficultyfilewidth elements
        file_links = []
        link_count = 0
        
        for i, element in enumerate(file_elements, 1):
            try:
                # Find all links inside this element
                links = element.find_elements(By.TAG_NAME, "a")
                
                for j, link in enumerate(links, 1):
                    # Get link text and href
                    link_text = link.text.strip() or "[No text]"
                    link_href = link.get_attribute("href")
                    
                    print(f"Element {i}, Link {j}: {link_text} ({link_href})")
                    file_links.append({"text": link_text, "url": link_href})
                    
                    # Click the link (opens in new tab/window)
                    link.click()
                    print(f"Clicked on link: {link_text} ({link_count + 1})")
                    
                    # Switch to the new tab
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    # Wait for the page to load
                    time.sleep(2)
                    
                    # Check if disclaimer page is present and click "I understand" if found
                    try:
                        # Look for the "I understand" link
                        disclaimer_link = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'I understand')]"))
                        )
                        
                        print("Found 'I understand' disclaimer. Clicking it...")
                        disclaimer_link.click()
                        
                        # Wait for the page to load after clicking the disclaimer
                        time.sleep(2)
                        print("Clicked on 'I understand' and proceeded to the content page.")
                    except Exception as e:
                        print("No disclaimer found or error handling disclaimer:", e)
                    
                    # Check for the second verification link with "I understand, continue" button
                    try:
                        # Look for the "I understand, continue" link with class "bigbutton"
                        continue_link = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'bigbutton') and contains(text(), 'I understand, continue')]"))
                        )
                        
                        print("Found 'I understand, continue' button. Clicking it...")
                        pdf_url = continue_link.get_attribute("href")
                        continue_link.click()
                        
                        # Wait for the page to load after clicking the continue button
                        time.sleep(2)
                        print("Clicked on 'I understand, continue' and proceeded to the PDF.")
                        
                        # Extract filename from URL
                        parsed_url = urllib.parse.urlparse(pdf_url)
                        filename = os.path.basename(parsed_url.path)
                        
                        # If filename is empty or doesn't end with .pdf, create a custom name
                        if not filename or not filename.lower().endswith(('.pdf', '.jpg', '.png')):
                            filename = f"imslp_download_{link_count + 1}.pdf"
                        
                        # Add file number at the beginning of the filename
                        numbered_filename = f"{link_count + 1:03d}_{filename}"
                        
                        # Download the file directly from the href
                        print(f"Downloading file from direct link: {numbered_filename}")
                        response = requests.get(pdf_url, stream=True)
                        
                        if response.status_code == 200:
                            file_path = os.path.join(download_dir, numbered_filename)
                            with open(file_path, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            print(f"Successfully downloaded: {file_path}")
                        else:
                            print(f"Failed to download file. Status code: {response.status_code}")
                            
                        # Continue to next link since we've already handled the PDF
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        link_count += 1
                        continue
                        
                    except Exception as e:
                        print("No 'I understand, continue' button found or error handling it:", e)
                    
                    # Now look for the download link (only if we didn't already download from the continue button)
                    try:
                        # Look for the "Click here to continue your download" link
                        download_link = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//a[contains(., 'Click here to continue your download')]"))
                        )
                        
                        # Get the href attribute
                        pdf_url = download_link.get_attribute("href")
                        print(f"Found download link: {pdf_url}")
                        
                        # Extract filename from URL
                        parsed_url = urllib.parse.urlparse(pdf_url)
                        filename = os.path.basename(parsed_url.path)
                        
                        # If filename is empty or doesn't end with .pdf, create a custom name
                        if not filename or not filename.lower().endswith(('.pdf', '.jpg', '.png')):
                            filename = f"imslp_download_{link_count + 1}.pdf"
                        
                        # Add file number at the beginning of the filename
                        numbered_filename = f"{link_count + 1:03d}_{filename}"
                        
                        # Download the file
                        print(f"Downloading file: {numbered_filename}")
                        response = requests.get(pdf_url, stream=True)
                        
                        if response.status_code == 200:
                            file_path = os.path.join(download_dir, numbered_filename)
                            with open(file_path, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            print(f"Successfully downloaded: {file_path}")
                        else:
                            print(f"Failed to download file. Status code: {response.status_code}")
                            
                    except Exception as e:
                        print(f"Error finding or downloading PDF: {e}")
                    
                    # Close the current tab and switch back to the main window
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
                    # Small delay to avoid overwhelming the browser
                    time.sleep(1)
                    
                    link_count += 1
            except Exception as e:
                print(f"Error processing element {i}: {e}")
        
        # Save links to a file
        with open("difficultyfilewidth_links.txt", "w", encoding="utf-8") as f:
            f.write(f"Links extracted from {url}\n")
            f.write(f"Total links clicked: {len(file_links)}\n\n")
            for i, link in enumerate(file_links, 1):
                f.write(f"{i}. Text: {link['text']} | URL: {link['url']}\n")
        
        print(f"\nLinks saved to 'difficultyfilewidth_links.txt'")
        
        # Keep the browser open for a minute
        print("Keeping browser open for 1 minute for inspection...")
        time.sleep(60)  # 1 minute
        
        # Close the browser
        driver.quit()
        print("Browser closed.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        # Attempt to close the browser if an error occurs
        try:
            driver.quit()
        except:
            pass

# Call the function if this script is run directly
if __name__ == "__main__":
    download_imslp_pdfs()