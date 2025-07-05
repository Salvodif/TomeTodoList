import csv
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
)

# --- Struttura Dati ---

@dataclass
class Book:
    book_id: int
    title: str
    author: str
    exclusive_shelf: str
    my_rating: int = 0
    publisher: str = ""
    year_published: int = 0
    date_read: str = ""
    date_added: str = ""
    bookshelves: str = ""
    my_review: str = ""
    isbn13: str = "0000000000000"
    is_reading: bool = field(init=False, repr=False)

    def __post_init__(self):
        self.is_reading = self.exclusive_shelf == "currently-reading"

# --- Logica di Gestione Dati ---

DB_CSV = "my_library.csv"

def clean_isbn(isbn: str) -> str:
    cleaned = isbn.strip('="')
    return cleaned if cleaned.isdigit() and len(cleaned) == 13 else "0000000000000"

def rating_to_stars(rating: int) -> str:
    if not isinstance(rating, int) or not (0 <= rating <= 5):
        return "☆☆☆☆☆"
    return "★" * rating + "☆" * (5 - rating)

def load_books_from_csv(filename: str, is_initial_import: bool = False) -> List[Book]:
    books = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if is_initial_import:
                reader.fieldnames = [name.lower().replace(' ', '_').replace('-', '_') for name in reader.fieldnames]

            for row in reader:
                try:
                    book_id_str = row.get("book_id") or row.get("book_id")
                    if not book_id_str: continue

                    book_id = int(book_id_str)
                    if any(b.book_id == book_id for b in books):
                        continue
                        
                    books.append(
                        Book(
                            book_id=book_id,
                            title=row.get("title", "N/A"),
                            author=row.get("author", "N/A"),
                            isbn13=clean_isbn(row.get("isbn13", "")),
                            my_rating=int(float(row.get("my_rating", 0))),
                            publisher=row.get("publisher", ""),
                            year_published=int(float(row.get("year_published", 0))) if row.get("year_published") else 0,
                            date_read=row.get("date_read", ""),
                            date_added=row.get("date_added", ""),
                            bookshelves=row.get("bookshelves", ""),
                            my_review=row.get("my_review", "").replace('<br/>', '\n'),
                            exclusive_shelf=row.get("exclusive_shelf", "to-read"),
                        )
                    )
                except (ValueError, TypeError):
                    continue
    except FileNotFoundError:
        return []
    return books

def save_books_to_csv(filename: str, books: List[Book]):
    if not books: return
    fieldnames = [f.name for f in Book.__dataclass_fields__.values() if f.name != 'is_reading']
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for book in books:
            book_dict = asdict(book)
            book_dict.pop('is_reading', None)
            writer.writerow(book_dict)

# --- Schermate Modali ---

class InitialSetupScreen(ModalScreen[Optional[str]]):
    def compose(self) -> ComposeResult:
        with Vertical(id="initial-setup-dialog"):
            yield Static("Benvenuto in TomeTodoList!", id="welcome-title")
            yield Static("Il file della libreria (my_library.csv) non è stato trovato.\n\nIndica il percorso del file CSV da importare per iniziare.", id="instructions")
            yield Input(value="goodreads_library_export.csv", id="csv_path_input")
            yield Button("Inizia Importazione", variant="primary", id="import")
            yield Button("Esci", variant="error", id="quit_app")
    
    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "quit_app":
            self.app.exit()
        elif event.button.id == "import":
            path = self.query_one("#csv_path_input", Input).value
            if not os.path.exists(path):
                self.app.notify(f"File non trovato: '{path}'", title="Errore", severity="error")
            else:
                self.dismiss(path)

