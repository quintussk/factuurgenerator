from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal,Vertical, Grid, ScrollableContainer, VerticalScroll
from textual.widgets import Input, Button, Footer, Header, Static, Label, Checkbox, Switch, ListItem, ListView
from textual import on, events
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.screen import Screen
import json
from pathlib import Path
from textual.reactive import Reactive

QUESTION = "Wil je een begroting maken?"

VERZEKERINGEN = [
    ("verz1","Evenementenvergunning: ","Gemiddelde kosten: €300", 300),
    ("verz2","Veiligheidsplan: ","Gemiddelde kosten: €1250", 1250),
    ("verz3","Drank- en voedselvergunning: ","Gemiddelde kosten: €200", 200),
    ("verz4","Geluidsvergunning: ","Gemiddelde kosten: €175", 175),
    ("verz5","Muziekvergunning: ","Gemiddelde kosten: €125", 125),
    ("verz6","Keuring van de stellingen: ","Gemiddelde kosten: €200", 200),
    ("verz7","Aanpassing openbare orde: ","Gemiddelde kosten: €100", 100),
]

CATERING = [
    ("labelA", 150, "Label A Catering"),
    ("labelB", 100, "Label B Catering"),
    ("labelC", 50, "Label C Catering"),
]

SAMENVATTING =[
    ("gasten", "Totale aantal gasten: "),
    ("labelA", "Catering label A: "),
    ("labelB", "Catering label B:"),
    ("labelC", "Catering label C: "),
    ("Evenementenbenodigdheden", "Evenement benodigdheden:"),
    ("Evenementenvergunning: ","Evenementenvergunning: "),
    ("Veiligheidsplan: ","Veiligheidsplan: "),
    ("Drank- en voedselvergunning: ","Drank- en voedselvergunning: "),
    ("Geluidsvergunning: ","Geluidsvergunning: "),
    ("Muziekvergunning: ","Muziekvergunning: "),
    ("Keuring van de stellingen: ","Keuring van de stellingen: "),
    ("Aanpassing openbare orde: ","Aanpassing openbare orde: "),
    ("witregel","_____________________________"),
    ("totale kosten","Totale kosten: "),
]

class PeopleInput(Widget):
    value: reactive[float] = reactive(0.0)

    class SetpointChanged(Message):
        """Sent when the 'bit' changes."""

        def __init__(self, value: float) -> None:
            super().__init__()
            self.value = value

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Aantal gasten")

    def on_input_changed(self, event: Input.Changed) -> None:
        event.stop()
        try:
            self.value = float(event.value or "0")
        except ValueError:
            return

        # self.post_message(self.SetpointChanged(self.value))

    def key_enter(self, event: Input.Changed) -> None:
        event.stop()
        self.update_json("gasten", self.value)
        self.post_message(self.SetpointChanged(self.value))
        pakketkeuze = self.app.query_one("#pakket_keuze")
        if pakketkeuze:
            pakketkeuze.update_pakketkeuze()

        benodigheden = self.app.query_one("#benodigheden_id")
        if benodigheden:
            benodigheden.update_prijs()

    def update_json(self, vraag, score):
        JSON_PATH = str(Path(__file__).with_suffix('.json'))

        if not Path(JSON_PATH).exists():
            with open(JSON_PATH, 'w') as file:
                json.dump({}, file)
        
        with open(JSON_PATH, 'r+') as file:
            try:
                data = json.load(file)
                data[vraag] = score
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
            except json.JSONDecodeError:
                print("Failed to decode JSON, initializing new data.")
                data = {vraag: score}
                json.dump(data, file, indent=4)

class PeopleChoice(Static):
    def compose(self) -> ComposeResult:
        with Horizontal ():
            yield Label("Aantal gasten aanwezig:", classes="Labels")
            yield PeopleInput(classes="inputs")
        
