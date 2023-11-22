import csv
import re

# Funzione per rimuovere numeri, trattini e spazi dal terzo campo


# Nome del file di input e di output
input_file = '../Resources/stops.txt'
output_file = '../Resources/NewStop.csv'

# Colonne da eliminare
columns_to_remove = ["stop_timezone", "wheelchair_boarding", "stop_lat", "stop_lon", "zone_id", "parent_station",
                     "location_type", "stop_desc", "stop_url","stop_id"]

# Leggi il file di input e scrivi il file di output
with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Leggi l'intestazione e determina gli indici delle colonne da mantenere
    header = next(reader)
    keep_indices = [i for i, column in enumerate(header) if column not in columns_to_remove]

    # Aggiungi una colonna vuota per contenere il campo modificato
    new_header = header + ["new_field"]
    writer.writerow(new_header)

    # Scansiona il resto del file e scrivi solo le colonne mantenute
    for row in reader:
        new_row = [row[i] for i in keep_indices]

        # Rimuovi numeri, trattini e spazi dal terzo campo (assumendo che sia l'indice 2)
        new_row[1] = row[2].replace(f"Fermata {row[1]} - ", "")

        writer.writerow(new_row)

print("Colonne rimosse, numeri, trattini e spazi dal terzo campo rimossi con successo.")