class BookFormScreen(ModalScreen[Optional[Book]]):
    def __init__(self, book: Optional[Book] = None):
        super().__init__()
        self.book_to_edit = book
        self.title_text = "Modifica Libro" if book else "Aggiungi Nuovo Libro"

    def compose(self) -> ComposeResult:
        with Grid(id="book-form"):
            yield Label(self.title_text, id="form-title")
            yield Label("Titolo [red]*[/]")
            yield Input(value=self.book_to_edit.title if self.book_to_edit else "", id="title")
            yield Label("Autore [red]*[/]")
            yield Input(value=self.book_to_edit.author if self.book_to_edit else "", id="author")
            yield Label("Stato [red]*[/]")
            shelf_options = [("In Lettura", "currently-reading"), ("Letto", "read"), ("Da Leggere", "to-read")]
            yield Select(options=shelf_options, value=self.book_to_edit.exclusive_shelf if self.book_to_edit else "to-read", id="exclusive_shelf")
            yield Label("Rating (0-5)")
            yield Input(value=str(self.book_to_edit.my_rating) if self.book_to_edit else "0", id="my_rating", type="integer")
            yield Label("Editore")
            yield Input(value=self.book_to_edit.publisher if self.book_to_edit else "", id="publisher")
            yield Label("Anno Pubblicazione")
            yield Input(value=str(self.book_to_edit.year_published) if self.book_to_edit else "", id="year_published", type="integer")
            yield Label("Data Lettura (YYYY/MM/DD)")
            yield Input(value=self.book_to_edit.date_read if self.book_to_edit else "", id="date_read")
            yield Label("ISBN13")
            yield Input(value=self.book_to_edit.isbn13 if self.book_to_edit else "", id="isbn13")
            yield Label("Tags (separati da virgola)")
            yield Input(value=self.book_to_edit.bookshelves if self.book_to_edit else "", id="bookshelves")
            yield Label("Recensione")
            yield Input(value=self.book_to_edit.my_review if self.book_to_edit else "", id="my_review", multiline=True)
            yield Button("Salva", variant="primary", id="save")
            yield Button("Annulla", variant="default", id="cancel")
    
    @on(Button.Pressed)
    def handle_button_press(self, event: Button.Pressed):
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            title = self.query_one("#title", Input).value
            author = self.query_one("#author", Input).value
            if not title or not author:
                self.app.notify("Titolo e Autore sono campi obbligatori.", title="Errore", severity="error")
                return
            
            try:
                rating = int(self.query_one("#my_rating", Input).value or 0)
                if not (0 <= rating <= 5):
                    self.app.notify("Il rating deve essere tra 0 e 5.", title="Errore", severity="error")
                    return
                year = int(self.query_one("#year_published", Input).value or 0)
            except ValueError:
                self.app.notify("Rating e Anno devono essere numeri.", title="Errore", severity="error")
                return

            book_id = self.book_to_edit.book_id if self.book_to_edit else self.app.get_next_book_id()
            date_added = self.book_to_edit.date_added if self.book_to_edit else datetime.now().strftime("%Y/%m/%d")

            new_book = Book(
                book_id=book_id, title=title, author=author,
                exclusive_shelf=self.query_one("#exclusive_shelf", Select).value,
                my_rating=rating, publisher=self.query_one("#publisher", Input).value,
                year_published=year, date_read=self.query_one("#date_read", Input).value,
                date_added=date_added, isbn13=self.query_one("#isbn13", Input).value or "0000000000000",
                bookshelves=self.query_one("#bookshelves", Input).value,
                my_review=self.query_one("#my_review", Input).value
            )
            self.dismiss(new_book)

class ConfirmDeleteScreen(ModalScreen[bool]):
    def __init__(self, book_title: str):
        super().__init__()
        self.book_title = book_title

    def compose(self) -> ComposeResult:
        with Grid(id="confirm-delete-dialog"):
            yield Static(f"Sei sicuro di voler cancellare:\n\n[b]{self.book_title}[/b]?", id="question")
            yield Button("Cancella", variant="error", id="delete")
            yield Button("Annulla", variant="primary", id="cancel")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss(event.button.id == "delete")

class SearchScreen(ModalScreen[Optional[str]]):
    def __init__(self, initial_value: str = ""):
        super().__init__()
        self.initial_value = initial_value

    def compose(self) -> ComposeResult:
        with Vertical(id="search-dialog"):
            yield Static("Cerca Libri", id="search-title")
            yield Input(value=self.initial_value, placeholder="Titolo o autore...", id="search-modal-input")
            with Grid(id="search-buttons"): # Rimosso columns=2
                yield Button("Cerca", variant="primary", id="search-confirm")
                yield Button("Annulla", variant="default", id="search-cancel")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "search-cancel":
            self.dismiss(None)
        elif event.button.id == "search-confirm":
            search_term = self.query_one("#search-modal-input", Input).value
            self.dismiss(search_term)

    @on(Input.Submitted, "#search-modal-input")
    def on_input_submitted(self, event: Input.Submitted):
        self.dismiss(event.value)