class InsuraceExtra(Static):
    name: str
    vraag: str
    verzekering: str
    kosten: int
    switch_state: Reactive[bool] = Reactive(False)

    def compose(self) -> ComposeResult:
        for verz_nmmr, verz, uitleg, kost in VERZEKERINGEN:
            if verz_nmmr is self.name:
                self.vraag = verz + "(" + uitleg + ")"
                self.verzekering = verz
                self.kosten = kost
        with Grid(classes="insurancegrid"):
            yield Label(self.vraag, classes="labelGrid")
            yield Switch(id=self.name, classes="switches")

    @on(Switch.Changed)
    async def on_switch_changed(self, event: Switch.Changed) -> None:
        # if event.sender.id == self.name:  # Check if the event is from this particular switch
        self.switch_state = event.value
        if event.value:
            self.update_json(self.verzekering, self.kosten)
        else:
            self.remove_entry(self.verzekering)

    def update_json(self, vraag, score):
        JSON_PATH = str(Path(__file__).with_suffix('.json'))

        if not Path(JSON_PATH).exists():
            with open(JSON_PATH, 'w') as file:
                json.dump({}, file)
        
        with open(JSON_PATH, 'r+') as file:
            try:
                data = json.load(file)
                data[vraag] = score
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
            except json.JSONDecodeError:
                print("Failed to decode JSON, initializing new data.")
                data = {vraag: score}
                json.dump(data, file, indent=4)

    def remove_entry(self, vraag):
        JSON_PATH = str(Path(__file__).with_suffix('.json'))

        if not Path(JSON_PATH).exists():
            print("Het JSON-bestand bestaat niet.")
            return

        with open(JSON_PATH, 'r+') as file:
            data = json.load(file)
            if vraag in data:
                del data[vraag]
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
                print(f"{vraag} is verwijderd.")
            else:
                print(f"{vraag} is niet gevonden in het bestand.")

class Insurance(Static):
    def compose(self) -> ComposeResult:
        with Vertical():
            with Grid(id="heatzones"):
                yield Static("Vergunningen: ", classes="verzekering_titel")
                yield InsuraceExtra("Verzekering1", id="vrz1", name="verz1")
                yield InsuraceExtra("Verzekering2", id="vrz2", name="verz2")
                yield InsuraceExtra("Verzekering3", id="vrz3", name="verz3")
                yield InsuraceExtra("Verzekering4", id="vrz4", name="verz4")
                yield InsuraceExtra("Verzekering5", id="vrz5", name="verz5")
                yield InsuraceExtra("Verzekering6", id="vrz6", name="verz6")
                yield InsuraceExtra("Verzekering7", id="vrz7", name="verz7")

class PakketKeuze(Static):
    selected_label: Reactive[str] = Reactive("")
    id = "pakket_keuze"

    def compose(self) -> ComposeResult:
        with Horizontal ():
            yield Label("Catering Keuze:", classes="Labels")
            yield ListView(
                ListItem(Label("A label    (150€ pp)"),id= "labelA"), 
                ListItem(Label("B label    (100€ pp)"),id= "labelB"),
                ListItem(Label("C label     (50€ pp)"),id= "labelC"),
            classes = "pakket")

    @on(ListView.Highlighted)
    async def on_item_focus(self, event: ListView.Highlighted) -> None:
        self.selected_label = event.item.id
        self.update_pakketkeuze()
    
    def update_pakketkeuze(self):
        for label,_,beschrijving in CATERING:
            self.remove_entry(label)
        for label,prijs,beschrijving in CATERING:
            if label is self.selected_label:
                self.update_json(label, self.kostenberekening(prijs))

    async def perform_action_based_on_selection(self, focused_item_text):
        # Implementeer de actie die moet gebeuren wanneer een item focus krijgt
        print(f"Item gefocust: {focused_item_text}")

    def update_json(self, vraag, score):
        JSON_PATH = str(Path(__file__).with_suffix('.json'))

        if not Path(JSON_PATH).exists():
            with open(JSON_PATH, 'w') as file:
                json.dump({}, file)
        
        with open(JSON_PATH, 'r+') as file:
            try:
                data = json.load(file)
                data[vraag] = score
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
            except json.JSONDecodeError:
                print("Failed to decode JSON, initializing new data.")
                data = {vraag: score}
                json.dump(data, file, indent=4)

    def kostenberekening(self, prijs):
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
        prijs_per_gast = prijs  # Dit is een voorbeeldprijs, pas deze aan naar je behoefte
        totale_kosten = aantal_gasten * prijs_per_gast
        print(f"Totale kosten voor {aantal_gasten} gasten: €{totale_kosten}")

        # Je kunt ervoor kiezen om deze waarde terug te geven
        return totale_kosten
    
    def remove_entry(self, vraag):
        JSON_PATH = str(Path(__file__).with_suffix('.json'))

        if not Path(JSON_PATH).exists():
            print("Het JSON-bestand bestaat niet.")
            return

        with open(JSON_PATH, 'r+') as file:
            data = json.load(file)
            if vraag in data:
                del data[vraag]
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
                print(f"{vraag} is verwijderd.")
            else:
                print(f"{vraag} is niet gevonden in het bestand.")



