import os
from src.generate import generate_csv
from src.process import load_csv, apply_business_rules, aggregate_data
from src.db import init_db, insert_transactions_with_retry

def run_pipeline(simulate_fail=False):
    # 1. Initialisation de la base de données
    init_db()
    data_dir = "data"
    filename = "transactions.csv"
    file_path = os.path.join(data_dir, filename)
    
    # 2. Génération du fichier CSV unique (incluant la 4ème ligne erronée)
    generate_csv(output_dir=data_dir, filename=filename)
    
    # 3. Chargement des données
    print(f"\nTraitement du fichier : {file_path} ...")
    raw_data = load_csv(file_path)
    
    # 4. Traitement (le Data Quality Check dans apply_business_rules ignorera l'erreur)
    processed_data = apply_business_rules(raw_data)
    
    # 5. Calcul des agrégations sur les données valides
    aggregations = aggregate_data(processed_data)
    print("Résultats des agrégations :", aggregations)
    
    # 6. Insertion en base avec mécanisme de retry (Étape 7)
    insert_transactions_with_retry(processed_data, file_path, simulate_fail=simulate_fail)

if __name__ == "__main__":
    # Passer simulate_fail=True pour tester le mécanisme de retry de l'étape 7
    run_pipeline(simulate_fail=False)