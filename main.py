import os
import glob
from src.generate import generate_csvs
from src.process import load_csv, add_high_amount_flag, calculate_sums
from src.db import init_db, insert_with_retry

def run_pipeline():
    print("--- 1. Génération des données ---")
    generate_csvs(output_dir="data", num_files=2)

    print("\n--- 2. Initialisation de la base de données ---")
    db_path = "pipeline.db"
    init_db(db_path)

    print("\n--- 3. Chargement, traitement et insertion ---")
    csv_files = glob.glob("data/*.csv")
    
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        df = load_csv(filepath)
        
        # Traitement
        df_flagged = add_high_amount_flag(df)
        sums = calculate_sums(df_flagged)
        
        print(f"\nRésultats des sommes pour {filename}:")
        for categorie, valeurs in sums.items():
            print(f"  {categorie}: {valeurs}")
        
        # Insertion
        insert_with_retry(db_path, df_flagged, filename)

if __name__ == "__main__":
    run_pipeline()