class Benodigdheden(Static):
    selected_Benodigheden: Reactive[bool] = Reactive(False)
    id = "benodigheden_id"
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label("Evenementenbenodigdheden (Stoelen, tafels, tenten en overige benodigdheden) voor 8€ pp: ", classes="Labels")
            yield Switch(id=self.name, classes="switches")

    @on(Switch.Changed)
    async def on_switch_changed(self, event: Switch.Changed) -> None:
        # if event.sender.id == self.name:  # Check if the event is from this particular switch
        self.switch_state = event.value
        self.selected_Benodigheden = event.value
        self.update_prijs()

    def update_prijs(self):
        if self.selected_Benodigheden:
            self.update_json("Evenementenbenodigdheden", self.kostenberekening())
        else:
            self.remove_entry("Evenementenbenodigdheden")

    def kostenberekening(self):
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
        prijs_per_gast = 8.0  # Dit is een voorbeeldprijs, pas deze aan naar je behoefte
        totale_kosten = aantal_gasten * prijs_per_gast
        print(f"Totale kosten voor {aantal_gasten} gasten: €{totale_kosten}")

        # Je kunt ervoor kiezen om deze waarde terug te geven
        return totale_kosten


    def update_json(self, vraag, score):
        JSON_PATH = str(Path(__file__).with_suffix('.json'))

        if not Path(JSON_PATH).exists():
            with open(JSON_PATH, 'w') as file:
                json.dump({}, file)
        
        with open(JSON_PATH, 'r+') as file:
            try:
                data = json.load(file)
                data[vraag] = score
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
            except json.JSONDecodeError:
                print("Failed to decode JSON, initializing new data.")
                data = {vraag: score}
                json.dump(data, file, indent=4)

    def remove_entry(self, vraag):
        JSON_PATH = str(Path(__file__).with_suffix('.json'))

        if not Path(JSON_PATH).exists():
            print("Het JSON-bestand bestaat niet.")
            return

        with open(JSON_PATH, 'r+') as file:
            data = json.load(file)
            if vraag in data:
                del data[vraag]
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
                print(f"{vraag} is verwijderd.")
            else:
                print(f"{vraag} is niet gevonden in het bestand.")

class Switchscreen(Static):
    """A stopwatch widget."""
    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Terug", id="terug", variant="error")
        yield Button("Volgende", id="volgende", variant="success")

class Switchscreen2(Static):
    """A stopwatch widget."""
    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Terug", id="terug", variant="error")
        yield Button("Indienen", id="indienen", variant="success")

