import csv
import json
import os
import re

def clean_filename(name):
    """Clean a name to make it suitable for a filename."""
    return re.sub(r'[^\w\s]', '', name).replace(' ', '_').lower()

def zero_pad_number(num, length=6):
    """Zero pad a number to the specified length."""
    return str(num).zfill(length)

def process_csv(csv_file, output_dir='output'):
    """Process the CSV file and generate JSON files."""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the CSV file
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        # Track created person files to avoid duplicates
        person_files = {}
        position_counter = 1
        person_counter = 1

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
                position_filename = f"congressional_representative_position_{zero_pad_number(position_counter, 4)}.json"

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
                with open(os.path.join(output_dir, person_filename), 'w', encoding='utf-8') as person_file:
                    json.dump(person_data, person_file, indent=2)

                person_counter += 1

            # Create congressional representative position JSON file - defined earlier for reference in person JSON

            # Create the position data structure
            position_data = {
                "district": district,
                "district_wiki_url": row.get('District Wiki URL', ''),
                "seat_holder": person_files.get(name, "vacant") if name else "vacant"
            }

            # Write position file
            with open(os.path.join(output_dir, position_filename), 'w', encoding='utf-8') as position_file:
                json.dump(position_data, position_file, indent=2)

            position_counter += 1

process_csv('./files/representatives_init.csv')