# --- App Principale ---

class BookTrackerApp(App): # Keeping class name for now to avoid larger refactor
    CSS_PATH = "tometodolist.tcss"
    BINDINGS = [
        Binding("q", "quit", "Esci"), Binding("a", "add_book", "Aggiungi"),
        Binding("e", "edit_book", "Modifica"), Binding("d", "delete_book", "Cancella"),
    ]

    def __init__(self):
        super().__init__()
        self.books: List[Book] = []
        self.table = DataTable(id="book-table")
        self.columns = [
            ("Autore", "author"), ("Titolo", "title"), ("Rating", "my_rating"),
            ("Editore", "publisher"), ("Anno", "year_published"), ("Letto il", "date_read"),
            ("Aggiunto il", "date_added"), ("Tags", "bookshelves"), ("ISBN13", "isbn13"),
            ("Recensione", "my_review")
        ]
        self.sort_by = "author"
        self.sort_reverse = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with VerticalScroll():
            yield self.table
        yield Footer()

    def on_mount(self) -> None:
        self.title = "TomeTodoList"
        self.table.cursor_type = "row"
        self.table.add_columns(*[col[0] for col in self.columns])
        
        # --- LOGICA DI AVVIO ---
        # Controlla se il nostro database 'my_library.csv' esiste.
        if not os.path.exists(DB_CSV):
            # 1. SE NON ESISTE (PRIMO AVVIO):
            #    Mostra la schermata per l'importazione iniziale.
            def setup_callback(path: Optional[str]):
                if path:
                    self.load_and_display_books(path, is_initial_import=True)
            self.push_screen(InitialSetupScreen(), setup_callback)
        else:
            # 2. SE ESISTE GIÀ (AVVII SUCCESSIVI):
            #    Carica direttamente dal nostro database e salta l'importazione.
            self.load_and_display_books(DB_CSV)

    def load_and_display_books(self, path: str, is_initial_import: bool = False):
        self.books = load_books_from_csv(path, is_initial_import)
        if is_initial_import and self.books:
            self.notify(f"Importati {len(self.books)} libri da '{os.path.basename(path)}'.")
        self.refresh_table()

    def get_next_book_id(self) -> int:
        if not self.books: return 1
        return max(int(book.book_id) for book in self.books) + 1

    def refresh_table(self):
        self.table.clear()
        
        sort_attr = self.sort_by
        sort_reverse = self.sort_reverse
        
        key_func = lambda x: str(getattr(x, sort_attr) or "")
        
        reading_books = sorted([b for b in self.books if b.is_reading], key=key_func, reverse=sort_reverse)
        other_books = sorted([b for b in self.books if not b.is_reading], key=key_func, reverse=sort_reverse)
        
        sorted_books = reading_books + other_books

        for book in sorted_books:
            # Aggiunge una riga alla volta. L'ordine dei valori deve corrispondere
            # all'ordine definito in self.columns
            self.table.add_row(
                book.author, 
                book.title, 
                rating_to_stars(book.my_rating),
                book.publisher, 
                str(book.year_published) if book.year_published else "",
                book.date_read, 
                book.date_added, 
                book.bookshelves, 
                book.isbn13, 
                book.my_review,
                key=str(book.book_id)
            )

    @on(DataTable.HeaderSelected)
    def on_header_selected(self, event: DataTable.HeaderSelected):
        new_sort_by = self.columns[0][1] # Default
        for label, attr in self.columns:
            if str(event.column.label) == label:
                new_sort_by = attr
                break
        
        if self.sort_by == new_sort_by:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_by = new_sort_by
            self.sort_reverse = False
        
        self.refresh_table()

    def action_add_book(self):
        def on_dismiss(new_book: Optional[Book]):
            if new_book:
                self.books.append(new_book)
                self.refresh_table()
                self.notify(f"Libro '{new_book.title}' aggiunto.", title="Successo")
        self.push_screen(BookFormScreen(), on_dismiss)

    def action_edit_book(self):
        if self.table.cursor_row < 0:
            self.notify("Seleziona un libro da modificare.", title="Attenzione", severity="warning")
            return
        
        book_id = int(self.table.get_row_key(self.table.cursor_row))
        book_to_edit = next((b for b in self.books if b.book_id == book_id), None)
        if not book_to_edit: return

        def on_dismiss(updated_book: Optional[Book]):
            if updated_book:
                for i, book in enumerate(self.books):
                    if book.book_id == updated_book.book_id:
                        self.books[i] = updated_book
                        break
                self.refresh_table()
                self.notify(f"Libro '{updated_book.title}' modificato.", title="Successo")
        self.push_screen(BookFormScreen(book=book_to_edit), on_dismiss)
    
    def action_delete_book(self):
        if self.table.cursor_row < 0:
            self.notify("Seleziona un libro da cancellare.", title="Attenzione", severity="warning")
            return
            
        book_id = int(self.table.get_row_key(self.table.cursor_row))
        book_to_delete = next((b for b in self.books if b.book_id == book_id), None)
        if not book_to_delete: return

        def on_dismiss(should_delete: bool):
            if should_delete:
                self.books = [b for b in self.books if b.book_id != book_to_delete.book_id]
                self.refresh_table()
                self.notify(f"Libro '{book_to_delete.title}' cancellato.", title="Successo")
        self.push_screen(ConfirmDeleteScreen(book_title=book_to_delete.title), on_dismiss)
    
    def action_quit(self):
        save_books_to_csv(DB_CSV, self.books)
        self.exit()