class Factuur(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ScrollableContainer( Samenvatting(),Switchscreen2())

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "terug":
            self.app.pop_screen()
        elif event.button.id == "indienen":
            print("hier nog wat voor het indienen")
            # self.update_total_costs()

class Started(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ScrollableContainer( PeopleChoice(),PakketKeuze(), Benodigdheden(),Switchscreen(), Insurance())

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "terug":
            self.app.pop_screen()
        elif event.button.id == "volgende":
            if self.check_for_Null():
                self.update_total_costs()
                self.app.push_screen(Factuur())

    def watch_dark(self, dark: bool) -> None:
        self.query("Button").set_appearance("error" if dark else "primary")
    
    def on_load(self) -> None:
        """Load the app.""" 
        self.bind("q", "quit", description="Quit")
        self.bind("d", "toggle_dark", description="Toggle mode")

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

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
        
    def update_total_costs(self):
        JSON_PATH = str(Path(__file__).with_suffix('.json'))

        try:
            # Open het JSON-bestand
            with open(JSON_PATH, 'r+') as file:
                data = json.load(file)

                # Bereken de totale kosten
                total_costs = sum(value for key, value in data.items()
                              if key not in ["gasten", "totale kosten"] and isinstance(value, (int, float)))

                # Update de totale kosten in het JSON-bestand
                data["totale kosten"] = total_costs

                # Schrijf de bijgewerkte data terug naar het bestand
                file.seek(0)  # Ga terug naar het begin van het bestand
                json.dump(data, file, indent=4)
                file.truncate()  # Verwijder alles na de nieuwe data
                
                print(f"Totale kosten zijn bijgewerkt naar: {total_costs}")

        except FileNotFoundError:
            print("Het JSON-bestand bestaat niet.")
        except json.JSONDecodeError:
            print("Het JSON-bestand is beschadigd of bevat geen geldige JSON.")

class Samenvatting(Static):
    def compose(self) -> ComposeResult:
        JSON_PATH = str(Path(__file__).with_suffix('.json'))
        yield Static("Samenvatting Kosten: ", classes="verzekering_titel")

        try:
            # Open het JSON-bestand
            with open(JSON_PATH, 'r+') as file:
                data = json.load(file)
                for f,tekst in SAMENVATTING:
                    if f == "witregel":
                            with Grid(classes="samenvattinggrid"):
                                yield Static(tekst, classes = "samenvatting_key")
                                yield Static("__________", classes = "samenvatting_key")
                    else:
                        for key,value in data.items():
                            if f == key:
                                with Grid(classes="samenvattinggrid"):
                                    if key != "gasten":
                                        formatted_value = f"€{value:,.2f}"
                                    else:
                                        formatted_value = f"{value:.0f}"
                                    yield Static(tekst, classes = "samenvatting_key")
                                    yield Static(formatted_value, classes = "samenvatting_value")
                                    # yield Static(formatted_value, classes = "samenvatting_value")
        except FileNotFoundError:
            print("Het JSON-bestand bestaat niet.")
        except json.JSONDecodeError:
            print("Het JSON-bestand is beschadigd of bevat geen geldige JSON.")
class YEBU(App):
    id = "YEBU"
    CSS_PATH = str(Path(__file__).with_suffix('.tcss'))

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Vertical(
                Static(QUESTION, classes="question"),
                Button("Start", variant="success", id="start", classes="button_start")
            ),
            id="start_screen",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start":
            # self.push_screen(AantalMensen())
            self.resetJson()
            self.push_screen(Started())
            
    def resetJson(self):
        JSON_PATH = str(Path(__file__).with_suffix('.json'))
        if not Path(JSON_PATH).exists():
            print("Het JSON-bestand bestaat niet.")
            return
        with open(JSON_PATH, 'w') as file:
            json.dump({}, file) 

    def on_load(self) -> None:
        """Load the app.""" 
        self.bind("q", "quit", description="Quit")
        self.bind("d", "toggle_dark", description="Toggle mode")

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

def main():
    app = YEBU()
    app.run()

if __name__ == "__main__":
    main()