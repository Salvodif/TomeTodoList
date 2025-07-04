# Book Tracker

A simple application to track your book reading progress.

This project uses a CSV file to store book data. The initial project was developed using a `goodreads_library_export.csv` file, which can be typically downloaded from [Goodreads](https://www.goodreads.com/).

However, you can start with any CSV file, even an empty one. The application will create or adapt the CSV file as needed to store your book information.

## Features

- Import books from a CSV file (e.g., Goodreads export).
- View your book library in a sortable, interactive table.
- Add new books with comprehensive details (title, author, rating, ISBN, review, reading status, etc.).
- Edit existing book information.
- Delete books from your library.
- Books marked as "currently-reading" are prioritized at the top of the list.
- All data is saved locally to `my_library.csv`.
- User-friendly terminal interface powered by Textual.

## Installation

1.  **Python**: Requires Python 3.7+ (Textual recommendation).
2.  **Install Textual**:
    ```bash
    pip install textual
    ```
    (If you have a `requirements.txt` file, you can use `pip install -r requirements.txt` instead).

## Usage

1.  Run the application from your terminal:
    ```bash
    python main.py
    ```
2.  **First Run**:
    - If `my_library.csv` is not found in the same directory as `main.py`, the application will prompt you to enter the path to your existing CSV file (e.g., `goodreads_library_export.csv`).
    - If you don't have an existing CSV, you can point it to a non-existent file name (e.g., `my_books.csv`) or an empty CSV, and the application will create it for you.
3.  **Subsequent Runs**: The application will automatically load data from `my_library.csv`.

**Keyboard Shortcuts:**
- `a`: Add a new book
- `e`: Edit the selected book
- `d`: Delete the selected book
- `q`: Quit the application (and save changes)

## Contributing

(To be filled in - e.g., Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.)

## License

[MIT](LICENSE)