if __name__ == "__main__":
    css_content = """
    TomeTodoListApp { background: $surface; }
    #book-table { height: 100%; }
    #book-form, #confirm-delete-dialog, #initial-setup-dialog {
        padding: 0 1; width: 80; border: thick $primary; background: $surface;
    }
    #book-form, #confirm-delete-dialog {
        grid-size: 2; grid-gutter: 1 2; height: auto;
    }
    #initial-setup-dialog { align: center middle; height: 15; }
    #welcome-title { width: 100%; text-align: center; padding-top: 1; text-style: bold; }
    #instructions { width: 100%; text-align: center; margin: 1 0; }
    #form-title, #question {
        column-span: 2; width: 100%; text-align: center; padding: 1; background: $primary; color: $text;
    }
    #question { height: auto; }
    #confirm-delete-dialog { width: 60; }
    Input, Select { width: 100%; }
    #my_review { height: 5; }
    Button { margin-top: 1; width: 100%; }

    /* Stili per SearchScreen */
    #search-dialog {
        padding: 1 2; /* Aggiunto padding interno */
        width: 70; /* Larghezza leggermente aumentata */
        border: thick $primary;
        background: $surface;
        height: auto;
        /* Non serve align: center middle; per il Vertical, gestisce i figli */
    }
    #search-title { /* Già presente in BookForm, ma può essere specifico se necessario */
        column-span: 2; /* Utile se search-dialog fosse un Grid, ma è Vertical */
        width: 100%;
        text-align: center;
        padding-bottom: 1; /* Spazio sotto il titolo */
        text-style: bold;
        /* background: $primary; /* Rimosso per uniformità o se si preferisce senza */
        /* color: $text; */
    }
    #search-modal-input {
        margin-bottom: 1; /* Spazio prima dei bottoni */
    }
    #search-buttons {
        grid-size: 2; /* Definisce 2 colonne per la griglia dei bottoni */
        grid-gutter: 1 2; /* Spaziatura orizzontale e verticale tra i bottoni */
        /* width: 100%; Non necessario se i bottoni stessi hanno width 100% e il Grid si adatta */
    }
    """
    with open("tometodolist.tcss", "w") as css_file:
        css_file.write(css_content)

    app = BookTrackerApp() # Class name remains BookTrackerApp, as renaming it is a larger refactor
    app.run()