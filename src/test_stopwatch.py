import json
from pathlib import Path

class JSONChecker:
    def check_for_Null(self) -> bool:
        JSON_PATH = str(Path(__file__).with_suffix('.json'))
        try:
            # Open het JSON-bestand
            with open(JSON_PATH, 'r') as file:
                data = json.load(file)
                for key, value in data.items():
                    if value is None:
                        return False
                return True

        except FileNotFoundError:
            print("Het JSON-bestand bestaat niet.")
            return False
        except json.JSONDecodeError:
            print("Het JSON-bestand is beschadigd of bevat geen geldige JSON.")
            return False

# Gebruik de klasse
checker = JSONChecker()
result = checker.check_for_Null()
print(result)
