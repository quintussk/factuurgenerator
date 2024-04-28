from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal,Vertical, Grid, ScrollableContainer, VerticalScroll
from textual.widgets import Input, Button, Footer, Header, Static, Label, Checkbox, Switch, ListItem, ListView
from textual import on
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.screen import Screen
import json
from pathlib import Path
from textual.reactive import Reactive

QUESTION = "Wil je starten?"

VERZEKERINGEN = [
    ("verz1","Evenementenvergunning: ","Gemiddelde kosten: €300", 300),
    ("verz2","Veiligheidsplan: ","Gemiddelde kosten: €1250", 1250),
    ("verz3","Drank- en voedselvergunning: ","Gemiddelde kosten: €200", 200),
    ("verz4","Geluidsvergunning: ","Gemiddelde kosten: €175", 175),
    ("verz5","Muziekvergunning: ","Gemiddelde kosten: €125", 125),
    ("verz6","Keuring van de stellingen: ","Gemiddelde kosten: €200", 200),
    ("verz7","Aanpassing openbare orde: ","Gemiddelde kosten: €100", 100),
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
                yield Static("Verzekeringen: ", classes="verzekering_titel")
                yield InsuraceExtra("Verzekering1", id="vrz1", name="verz1")
                yield InsuraceExtra("Verzekering2", id="vrz2", name="verz2")
                yield InsuraceExtra("Verzekering3", id="vrz3", name="verz3")
                yield InsuraceExtra("Verzekering4", id="vrz4", name="verz4")
                yield InsuraceExtra("Verzekering5", id="vrz5", name="verz5")
                yield InsuraceExtra("Verzekering6", id="vrz6", name="verz6")
                yield InsuraceExtra("Verzekering7", id="vrz7", name="verz7")

class PakketKeuze(Static):
    def compose(self) -> ComposeResult:
        with Horizontal ():
            yield Label("Catering Keuze:", classes="Labels")
            yield ListView(
                ListItem(Label("A label    (150€ pp)")),
                ListItem(Label("B label    (100€ pp)")),
                ListItem(Label("C label     (50€ pp)")),
            classes = "pakket")

    

    

class Benodigdheden(Static):
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label("Evenementenbenodigdheden (Stoelen, tafels, tenten en overige benodigdheden) voor 8€ pp: ", classes="Labels")
            yield Switch(id=self.name, classes="switches")

    @on(Switch.Changed)
    async def on_switch_changed(self, event: Switch.Changed) -> None:
        # if event.sender.id == self.name:  # Check if the event is from this particular switch
        self.switch_state = event.value
        if event.value:
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

class Started(Screen):
    def compose(self) -> ComposeResult:
        yield ScrollableContainer( PeopleChoice(),PakketKeuze(), Benodigdheden(),Switchscreen(), Insurance())

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "terug":
            self.app.pop_screen()
        elif event.button.id == "volgende":
            print("Moving to next part...")

    def watch_dark(self, dark: bool) -> None:
        self.query("Button").set_appearance("error" if dark else "primary")


class YEBU(App):
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

if __name__ == "__main__":
    app = YEBU()
    app.run()