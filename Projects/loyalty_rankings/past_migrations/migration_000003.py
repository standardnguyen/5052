import os
import json
import glob
import requests
from bs4 import BeautifulSoup
import re
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("headshot_migration.log"),
        logging.StreamHandler()
    ]
)

def get_headshot_url(wiki_url):
    """
    Crawl the Wikipedia page and extract the headshot image URL.

    Args:
        wiki_url (str): The Wikipedia URL to crawl

    Returns:
        str or None: The full image URL if found, None otherwise
    """
    if not wiki_url:
        return None

    # Add a delay to avoid hitting rate limits
    time.sleep(1)

    try:
        # Make sure the URL is properly formatted
        if not wiki_url.startswith('http'):
            wiki_url = f"https://en.wikipedia.org{wiki_url}"

        # Fetch the page
        response = requests.get(wiki_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for the image link with class mw-file-description
        image_link = soup.select_one('a.mw-file-description')

        if not image_link:
            logging.warning(f"No image link found on {wiki_url}")
            return None

        # Get the href attribute
        href = image_link.get('href')
        if not href:
            logging.warning(f"Image link has no href on {wiki_url}")
            return None

        # Find the img element within the link
        img = image_link.find('img')
        if not img:
            logging.warning(f"No img element found in the link on {wiki_url}")
            return None

        # Extract the source URL and convert to full resolution
        src = img.get('src')
        if not src:
            logging.warning(f"No src attribute found in the img element on {wiki_url}")
            return None

        # Get the data-file-width and data-file-height
        data_file_width = img.get('data-file-width')
        data_file_height = img.get('data-file-height')

        # Extract the base filename from the src
        match = re.search(r'(/[^/]+\.jpg)', src)
        if not match:
            # Try to construct from the href instead
            file_name = os.path.basename(href)
            # Convert URL encoding
            file_name = file_name.replace('File:', '')

            # If we can't extract the filename, use the src as fallback
            if not file_name:
                logging.warning(f"Using thumbnail URL as fallback for {wiki_url}")
                # Make sure the src has a proper protocol
                if src.startswith('//'):
                    return f"https:{src}"
                return src

            # Try to construct the full URL
            commons_url = f"https://commons.wikimedia.org/wiki/File:{file_name}"
            try:
                commons_response = requests.get(commons_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                commons_response.raise_for_status()
                commons_soup = BeautifulSoup(commons_response.text, 'html.parser')
                full_img_link = commons_soup.select_one('.fullImageLink a')
                if full_img_link and full_img_link.get('href'):
                    full_url = full_img_link.get('href')
                    if full_url.startswith('//'):
                        full_url = f"https:{full_url}"
                    return full_url
            except Exception as e:
                logging.error(f"Error fetching Commons page: {e}")

            # If we can't get it from Commons, construct a URL based on the filename
            file_name_encoded = file_name.replace(' ', '_')
            return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{file_name_encoded[0]}/{file_name_encoded[0:2]}/{file_name_encoded}"

        # Extract the base path from the src
        base_path = match.group(1)

        # Identify the directory structure (typically first two chars of the file hash)
        src_parts = src.split('/')
        if len(src_parts) >= 4:
            hash_dir = '/'.join(src_parts[-4:-2])  # Get the hash directory parts

            # Construct the full resolution URL
            full_url = f"https://upload.wikimedia.org/wikipedia/commons/{hash_dir}{base_path}"
            return full_url

        # If we can't parse properly, use the thumbnail URL as fallback
        logging.warning(f"Using thumbnail URL as fallback for {wiki_url}")
        if src.startswith('//'):
            return f"https:{src}"
        return src

    except Exception as e:
        logging.error(f"Error processing {wiki_url}: {str(e)}")
        return None

def process_person_files(output_dir='output'):
    """
    Process all person JSON files in the output directory.

    Args:
        output_dir (str): The directory containing the person JSON files
    """
    # Find all person files
    person_files = glob.glob(os.path.join(output_dir, "person_*.json"))
    logging.info(f"Found {len(person_files)} person files to process")

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in person_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                person_data = json.load(file)

            # Skip if headshot_url already exists
            if "headshot_url" in person_data and person_data["headshot_url"]:
                logging.info(f"Skipping {file_path} - headshot_url already exists")
                skipped_count += 1
                continue

            # Get the person_wiki_url
            wiki_url = person_data.get("person_wiki_url")
            if not wiki_url:
                logging.warning(f"No person_wiki_url found in {file_path}")
                skipped_count += 1
                continue

            # Get the headshot URL
            logging.info(f"Processing {person_data.get('name', 'Unknown')} from {wiki_url}")
            headshot_url = get_headshot_url(wiki_url)

            if headshot_url:
                # Update the person data
                person_data["headshot_url"] = headshot_url

                # Write the updated data back to the file
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(person_data, file, indent=2)

                logging.info(f"Updated {file_path} with headshot_url: {headshot_url}")
                updated_count += 1
            else:
                logging.warning(f"No headshot found for {person_data.get('name', 'Unknown')} at {wiki_url}")
                error_count += 1

        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")
            error_count += 1

    logging.info(f"Migration complete. Updated: {updated_count}, Skipped: {skipped_count}, Errors: {error_count}")

process_person_files()
