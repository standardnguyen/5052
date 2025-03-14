import os
import json
import glob
import requests
import logging
import time
import shutil
from pathlib import Path
from urllib.parse import urlparse

# Set up logging
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "migration_000005.log")),
        logging.StreamHandler()
    ]
)

def download_headshot(url, person_name, output_dir):
    """
    Download a headshot image from the given URL.

    Args:
        url (str): The URL of the headshot image
        person_name (str): The name of the person (for filename generation)
        output_dir (str): The directory to save the image

    Returns:
        str or None: The local path where the image was saved, None if download failed
    """
    if not url:
        return None

    try:
        # Add a delay to avoid hitting rate limits
        time.sleep(0.5)

        # Make the request
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }, stream=True)
        response.raise_for_status()

        # Create a safe filename from person's name
        safe_name = "".join([c if c.isalnum() else "_" for c in person_name]).lower()

        # Get file extension from URL or default to .jpg
        parsed_url = urlparse(url)
        path = parsed_url.path
        extension = os.path.splitext(path)[1]
        if not extension or len(extension) > 5:  # Sanity check on extension
            extension = '.jpg'

        # Create filename with person name
        filename = f"{safe_name}{extension}"

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Full path for the image
        image_path = os.path.join(output_dir, filename)

        # If file already exists, add a counter
        counter = 1
        while os.path.exists(image_path):
            filename = f"{safe_name}_{counter}{extension}"
            image_path = os.path.join(output_dir, filename)
            counter += 1

        # Save the image
        with open(image_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        logging.info(f"Downloaded headshot for {person_name} to {image_path}")

        # Return the relative path from the static folder
        return os.path.relpath(image_path, os.path.dirname(os.path.dirname(output_dir)))

    except Exception as e:
        logging.error(f"Error downloading headshot for {person_name} from {url}: {str(e)}")
        return None

def download_and_update_headshots(output_dir='output', headshots_dir='static/headshots'):
    """
    Process all person JSON files, download headshots, and update with local paths.

    Args:
        output_dir (str): The directory containing the person JSON files
        headshots_dir (str): The directory to save the headshot images
    """
    # Find all person files
    person_files = glob.glob(os.path.join(output_dir, "person_*.json"))
    logging.info(f"Found {len(person_files)} person files to process")

    downloaded_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in person_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                person_data = json.load(file)

            # Skip if headshot_local_url already exists
            if "headshot_local_url" in person_data and person_data["headshot_local_url"]:
                logging.info(f"Skipping {file_path} - headshot_local_url already exists")
                skipped_count += 1
                continue

            # Get the headshot_url
            headshot_url = person_data.get("headshot_url")
            if not headshot_url:
                logging.warning(f"No headshot_url found in {file_path}")
                skipped_count += 1
                continue

            # Get the person's name
            person_name = person_data.get("name", "unknown_person")

            # Download the headshot
            logging.info(f"Downloading headshot for {person_name} from {headshot_url}")
            local_path = download_headshot(headshot_url, person_name, headshots_dir)

            if local_path:
                # Update the person data with the local path
                person_data["headshot_local_url"] = local_path

                # Write the updated data back to the file
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(person_data, file, indent=2)

                logging.info(f"Updated {file_path} with headshot_local_url: {local_path}")
                downloaded_count += 1
            else:
                logging.warning(f"Failed to download headshot for {person_name} from {headshot_url}")
                error_count += 1

        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")
            error_count += 1

    logging.info(f"Download migration complete. Downloaded: {downloaded_count}, Skipped: {skipped_count}, Errors: {error_count}")

download_and_update_headshots()
