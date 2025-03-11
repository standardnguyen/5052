#!/usr/bin/env python3
"""
simplified_congress_md_generator.py

This script processes CSV files containing information about members of Congress
(both Representatives and Senators) and generates individual markdown files for each member.

The script will:
1. Read CSV files from the ./input directory
2. Create output folders (./output/representatives and ./output/senators) if they don't exist
3. Generate a markdown file for each congressperson
4. Format the markdown with the member's name as a heading and their details below

CSV Structure:
- Representatives: District, Name, Party, ID, District Wikipedia URL, Member Wikipedia URL
- Senators: State, Name, Party, ID, Wikipedia URL

Features:
- Handles vacant positions by skipping them
- Properly manages special characters in names for filenames
- Identifies and skips error URLs
- Creates clean, well-formatted markdown files

Usage:
    python simplified_congress_md_generator.py

Requirements:
    - Input CSV files must be in ./input directory with the exact filenames:
      - "Democratic Congresspersons - Representatives.csv"
      - "Democratic Congresspersons - Senators.csv"
    - Python 3.6+ recommended

Date: March 11, 2025
"""

import os
import csv
import sys

def sanitize_filename(name):
    """
    Create a valid filename from a person's name by removing problematic characters.

    Args:
        name (str): The person's name

    Returns:
        str: A sanitized filename
    """
    return name.replace(' ', '_').replace(',', '').replace('.', '').replace('(', '').replace(')', '')

def process_representatives(input_file, output_folder):
    """
    Process CSV data for Representatives and create individual markdown files.

    CSV format: District, Name, Party, ID, District Wikipedia URL, Member Wikipedia URL

    Args:
        input_file (str): Path to the input CSV file
        output_folder (str): Path to the output folder where markdown files will be created
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    # Track processed count
    processed_count = 0
    skipped_count = 0

    # Read the CSV file
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)

            # Process each row (representative)
            for row in reader:
                if len(row) < 6:
                    print(f"Warning: Skipping incomplete row: {row}")
                    skipped_count += 1
                    continue

                # Handle special cases like Vacant positions
                district = row[0]
                name = row[1]
                party = row[2]

                # Skip rows where name is Vacant
                if name.lower() == "vacant":
                    print(f"Skipping vacant position: {district}")
                    skipped_count += 1
                    continue

                # Handle cases where URLs might be missing or malformed
                district_wiki = row[4] if len(row) > 4 and not row[4].startswith("#ERROR") else ""
                member_wiki = row[5] if len(row) > 5 and not (row[5] == "" or row[5].startswith("#ERROR")) else ""

                # Create a valid filename from the name
                filename = sanitize_filename(name)
                md_path = os.path.join(output_folder, f"{filename}.md")

                # Skip if file already exists
                if os.path.exists(md_path):
                    print(f"File already exists, skipping: {md_path}")
                    skipped_count += 1
                    continue

                # Create markdown content
                content = f"# {name}\n\n"
                content += f"**District**: {district}\n\n"
                content += f"**Party**: {party}\n\n"

                if member_wiki:
                    content += f"**Wikipedia**: [{name}]({member_wiki})\n\n"

                if district_wiki:
                    content += f"**District Info**: [{district}]({district_wiki})\n\n"

                # Write to markdown file
                with open(md_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(content)

                processed_count += 1
                print(f"Created file: {md_path}")

        print(f"Representatives processing complete: {processed_count} files created, {skipped_count} entries skipped")

    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")

def process_senators(input_file, output_folder):
    """
    Process CSV data for Senators and create individual markdown files.

    CSV format: State, Name, Party, ID, Wikipedia URL

    Args:
        input_file (str): Path to the input CSV file
        output_folder (str): Path to the output folder where markdown files will be created
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    # Track processed count
    processed_count = 0
    skipped_count = 0

    # Read the CSV file
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)

            # Process each row (senator)
            for row in reader:
                if len(row) < 4:
                    print(f"Warning: Skipping incomplete row: {row}")
                    skipped_count += 1
                    continue

                state = row[0]
                name = row[1]
                party = row[2]

                # Skip if name is vacant
                if name.lower() == "vacant":
                    print(f"Skipping vacant position for: {state}")
                    skipped_count += 1
                    continue

                # Handle missing or malformed Wikipedia URL
                wiki_url = row[4] if len(row) > 4 and not row[4].startswith("#ERROR") else ""

                # Create a valid filename from the name
                filename = sanitize_filename(name)
                md_path = os.path.join(output_folder, f"{filename}.md")

                # Skip if file already exists
                if os.path.exists(md_path):
                    print(f"File already exists, skipping: {md_path}")
                    skipped_count += 1
                    continue

                # Create markdown content
                content = f"# {name}\n\n"
                content += f"**State**: {state}\n\n"
                content += f"**Party**: {party}\n\n"

                if wiki_url:
                    content += f"**Wikipedia**: [{name}]({wiki_url})\n\n"

                # Write to markdown file
                with open(md_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(content)

                processed_count += 1
                print(f"Created file: {md_path}")

        print(f"Senators processing complete: {processed_count} files created, {skipped_count} entries skipped")

    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")

def main():
    """
    Main function to process both Representatives and Senators CSV files.
    """
    # Base directories
    input_dir = "./input"
    output_dir = "./output"

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found. Please create this directory and add the CSV files.")
        sys.exit(1)

    print(f"Starting processing of Congress data...")

    # Process Representatives
    rep_input = os.path.join(input_dir, "Democratic Congresspersons - Representatives.csv")
    rep_output = os.path.join(output_dir, "representatives")
    print(f"Processing Representatives from: {rep_input}")
    process_representatives(rep_input, rep_output)

    # Process Senators
    sen_input = os.path.join(input_dir, "Democratic Congresspersons - Senators.csv")
    sen_output = os.path.join(output_dir, "senators")
    print(f"Processing Senators from: {sen_input}")
    process_senators(sen_input, sen_output)

    print(f"Processing complete. Output files can be found in: {output_dir}/representatives and {output_dir}/senators")

if __name__ == "__main__":
    main()
