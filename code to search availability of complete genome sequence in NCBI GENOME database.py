import time
import pandas as pd
from Bio import Entrez

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
# ALWAYS provide your email when using NCBI Entrez
Entrez.email = "your_email@example.com"

INPUT_FILE = "TEMPURA.xlsx"   # Name of your input Excel file
OUTPUT_FILE = "ncbi_search_results.xlsx" # Name of the file to save results
COLUMN_NAME = "Bacterial Name"          # The column header containing the strain names

# -------------------------------------------------------------
# Helper Function to Check NCBI
# -------------------------------------------------------------
def check_complete_genome(strain_name):
    """
    Searches the NCBI Assembly database for a specific strain
    and checks if a 'Complete Genome' is available.
    """
    if pd.isna(strain_name) or str(strain_name).strip() == "":
        return "No"
    
    # Construct a specific search query for the Assembly database
    query = f'"{strain_name.strip()}"[Organism] AND "complete genome"[Assembly Level] AND latest[Filter]'
    
    try:
        handle = Entrez.esearch(db="assembly", term=query, retmax=1)
        record = Entrez.read(handle)
        handle.close()
        
        # If IDList contains any IDs, it means a complete genome was found
        if record["IdList"]:
            return "Yes"
        else:
            return "No"
            
    except Exception as e:
        print(f"Error searching for '{strain_name}': {e}")
        return "Error/Timeout"

# -------------------------------------------------------------
# Main Execution
# -------------------------------------------------------------
def main():
    print(f"Reading {INPUT_FILE}...")
    # Reads ALL columns from your original sheet
    df = pd.read_excel(INPUT_FILE)
    
    if COLUMN_NAME not in df.columns:
        print(f"Error: Column '{COLUMN_NAME}' not found in the Excel file.")
        print(f"Available columns: {list(df.columns)}")
        return

    print("Starting NCBI database search (this will preserve all original columns)...")
    results = []
    
    for idx, row in df.iterrows():
        strain = row[COLUMN_NAME]
        print(f"Checking [{idx + 1}/{len(df)}]: {strain} ... ", end="", flush=True)
        
        status = check_complete_genome(strain)
        print(status)
        results.append(status)
        
        # Respect NCBI's rate limits (max 3 requests per second without an API key)
        time.sleep(0.4)
    
    # Safely insert the new column at the very end of the existing dataframe
    df["Complete Sequence Available"] = results
    
    # Save the entire dataframe (original columns + new column) to the output file
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nDone! All original data + results successfully saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()