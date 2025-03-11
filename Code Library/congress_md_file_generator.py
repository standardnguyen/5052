#!/usr/bin/env python3
"""
congress_md_file_generator.py

This script processes CSV files containing information about members of Congress
(both Representatives and Senators) and generates individual markdown files for each member.
It handles various CSV formats, including the special format observed in the senators file.

The script will:
1. Read CSV files from the ./input directory
2. Create output folders (./output/representatives and ./output/senators) if they don't exist
3. Generate a markdown file for each congressperson if one doesn't already exist
4. Format the markdown with the member's name as a heading and their details below

Usage:
    python democratic_congress_md_generator.py

Requirements:
    - Input CSV files must be in ./input directory with the exact filenames:
      - "Democratic Congresspersons - Representatives.csv"
      - "Democratic Congresspersons - Senators.csv"
    - CSV files should contain columns with member information
    - Python 3.6+ recommended

Author: [Your Name]
Date: March 11, 2025
"""

import os
import csv
import pathlib
import sys

def process_congressional_data(input_file, output_folder):
    """
    Process CSV data for congressional members and create individual markdown files.

    Args:
        input_file (str): Path to the input CSV file
        output_folder (str): Path to the output folder where markdown files will be created
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    # Read the CSV file
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Check if the CSV has data
            if not reader.fieldnames:
                print(f"Warning: {input_file} appears to be empty or has no headers.")
                return

            # Process each row (congressperson)
            for row in reader:
                # Extract name based on the file structure
                name = None
                district = None

                # First try standard name columns
                for possible_name_field in ['Name', 'Full Name', 'Member', 'Congressperson']:
                    if possible_name_field in row and row[possible_name_field]:
                        name = row[possible_name_field]
                        break

                # Special handling for senators file format
                if not name and "Senators" in input_file:
                    # Check if this is the format where the senator name is a value (not a key)
                    # e.g., {'Alabama': 'Ohio', 'Tommy Tuberville': 'Bernie Moreno', ...}
                    senator_key = None
                    for key in row.keys():
                        # Look for keys that might be senator names (not state names, numbers, or URLs)
                        if (key not in ['Alabama', 'Republican', 'Democratic'] and
                            not key.isdigit() and
                            not key.startswith('http')):
                            senator_key = key
                            break

                    if senator_key and row[senator_key]:
                        name = row[senator_key]  # Use the value of this field as the name
                        # Also get the state from the corresponding column
                        for state_key in row.keys():
                            if state_key in ['Alabama', 'State']:
                                district = row[state_key]
                                break

                # Special handling for representatives file format
                if not name and "Representatives" in input_file:
                    # The format is similar to senators, but includes district information
                    # e.g., {'Alabama 1': 'Tennessee 9', 'Barry Moore': 'Steve Cohen', ...}
                    rep_key = None
                    district_key = None

                    for key in row.keys():
                        # Find the key that likely contains a representative name
                        if not key.isdigit() and not key.startswith('http') and 'Republican' not in key and 'Democratic' not in key:
                            # Check if the key contains a number (district indicator)
                            if any(char.isdigit() for char in key):
                                district_key = key
                            # Otherwise it might be a representative name
                            elif not key.isdigit() and key not in ['Republican', 'Democratic', 'Alabama']:
                                rep_key = key

                    if rep_key and row[rep_key]:
                        name = row[rep_key]

                    if district_key and row[district_key]:
                        district = row[district_key]

                if not name:
                    print(f"Warning: Could not find name in row: {row}")
                    continue

                # Create a valid filename from the name
                filename = name.replace(' ', '_').replace(',', '').replace('.', '')
                md_path = os.path.join(output_folder, f"{filename}.md")

                # Skip if file already exists
                if os.path.exists(md_path):
                    print(f"File already exists, skipping: {md_path}")
                    continue

                # Create markdown content from the row data
                content = f"# {name}\n\n"

                # Handle different structures for different files
                if "Senators" in input_file:
                    # Special handling for senators CSV structure
                    state = row.get('Alabama', '')
                    party = row.get('Republican', '')
                    link = ''

                    # Find the Wikipedia link if it exists
                    for key, value in row.items():
                        if key.startswith('http') and 'wikipedia' in value:
                            link = value
                            break

                    # Add the extracted information
                    if state:
                        content += f"**State**: {state}\n\n"
                    if party:
                        content += f"**Party**: {party}\n\n"
                    if link:
                        content += f"**Wikipedia**: [{link}]({link})\n\n"

                elif "Representatives" in input_file:
                    # Special handling for representatives CSV structure
                    party = row.get('Republican', '')
                    link = ''

                    # Find the Wikipedia link if it exists
                    for key, value in row.items():
                        if key.startswith('http') and 'wikipedia' in value and 'district' not in value:
                            link = value
                            break

                    # Add the extracted information
                    if district:
                        content += f"**District**: {district}\n\n"
                    if party:
                        content += f"**Party**: {party}\n\n"
                    if link:
                        content += f"**Wikipedia**: [{link}]({link})\n\n"

                    # Get the district link
                    district_link = ''
                    for key, value in row.items():
                        if key.startswith('http') and 'district' in value:
                            district_link = value
                            break
                    if district_link:
                        content += f"**District Info**: [{district_link}]({district_link})\n\n"
                else:
                    # Standard handling for other files
                    for key, value in row.items():
                        if key not in ['Name', 'Full Name', 'Member', 'Congressperson'] and value:
                            content += f"**{key}**: {value}\n\n"

                # Write to markdown file
                with open(md_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(content)

                print(f"Created file: {md_path}")

    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")

def main():
    """
    Main function to process both Representatives and Senators CSV files.
    - Checks if input directory exists
    - Processes both files and generates markdown files in output directories
    """
    # Base directories
    input_dir = "./input"
    output_dir = "./output"

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found. Please create this directory and add the CSV files.")
        sys.exit(1)

    print(f"Starting processing of Democratic Congress data...")

    # Process Representatives
    rep_input = os.path.join(input_dir, "Democratic Congresspersons - Representatives.csv")
    rep_output = os.path.join(output_dir, "representatives")
    print(f"Processing Representatives from: {rep_input}")
    process_congressional_data(rep_input, rep_output)

    # Process Senators
    sen_input = os.path.join(input_dir, "Democratic Congresspersons - Senators.csv")
    sen_output = os.path.join(output_dir, "senators")
    print(f"Processing Senators from: {sen_input}")
    process_congressional_data(sen_input, sen_output)

    print(f"Processing complete. Output files can be found in: {output_dir}/representatives and {output_dir}/senators")

if __name__ == "__main__":
    main()
