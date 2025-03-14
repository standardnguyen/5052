import csv
import json
import os
import re
import glob

def clean_filename(name):
    """Clean a name to make it suitable for a filename."""
    return re.sub(r'[^\w\s]', '', name).replace(' ', '_').lower()

def zero_pad_number(num, length=6):
    """Zero pad a number to the specified length."""
    return str(num).zfill(length)

def get_last_person_number(output_dir):
    """Find the highest person file number in the output directory."""
    person_files = glob.glob(os.path.join(output_dir, "person_*.json"))
    if not person_files:
        return 0

    # Extract numbers from filenames
    numbers = []
    for file in person_files:
        # Extract the number part from filename (person_000001.json -> 000001)
        match = re.search(r'person_(\d+)\.json', os.path.basename(file))
        if match:
            numbers.append(int(match.group(1)))

    return max(numbers) if numbers else 0

def get_last_position_number(output_dir):
    """Find the highest position file number in the output directory."""
    position_files = glob.glob(os.path.join(output_dir, "*_position_*.json"))
    if not position_files:
        return 0

    # Extract numbers from filenames
    numbers = []
    for file in position_files:
        # Extract the number part from filename (senator_position_0001.json)
        match = re.search(r'position_(\d+)\.json', os.path.basename(file))
        if match:
            numbers.append(int(match.group(1)))

    return max(numbers) if numbers else 0

def process_csv(csv_file, output_dir='output'):
    """Process the CSV file and generate JSON files."""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Get the last person and position numbers used
    last_person_number = get_last_person_number(output_dir)
    last_position_number = get_last_position_number(output_dir)

    print(f"Continuing from person #{last_person_number} and position #{last_position_number}")

    # Read the CSV file
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # Track created person files to avoid duplicates
        person_files = {}
        position_counter = last_position_number + 1
        person_counter = last_person_number + 1

        for row in reader:
            district = row['District']
            name = row['Name']

            # Skip if row is empty or headers
            if not district or not name or district == 'District' or name == 'Name':
                continue

            # Create person JSON file if not already created
            if name not in person_files:
                person_filename = f"person_{zero_pad_number(person_counter)}.json"
                person_files[name] = person_filename

                # Get position filename for this district
                position_filename = f"senator_position_{zero_pad_number(position_counter, 4)}.json"

                # Create the person data structure
                person_data = {
                    "name": name,
                    "district": position_filename,  # Link to the position JSON file
                    "party": row.get('Party', ''),
                    "person_wiki_url": row.get('Person Wiki URL', ''),
                    "votes": {
                        "laken_riley": {
                            "vote": row.get('Vote on Laken Riley', ''),
                            "notes": row.get('Vote on Laken Riley Notes', ''),
                            "points": row.get('Vote on Laken Riley Points', '')
                        },
                        "hr_1968": {
                            "vote": row.get('Vote on H.R.1968', ''),
                            "points": row.get('Vote on 1968 Points', '')
                        }
                    },
                    "total_points": row.get('Sum', '')
                }

                # Write person file
                person_filepath = os.path.join(output_dir, person_filename)
                with open(person_filepath, 'w', encoding='utf-8') as person_file:
                    json.dump(person_data, person_file, indent=2)
                print(f"Created person file: {person_filepath}")
                person_counter += 1

            # Create senator position JSON file
            position_filename = f"senator_position_{zero_pad_number(position_counter, 4)}.json"

            # Create the position data structure
            position_data = {
                "district": district,
                "district_wiki_url": row.get('District Wiki URL', ''),
                "seat_holder": person_files.get(name, "vacant") if name else "vacant"
            }

            # Write position file
            position_filepath = os.path.join(output_dir, position_filename)
            with open(position_filepath, 'w', encoding='utf-8') as position_file:
                json.dump(position_data, position_file, indent=2)
            print(f"Created position file: {position_filepath}")
            position_counter += 1

        print(f"Process complete. Created {person_counter - last_person_number - 1} new person files and {position_counter - last_position_number - 1} new position files.")
        print(f"Total person files: {person_counter - 1}, Total position files: {position_counter - 1}")

process_csv('./files/senators_init.csv')
