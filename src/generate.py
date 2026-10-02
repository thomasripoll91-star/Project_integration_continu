import csv
import os
from datetime import datetime, timedelta

def generate_single_csv_with_error(output_dir="data", filename="transactions.csv"):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    
    # 8 enregistrements dans un seul fichier
    base_transactions = [
        {"iban_origine": "FR123", "pays_source": "FR", "banque_source": "BNP", "iban_destinataire": "DE456", "pays_destinataire": "DE", "montant": 1500.0},
        {"iban_origine": "FR123", "pays_source": "FR", "banque_source": "BNP", "iban_destinataire": "ES789", "pays_destinataire": "ES", "montant": 5500.0},
        {"iban_origine": "BE111", "pays_source": "BE", "banque_source": "ING", "iban_destinataire": "FR123", "pays_destinataire": "FR", "montant": 250.0},
        
        # INJECTION DE L'ERREUR : La 4ème transaction contient une chaîne de caractères au lieu d'un float
        {"iban_origine": "DE456", "pays_source": "DE", "banque_source": "N26", "iban_destinataire": "IT222", "pays_destinataire": "IT", "montant": "INVALID_MONTANT"}, 
        
        {"iban_origine": "IT222", "pays_source": "IT", "banque_source": "UniCredit", "iban_destinataire": "BE111", "pays_destinataire": "BE", "montant": 420.5},
        {"iban_origine": "ES789", "pays_source": "ES", "banque_source": "Santander", "iban_destinataire": "PT333", "pays_destinataire": "PT", "montant": 1200.0},
        {"iban_origine": "NL444", "pays_source": "NL", "banque_source": "Rabobank", "iban_destinataire": "FR123", "pays_destinataire": "FR", "montant": 6000.0},
        {"iban_origine": "LU555", "pays_source": "LU", "banque_source": "BGL", "iban_destinataire": "DE456", "pays_destinataire": "DE", "montant": 300.0}
    ]

    fieldnames = [
        "datetime_transaction", "iban_origine", "pays_source", 
        "banque_source", "iban_destinataire", "pays_destinataire", "montant"
    ]

    base_time = datetime.now()

    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for row_idx, transaction in enumerate(base_transactions):
            tx_time = base_time + timedelta(minutes=row_idx)
            transaction["datetime_transaction"] = tx_time.strftime("%Y-%m-%dT%H:%M:%S")
            writer.writerow(transaction)
            
    print(f"Fichier créé : {file_path} avec {len(base_transactions)} enregistrements[cite: 1].")
    print("L'erreur volontaire est située sur la 4ème ligne (iban_origine: DE456, montant: 'INVALID_MONTANT').")

if __name__ == "__main__":
    generate_single_csv_with_error()