from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, ListItem, ListView
from pathlib import Path
import json



def kostenberekening():
        JSON_PATH = str(Path(__file__).with_suffix('.json'))

        try:
            with open(JSON_PATH, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            print("Het JSON-bestand bestaat niet.")
            return
        except json.JSONDecodeError:
            print("Het JSON-bestand is beschadigd of leeg.")
            return

        # Haal het aantal gasten op uit het JSON-bestand
        aantal_gasten = data.get('gasten', None)
        
        if aantal_gasten is None:
            print("De waarde van gasten is niet gevonden in het JSON-bestand.")
            return

        # Hier kun je berekeningen uitvoeren met het aantal gasten
        # Voorbeeld: bereken de totale kosten op basis van een prijs per gast
        prijs_per_gast = 50.0  # Dit is een voorbeeldprijs, pas deze aan naar je behoefte
        totale_kosten = aantal_gasten * prijs_per_gast
        print(f"Totale kosten voor {aantal_gasten} gasten: €{totale_kosten}")

        # Je kunt ervoor kiezen om deze waarde terug te geven
        return totale_kosten

print(kostenberekening())