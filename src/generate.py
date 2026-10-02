import csv
import os

def generate_csvs(output_dir="data", num_files=2):
    os.makedirs(output_dir, exist_ok=True)
    
    base_transactions = [
        ["2023-10-01 10:00:00", "FR123", "France", "BNP", "DE456", "Allemagne", 1500.00],
        ["2023-10-01 10:15:00", "FR123", "France", "BNP", "ES789", "Espagne", 6000.00], # Flag > 5000
        ["2023-10-01 10:30:00", "IT111", "Italie", "UniCredit", "DE456", "Allemagne", 500.00],
        ["2023-10-01 11:00:00", "FR999", "France", "Societe Generale", "FR123", "France", 100.00],
        ["2023-10-01 11:30:00", "FR123", "France", "BNP", "IT111", "Italie", 200.00],
    ]

    columns = ["datetime_transaction", "iban_origine", "pays_source", "banque_source", 
               "iban_destinataire", "pays_destinataire", "montant"]

    for i in range(num_files):
        filepath = os.path.join(output_dir, f"transactions_batch_{i+1}.csv")
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(base_transactions)
        print(f"Fichier généré : {filepath}")

if __name__ == "__main__":
    generate_csvs()