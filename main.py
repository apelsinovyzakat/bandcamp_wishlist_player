import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pydub import AudioSegment
import warnings
AudioSegment.ffmpeg = "path/to/ffmpeg"


# Input username and construct the wishlist URL
username = input("Enter your username: ")
username_link = f"https://bandcamp.com/{username}/wishlist"

class Test1:
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1200, 800)  # Adjust window size
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_1(self, username_link):
        self.driver.get(username_link)

        # Wait for the "Show More" button to be visible
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#wishlist-items .show-more"))
        )

        # Scroll into view
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)  # Give time for the page to adjust

        # Try clicking, if intercepted, use JavaScript
        try:
            element.click()
        except:
            self.driver.execute_script("arguments[0].click();", element)

        # Scroll down the page to load more items
        scroll_positions_list = [i * 5000 for i in range(5)]
        for pos in scroll_positions_list:
            self.driver.execute_script(f"window.scrollTo(0, {pos});")
            time.sleep(0.7)  # Allow page elements to load before scrolling further

        # Extract album links
        album_links = []
        album_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a.item-link')
        for album in album_elements:
            link = album.get_attribute('href')  # Extract the album link
            if link:  # Filter out None values
                album_links.append(link)

        # Remove duplicates by converting to a set and back to a list
        filtered_album_links = list(set(album_links))

        # Print the list of album links
        print("Extracted album links:", len(filtered_album_links))

        return filtered_album_links


def convert_tmp_to_mp3(directory):
    """Convert .tmp files to .mp3 in the specified directory."""
    for filename in os.listdir(directory):
        if filename.endswith(".tmp"):
            tmp_path = os.path.join(directory, filename)
            mp3_path = os.path.join(directory, filename.replace(".tmp", ".mp3"))

            try:
                audio = AudioSegment.from_file(tmp_path)  # Read file
                audio.export(mp3_path, format="mp3")  # Convert to MP3
                os.remove(tmp_path)  # Delete the original .tmp file
                print(f"✅ Converted: {filename} → {mp3_path}")
            except Exception as e:
                print(f"❌ Failed to convert {filename}: {e}")



# Run the function

def download_album(album_url, save_path="downloads"):
    os.makedirs(save_path, exist_ok=True)  # Ensure the directory exists

    command = [
        "bandcamp-dl",
        "--base-dir", save_path,  # Set the download directory
        "--no-slugify",  # Keep track names unchanged
        album_url  # The album URL to download
    ]

    try:
        subprocess.run(command, check=True)
        convert_tmp_to_mp3(save_path)
        print(f"✅ Download complete: {album_url}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download album: {album_url}\nError: {e}")

# Main execution
if __name__ == "__main__":
    test = Test1()
    test.setup_method(None)  # Initialize the WebDriver
    try:
        filtered_album_links = test.test_1(username_link)  # Extract album links
    finally:
        test.teardown_method(None)  # Close the WebDriver

    # Download tracks from the extracted links
    for album_url in filtered_album_links:
        download_album(album_url)