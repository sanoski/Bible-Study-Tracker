import os
import sqlite3
import datetime
import math
import time
from typing import Tuple, List, Dict
import requests
from bs4 import BeautifulSoup
import bible_scraper_v2 as scraper
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import BarColumn, Progress
from rich import box
import json

# Initialize rich console for pretty display
console = Console()

# Database path - store in the same directory as the program
DB_PATH = "bible_tracker.db"

# Check if old database exists in home directory and migrate it
OLD_DB_PATH = os.path.expanduser("~/.bible_tracker.db")
def migrate_database():
    """Migrate database from home directory to local directory if needed."""
    global DB_PATH
    if os.path.exists(OLD_DB_PATH) and not os.path.exists(DB_PATH):
        import shutil
        console.print("[bold yellow]Migrating database from home directory to local directory...[/bold yellow]")
        try:
            shutil.copy2(OLD_DB_PATH, DB_PATH)
            console.print("[bold green]✓ Database migrated successfully![/bold green]")
            console.print("[cyan]You can delete the old database at ~/.bible_tracker.db if everything works correctly.[/cyan]")
        except Exception as e:
            console.print(f"[bold red]Error migrating database: {e}[/bold red]")
            console.print("[bold red]Continuing with existing database in home directory.[/bold red]")
            DB_PATH = OLD_DB_PATH

# Bible structure data with number of chapters per book
BIBLE_BOOKS = [
    {"id": 1, "name": "Genesis", "chapters": 50},
    {"id": 2, "name": "Exodus", "chapters": 40},
    {"id": 3, "name": "Leviticus", "chapters": 27},
    {"id": 4, "name": "Numbers", "chapters": 36},
    {"id": 5, "name": "Deuteronomy", "chapters": 34},
    {"id": 6, "name": "Joshua", "chapters": 24},
    {"id": 7, "name": "Judges", "chapters": 21},
    {"id": 8, "name": "Ruth", "chapters": 4},
    {"id": 9, "name": "1 Samuel", "chapters": 31},
    {"id": 10, "name": "2 Samuel", "chapters": 24},
    {"id": 11, "name": "1 Kings", "chapters": 22},
    {"id": 12, "name": "2 Kings", "chapters": 25},
    {"id": 13, "name": "1 Chronicles", "chapters": 29},
    {"id": 14, "name": "2 Chronicles", "chapters": 36},
    {"id": 15, "name": "Ezra", "chapters": 10},
    {"id": 16, "name": "Nehemiah", "chapters": 13},
    {"id": 17, "name": "Esther", "chapters": 10},
    {"id": 18, "name": "Job", "chapters": 42},
    {"id": 19, "name": "Psalms", "chapters": 150},
    {"id": 20, "name": "Proverbs", "chapters": 31},
    {"id": 21, "name": "Ecclesiastes", "chapters": 12},
    {"id": 22, "name": "Song of Solomon", "chapters": 8},
    {"id": 23, "name": "Isaiah", "chapters": 66},
    {"id": 24, "name": "Jeremiah", "chapters": 52},
    {"id": 25, "name": "Lamentations", "chapters": 5},
    {"id": 26, "name": "Ezekiel", "chapters": 48},
    {"id": 27, "name": "Daniel", "chapters": 12},
    {"id": 28, "name": "Hosea", "chapters": 14},
    {"id": 29, "name": "Joel", "chapters": 3},
    {"id": 30, "name": "Amos", "chapters": 9},
    {"id": 31, "name": "Obadiah", "chapters": 1},
    {"id": 32, "name": "Jonah", "chapters": 4},
    {"id": 33, "name": "Micah", "chapters": 7},
    {"id": 34, "name": "Nahum", "chapters": 3},
    {"id": 35, "name": "Habakkuk", "chapters": 3},
    {"id": 36, "name": "Zephaniah", "chapters": 3},
    {"id": 37, "name": "Haggai", "chapters": 2},
    {"id": 38, "name": "Zechariah", "chapters": 14},
    {"id": 39, "name": "Malachi", "chapters": 4},
    {"id": 40, "name": "Matthew", "chapters": 28},
    {"id": 41, "name": "Mark", "chapters": 16},
    {"id": 42, "name": "Luke", "chapters": 24},
    {"id": 43, "name": "John", "chapters": 21},
    {"id": 44, "name": "Acts", "chapters": 28},
    {"id": 45, "name": "Romans", "chapters": 16},
    {"id": 46, "name": "1 Corinthians", "chapters": 16},
    {"id": 47, "name": "2 Corinthians", "chapters": 13},
    {"id": 48, "name": "Galatians", "chapters": 6},
    {"id": 49, "name": "Ephesians", "chapters": 6},
    {"id": 50, "name": "Philippians", "chapters": 4},
    {"id": 51, "name": "Colossians", "chapters": 4},
    {"id": 52, "name": "1 Thessalonians", "chapters": 5},
    {"id": 53, "name": "2 Thessalonians", "chapters": 3},
    {"id": 54, "name": "1 Timothy", "chapters": 6},
    {"id": 55, "name": "2 Timothy", "chapters": 4},
    {"id": 56, "name": "Titus", "chapters": 3},
    {"id": 57, "name": "Philemon", "chapters": 1},
    {"id": 58, "name": "Hebrews", "chapters": 13},
    {"id": 59, "name": "James", "chapters": 5},
    {"id": 60, "name": "1 Peter", "chapters": 5},
    {"id": 61, "name": "2 Peter", "chapters": 3},
    {"id": 62, "name": "1 John", "chapters": 5},
    {"id": 63, "name": "2 John", "chapters": 1},
    {"id": 64, "name": "3 John", "chapters": 1},
    {"id": 65, "name": "Jude", "chapters": 1},
    {"id": 66, "name": "Revelation", "chapters": 22}
]

def get_verse_count(book: str, chapter: int) -> int:
    """Get the number of verses in a chapter by scraping JW.org."""
    formatted_book = book.lower().replace(' ', '-')
    if formatted_book[0].isdigit():
        formatted_book = formatted_book.replace(' ', '-', 1)
    
    url = f"https://www.jw.org/en/library/bible/nwt/books/{formatted_book}/{chapter}/"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            console.print(f"[yellow]Warning: Couldn't fetch verse count. Using default.[/yellow]")
            return 30  # Default fallback
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all verse elements
        verse_elements = soup.find_all("span", class_="verse")
        if not verse_elements:
            return 30  # Default fallback
        
        # Get the highest verse number
        highest_verse = 0
        for element in verse_elements:
            verse_num_elem = element.find("sup", class_="verseNum")
            if verse_num_elem:
                try:
                    verse_num = int(verse_num_elem.text.strip())
                    if verse_num > highest_verse:
                        highest_verse = verse_num
                except ValueError:
                    pass
        
        return highest_verse if highest_verse > 0 else 30
    except Exception as e:
        console.print(f"[yellow]Error getting verse count: {e}. Using default.[/yellow]")
        return 30  # Default fallback

# 2. Fix to suppress debug output from the bible_scraper
def get_verse_text(book: str, chapter: int, verse: int) -> str:
    """Get the text of a specific verse using the bible_scraper."""
    try:
        # Redirect console output and stderr temporarily to capture/suppress the scraper's output
        import io
        import sys
        
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()  # Also capture stderr to suppress all output
        
        # Call the scraper function
        scraper.get_scripture(book.lower(), chapter, verse)
        
        # Get the captured output
        output = sys.stdout.getvalue()
        
        # Restore original stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        
        # Extract just the verse text (remove book, chapter:verse prefix and debug output)
        lines = output.strip().split('\n')
        # Filter out debug lines
        verse_lines = [line for line in lines if not line.startswith("DEBUG:")]
        
        if verse_lines and " - " in verse_lines[-1]:
            return verse_lines[-1].split(" - ", 1)[1].strip()
        elif verse_lines:
            return verse_lines[-1].strip()
        return "Verse text not available."
    
    except Exception as e:
        console.print(f"[red]Error retrieving verse: {e}[/red]")
        return "Verse text not available."

def init_db():
    """Initialize the database with Bible structure."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        total_chapters INTEGER NOT NULL,
        book_order INTEGER NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY,
        book_id INTEGER NOT NULL,
        chapter_number INTEGER NOT NULL,
        total_verses INTEGER NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reading_progress (
        id INTEGER PRIMARY KEY,
        book_id INTEGER NOT NULL,
        chapter_number INTEGER NOT NULL,
        verse_number INTEGER NOT NULL,
        timestamp DATETIME NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reading_history (
        id INTEGER PRIMARY KEY,
        book_id INTEGER NOT NULL,
        chapter_number INTEGER NOT NULL,
        verse_number INTEGER NOT NULL,
        date_read DATETIME NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books (id)
    )
    ''')
    
    # Add verses table for downloaded text
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS verses (
        id INTEGER PRIMARY KEY,
        book_id INTEGER NOT NULL,
        chapter_number INTEGER NOT NULL,
        verse_number INTEGER NOT NULL,
        verse_text TEXT NOT NULL,
        FOREIGN KEY (book_id) REFERENCES books (id),
        UNIQUE(book_id, chapter_number, verse_number)
    )
    ''')
    
    # Check if books table is already populated
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        console.print("[bold cyan]Initializing Bible database...[/bold cyan]")
        
        # Populate books table
        for book in BIBLE_BOOKS:
            cursor.execute(
                "INSERT INTO books (id, name, total_chapters, book_order) VALUES (?, ?, ?, ?)",
                (book["id"], book["name"], book["chapters"], book["id"])
            )
        
        console.print("[cyan]Populating chapter data (this may take a moment)...[/cyan]")
        # Create progress bar
        with Progress() as progress:
            total_chapters = sum(book["chapters"] for book in BIBLE_BOOKS)
            task = progress.add_task("[cyan]Getting chapter data...", total=total_chapters)
            
            # Populate chapters table with verse counts
            for book in BIBLE_BOOKS:
                for chapter in range(1, book["chapters"] + 1):
                    # Check if we already have verse count data
                    cursor.execute(
                        "SELECT COUNT(*) FROM chapters WHERE book_id = ? AND chapter_number = ?",
                        (book["id"], chapter)
                    )
                    if cursor.fetchone()[0] == 0:
                        verse_count = get_verse_count(book["name"], chapter)
                        cursor.execute(
                            "INSERT INTO chapters (book_id, chapter_number, total_verses) VALUES (?, ?, ?)",
                            (book["id"], chapter, verse_count)
                        )
                    progress.update(task, advance=1)
        
        conn.commit()
    
    # Check if we need to initialize reading progress
    cursor.execute("SELECT COUNT(*) FROM reading_progress")
    if cursor.fetchone()[0] == 0:
        # Start at Genesis 1:1
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO reading_progress (book_id, chapter_number, verse_number, timestamp) VALUES (?, ?, ?, ?)",
            (1, 1, 1, timestamp)
        )
        conn.commit()
    
    conn.close()

def get_current_progress() -> Tuple[str, int, int]:
    """Get the current reading position."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT b.name, rp.chapter_number, rp.verse_number
    FROM reading_progress rp
    JOIN books b ON rp.book_id = b.id
    ORDER BY rp.timestamp DESC
    LIMIT 1
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result
    else:
        # Default to starting at Genesis 1:1
        return ("Genesis", 1, 1)

# 1. Fix for the progress bar calculation to not assume books between jumps are completed
def calculate_percentages() -> Dict[str, float]:
    """Calculate completion percentages based on actual reading history."""
    book, chapter, verse = get_current_progress()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current book ID
    cursor.execute("SELECT id, total_chapters FROM books WHERE name = ?", (book,))
    book_id, total_chapters = cursor.fetchone()
    
    # Get total verses in current chapter
    cursor.execute(
        "SELECT total_verses FROM chapters WHERE book_id = ? AND chapter_number = ?",
        (book_id, chapter)
    )
    result = cursor.fetchone()
    total_verses = result[0] if result else 30  # Default if not found
    
    # Calculate chapter completion
    chapter_percentage = (verse / total_verses) * 100
    
    # Calculate book completion
    # First, get sum of verses in chapters before current chapter
    cursor.execute(
        """
        SELECT SUM(total_verses) 
        FROM chapters 
        WHERE book_id = ? AND chapter_number < ?
        """,
        (book_id, chapter)
    )
    result = cursor.fetchone()
    verses_before_current_chapter = result[0] if result and result[0] else 0
    
    # Get total verses in book
    cursor.execute(
        "SELECT SUM(total_verses) FROM chapters WHERE book_id = ?",
        (book_id,)
    )
    result = cursor.fetchone()
    total_verses_in_book = result[0] if result and result[0] else 1  # Avoid division by zero
    
    book_percentage = ((verses_before_current_chapter + verse) / total_verses_in_book) * 100
    
    # Calculate Bible completion based on actual reading history
    # Instead of assuming all previous books are read, count verses from reading history
    cursor.execute("""
        SELECT COUNT(*) FROM reading_history
    """)
    total_verses_read = cursor.fetchone()[0]
    
    # Get total verses in Bible
    cursor.execute("SELECT SUM(total_verses) FROM chapters")
    result = cursor.fetchone()
    total_verses_in_bible = result[0] if result and result[0] else 1  # Avoid division by zero
    
    bible_percentage = (total_verses_read / total_verses_in_bible) * 100
    
    conn.close()
    
    return {
        "chapter": chapter_percentage,
        "book": book_percentage,
        "bible": bible_percentage
    }

def get_reading_rate() -> float:
    """Calculate the average verses read per day."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get reading history
    cursor.execute(
        """
        SELECT date_read
        FROM reading_history
        ORDER BY date_read
        """
    )
    reading_history = cursor.fetchall()
    
    if len(reading_history) < 2:
        conn.close()
        return 10.0  # Default rate if not enough data
    
    # Calculate average verses per day
    verse_counts_by_day = {}
    for row in reading_history:
        date_read = row[0].split()[0] if ' ' in row[0] else row[0].split('T')[0]
        if date_read not in verse_counts_by_day:
            verse_counts_by_day[date_read] = 0
        verse_counts_by_day[date_read] += 1
    
    daily_verses = list(verse_counts_by_day.values())
    
    conn.close()
    
    if not daily_verses:
        return 10.0  # Default
    
    return sum(daily_verses) / len(daily_verses)

def estimate_completion_times() -> Dict[str, int]:
    """Estimate days to complete current book and entire Bible."""
    book, chapter, verse = get_current_progress()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current book ID
    cursor.execute("SELECT id FROM books WHERE name = ?", (book,))
    book_id = cursor.fetchone()[0]
    
    # Get remaining verses in current book
    cursor.execute(
        """
        SELECT SUM(total_verses) 
        FROM chapters 
        WHERE book_id = ? AND chapter_number > ?
        """,
        (book_id, chapter)
    )
    result = cursor.fetchone()
    remaining_verses_in_book = result[0] if result and result[0] else 0
    
    # Add remaining verses in current chapter
    cursor.execute(
        "SELECT total_verses FROM chapters WHERE book_id = ? AND chapter_number = ?",
        (book_id, chapter)
    )
    result = cursor.fetchone()
    total_verses_in_chapter = result[0] if result else 30
    remaining_verses_in_chapter = total_verses_in_chapter - verse
    
    remaining_verses_in_book += remaining_verses_in_chapter
    
    # Get remaining verses in Bible
    cursor.execute(
        """
        SELECT SUM(c.total_verses)
        FROM chapters c
        JOIN books b ON c.book_id = b.id
        WHERE b.book_order > ?
        """,
        (book_id,)
    )
    result = cursor.fetchone()
    remaining_verses_after_book = result[0] if result and result[0] else 0
    
    remaining_verses_in_bible = remaining_verses_in_book + remaining_verses_after_book
    
    conn.close()
    
    # Calculate estimates
    reading_rate = get_reading_rate()
    days_to_complete_book = math.ceil(remaining_verses_in_book / reading_rate) if reading_rate > 0 else 30
    days_to_complete_bible = math.ceil(remaining_verses_in_bible / reading_rate) if reading_rate > 0 else 365
    
    return {
        "book": days_to_complete_book,
        "bible": days_to_complete_bible
    }

def get_books_read() -> List[str]:
    """Get a list of completely read books based on reading history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all books
    cursor.execute("SELECT id, name, total_chapters FROM books ORDER BY book_order")
    all_books = cursor.fetchall()
    
    completed_books = []
    
    for book_id, book_name, total_chapters in all_books:
        # Check if we have read every chapter of this book
        is_book_complete = True
        
        for chapter in range(1, total_chapters + 1):
            # Get total verses in this chapter
            cursor.execute(
                "SELECT total_verses FROM chapters WHERE book_id = ? AND chapter_number = ?",
                (book_id, chapter)
            )
            result = cursor.fetchone()
            if not result:
                is_book_complete = False
                break
                
            total_verses = result[0]
            
            # Check if we've read the last verse of this chapter
            cursor.execute(
                """
                SELECT COUNT(*) FROM reading_history
                WHERE book_id = ? AND chapter_number = ? AND verse_number = ?
                """,
                (book_id, chapter, total_verses)
            )
            
            if cursor.fetchone()[0] == 0:
                # Haven't read the last verse of this chapter
                is_book_complete = False
                break
        
        if is_book_complete:
            completed_books.append(book_name)
    
    conn.close()
    return completed_books

# 1. Fixed get_completed_chapters function with more direct query
def get_completed_chapters(book_name: str) -> List[int]:
    """Get a list of completed chapters for a specific book."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get book ID
    cursor.execute("SELECT id FROM books WHERE name = ?", (book_name,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return []
    
    book_id = result[0]
    
    # More direct query that should find completed chapters more reliably
    cursor.execute("""
        SELECT DISTINCT rh.chapter_number
        FROM reading_history rh
        JOIN chapters c ON rh.book_id = c.book_id AND rh.chapter_number = c.chapter_number
        WHERE rh.book_id = ? AND rh.verse_number >= c.total_verses
        ORDER BY rh.chapter_number
    """, (book_id,))
    
    completed_chapters = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return completed_chapters

# Updated part of display_dashboard function for chapter grid
def display_chapter_grid(book, completed_chapters):
    """Display a grid of chapters showing which ones are completed."""
    console.print(f"\n[bold cyan]Chapter Completion in {book}:[/bold cyan]")
    
    # Get total chapters for current book
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT total_chapters FROM books WHERE name = ?", (book,))
    total_chapters = cursor.fetchone()[0]
    conn.close()
    
    # Create a visual chapter grid
    chapter_grid = Table.grid(padding=1)
    
    # Determine number of columns based on total chapters
    cols = min(10, total_chapters)  # Max 10 columns
    
    # Create rows for the grid
    rows = []
    current_row = []
    
    for chap_num in range(1, total_chapters + 1):
        if chap_num in completed_chapters:
            current_row.append(f"[green]✓ {chap_num}[/green]")
        else:
            current_row.append(f"{chap_num}")
        
        if len(current_row) >= cols:
            rows.append(current_row)
            current_row = []
    
    # Add any remaining chapters
    if current_row:
        rows.append(current_row)
    
    # Add rows to the grid
    for row_data in rows:
        chapter_grid.add_row(*row_data)
    
    console.print(chapter_grid)


def get_next_verse() -> Tuple[str, int, int]:
    """Get the next verse to read."""
    book, chapter, verse = get_current_progress()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM books WHERE name = ?", (book,))
    book_id = cursor.fetchone()[0]
    
    cursor.execute(
        "SELECT total_verses FROM chapters WHERE book_id = ? AND chapter_number = ?",
        (book_id, chapter)
    )
    result = cursor.fetchone()
    total_verses = result[0] if result else 30  # Default if not found
    
    next_book = book
    next_chapter = chapter
    next_verse = verse + 1
    
    if next_verse > total_verses:
        next_verse = 1
        next_chapter += 1
        
        cursor.execute(
            "SELECT total_chapters FROM books WHERE id = ?",
            (book_id,)
        )
        total_chapters = cursor.fetchone()[0]
        
        if next_chapter > total_chapters:
            next_chapter = 1
            cursor.execute(
                "SELECT name FROM books WHERE book_order = (SELECT book_order + 1 FROM books WHERE id = ?)",
                (book_id,)
            )
            result = cursor.fetchone()
            if result:
                next_book = result[0]
    
    conn.close()
    return (next_book, next_chapter, next_verse)

def update_progress(book: str, chapter: int, verse: int, auto_advance=False):
    """
    Update the reading progress.
    
    Args:
        book: Book name
        chapter: Chapter number
        verse: Verse number
        auto_advance: If True and this is the last verse, advance to next chapter
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM books WHERE name = ?", (book,))
        result = cursor.fetchone()
        if not result:
            console.print(f"[red]Error: Book '{book}' not found.[/red]")
            return
        
        book_id = result[0]
        
        # Check if this is the last verse of the chapter
        cursor.execute(
            "SELECT total_verses FROM chapters WHERE book_id = ? AND chapter_number = ?",
            (book_id, chapter)
        )
        result = cursor.fetchone()
        total_verses = result[0] if result else 30
        
        # Always record the current progress first
        timestamp = datetime.datetime.now().isoformat()
        
        # Record the exact verse marked (this is crucial)
        cursor.execute(
            """
            INSERT INTO reading_progress (book_id, chapter_number, verse_number, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (book_id, chapter, verse, timestamp)
        )
        
        # Add to reading history
        cursor.execute(
            """
            INSERT INTO reading_history (book_id, chapter_number, verse_number, date_read)
            VALUES (?, ?, ?, ?)
            """,
            (book_id, chapter, verse, timestamp)
        )
        
        # If auto-advancing, move to the next chapter or book
        if verse >= total_verses and auto_advance:
            cursor.execute(
                "SELECT total_chapters FROM books WHERE id = ?",
                (book_id,)
            )
            total_chapters = cursor.fetchone()[0]
            
            # Create a new timestamp for the next position
            next_timestamp = datetime.datetime.now().isoformat()
            
            if chapter >= total_chapters:
                # Last chapter of book, move to next book
                cursor.execute(
                    "SELECT name FROM books WHERE book_order = (SELECT book_order + 1 FROM books WHERE id = ?)",
                    (book_id,)
                )
                result = cursor.fetchone()
                if result:
                    next_book = result[0]
                    next_chapter = 1
                    next_verse = 1
                    
                    # Update progress with next book
                    cursor.execute(
                        """
                        INSERT INTO reading_progress (book_id, chapter_number, verse_number, timestamp)
                        VALUES ((SELECT id FROM books WHERE name = ?), ?, ?, ?)
                        """,
                        (next_book, next_chapter, next_verse, next_timestamp)
                    )
                    
                    # Add to reading history
                    cursor.execute(
                        """
                        INSERT INTO reading_history (book_id, chapter_number, verse_number, date_read)
                        VALUES ((SELECT id FROM books WHERE name = ?), ?, ?, ?)
                        """,
                        (next_book, next_chapter, next_verse, next_timestamp)
                    )
            else:
                # Move to next chapter
                next_chapter = chapter + 1
                
                # Update progress with next chapter
                cursor.execute(
                    """
                    INSERT INTO reading_progress (book_id, chapter_number, verse_number, timestamp)
                    VALUES (?, ?, ?, ?)
                    """,
                    (book_id, next_chapter, 1, next_timestamp)
                )
                
                # Add to reading history
                cursor.execute(
                    """
                    INSERT INTO reading_history (book_id, chapter_number, verse_number, date_read)
                    VALUES (?, ?, ?, ?)
                    """,
                    (book_id, next_chapter, 1, next_timestamp)
                )
        
        conn.commit()
    finally:        
        # Always close the connection, even if an error occurs
        conn.close()
def get_downloaded_books() -> List[str]:
    """Get a list of books that have been downloaded."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT b.name 
        FROM verses v
        JOIN books b ON v.book_id = b.id
        ORDER BY b.book_order
    """)
    
    books = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return books

def download_book(book_name: str):
    """Download all verses for a specific book."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM books WHERE name = ?", (book_name,))
    result = cursor.fetchone()
    if not result:
        console.print(f"[red]Error: Book '{book_name}' not found.[/red]")
        conn.close()
        return False
    
    book_id = result[0]
    
    # Get all chapters for this book
    cursor.execute(
        "SELECT chapter_number, total_verses FROM chapters WHERE book_id = ? ORDER BY chapter_number",
        (book_id,)
    )
    chapters = cursor.fetchall()
    
    if not chapters:
        console.print(f"[red]Error: No chapter data found for '{book_name}'.[/red]")
        conn.close()
        return False
    
    total_verses = sum(chapter[1] for chapter in chapters)
    
    console.print(f"[bold cyan]Downloading {book_name} ({total_verses} verses)...[/bold cyan]")
    
    with Progress() as progress:
        task = progress.add_task(f"[cyan]Downloading {book_name}...", total=total_verses)
        
        for chapter_num, verse_count in chapters:
            for verse_num in range(1, verse_count + 1):
                # Check if verse already exists
                cursor.execute(
                    "SELECT COUNT(*) FROM verses WHERE book_id = ? AND chapter_number = ? AND verse_number = ?",
                    (book_id, chapter_num, verse_num)
                )
                if cursor.fetchone()[0] > 0:
                    progress.update(task, advance=1)
                    continue
                
                try:
                    # Add a small delay to avoid overwhelming the server
                    time.sleep(0.2)
                    
                    # Get verse text
                    verse_text = get_verse_text(book_name, chapter_num, verse_num)
                    
                    # Save to database
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO verses 
                        (book_id, chapter_number, verse_number, verse_text) 
                        VALUES (?, ?, ?, ?)
                        """,
                        (book_id, chapter_num, verse_num, verse_text)
                    )
                    
                    # Commit every 10 verses
                    if verse_num % 10 == 0:
                        conn.commit()
                
                except Exception as e:
                    console.print(f"[red]Error downloading {book_name} {chapter_num}:{verse_num}: {e}[/red]")
                
                progress.update(task, advance=1)
    
    conn.commit()
    conn.close()
    
    console.print(f"[bold green]✓ {book_name} downloaded successfully![/bold green]")
    return True

def export_to_json(output_file="bible_export.json", format_type="nested", book_filter=None):
    """Export Bible data to JSON file."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Make SQLite return rows as dictionaries
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if format_type == "nested":
        # Get all books or filtered books
        if book_filter:
            cursor.execute(
                "SELECT id, name FROM books WHERE name = ? ORDER BY book_order", 
                (book_filter,)
            )
        else:
            cursor.execute("SELECT id, name FROM books ORDER BY book_order")
        
        books = [dict(row) for row in cursor.fetchall()]
        
        bible_data = []
        
        for book in books:
            book_data = {
                "book": book["name"],
                "chapters": []
            }
            
            # Get chapters for this book
            cursor.execute(
                "SELECT chapter_number FROM chapters WHERE book_id = ? ORDER BY chapter_number",
                (book["id"],)
            )
            chapters = [dict(row) for row in cursor.fetchall()]
            
            for chapter in chapters:
                chapter_data = {
                    "chapter": chapter["chapter_number"],
                    "verses": []
                }
                
                # Get verses for this chapter
                cursor.execute(
                    """
                    SELECT verse_number, verse_text 
                    FROM verses 
                    WHERE book_id = ? AND chapter_number = ? 
                    ORDER BY verse_number
                    """,
                    (book["id"], chapter["chapter_number"])
                )
                verses = [dict(row) for row in cursor.fetchall()]
                
                for verse in verses:
                    chapter_data["verses"].append({
                        "verse": verse["verse_number"],
                        "text": verse["verse_text"]
                    })
                
                book_data["chapters"].append(chapter_data)
            
            bible_data.append(book_data)
        
    elif format_type == "flat":
        # Get all verses in a flat structure
        if book_filter:
            cursor.execute("""
                SELECT b.name as book, v.chapter_number as chapter, v.verse_number as verse, v.verse_text as text
                FROM verses v
                JOIN books b ON v.book_id = b.id
                WHERE b.name = ?
                ORDER BY b.book_order, v.chapter_number, v.verse_number
            """, (book_filter,))
        else:
            cursor.execute("""
                SELECT b.name as book, v.chapter_number as chapter, v.verse_number as verse, v.verse_text as text
                FROM verses v
                JOIN books b ON v.book_id = b.id
                ORDER BY b.book_order, v.chapter_number, v.verse_number
            """)
        
        bible_data = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(bible_data, f, indent=2, ensure_ascii=False)
    
    console.print(f"[bold green]✓ Bible data exported to {output_file}[/bold green]")
    return True

def display_dashboard():
    """Display the main dashboard."""
    console.clear()
    console.print(Panel.fit("[bold blue]Bible Study Tracker[/bold blue]", box=box.DOUBLE))
    
    # Get current progress
    book, chapter, verse = get_current_progress()
    console.print(f"\n[bold green]Current Position:[/bold green] {book} {chapter}:{verse}")
    
    # Display verse content (from downloaded text if available)
    console.print("\n[bold yellow]Current Verse:[/bold yellow]")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if we have the verse downloaded
    cursor.execute("SELECT id FROM books WHERE name = ?", (book,))
    book_id = cursor.fetchone()[0]
    
    cursor.execute(
        "SELECT verse_text FROM verses WHERE book_id = ? AND chapter_number = ? AND verse_number = ?",
        (book_id, chapter, verse)
    )
    result = cursor.fetchone()
    
    if result:
        # Use downloaded verse
        console.print(f"{book} {chapter}:{verse} - {result[0]}")
    else:
        # Use scraper but filter out debug output
        try:
            verse_text = get_verse_text(book, chapter, verse)
            console.print(f"{book} {chapter}:{verse} - {verse_text}")
        except Exception as e:
            console.print(f"[red]Error retrieving verse: {e}[/red]")
    
    conn.close()
    
    # Display next verse
    next_book, next_chapter, next_verse = get_next_verse()
    console.print(f"\n[bold cyan]Next Verse:[/bold cyan] {next_book} {next_chapter}:{next_verse}")
    
    # Generate JW.org link
    formatted_book = next_book.lower().replace(' ', '-')
    if formatted_book[0].isdigit():
        formatted_book = formatted_book.replace(' ', '-', 1)
    jw_link = f"https://www.jw.org/en/library/bible/nwt/books/{formatted_book}/{next_chapter}/"
    console.print(f"[link={jw_link}]Continue reading on JW.org[/link]")
    
    # Show completion percentages
    percentages = calculate_percentages()
    console.print("\n[bold magenta]Completion Progress:[/bold magenta]")
    
    # Create progress bars
    table = Table(show_header=True, header_style="bold")
    table.add_column("Metric")
    table.add_column("Progress", width=40)
    table.add_column("Percentage")
    
    # Chapter progress bar
    chapter_bar = "█" * int(percentages["chapter"] / 2.5) + " " * (40 - int(percentages["chapter"] / 2.5))
    chapter_color = "green" if percentages["chapter"] > 50 else "yellow"
    
    # Book progress bar
    book_bar = "█" * int(percentages["book"] / 2.5) + " " * (40 - int(percentages["book"] / 2.5))
    book_color = "green" if percentages["book"] > 50 else "yellow"
    
    # Bible progress bar
    bible_bar = "█" * int(percentages["bible"] / 2.5) + " " * (40 - int(percentages["bible"] / 2.5))
    bible_color = "green" if percentages["bible"] > 50 else "yellow"
    
    table.add_row(
        "Current Chapter",
        f"[{chapter_color}]{chapter_bar}[/{chapter_color}]",
        f"[bold]{percentages['chapter']:.1f}%[/bold]"
    )
    
    table.add_row(
        "Current Book",
        f"[{book_color}]{book_bar}[/{book_color}]",
        f"[bold]{percentages['book']:.1f}%[/bold]"
    )
    
    table.add_row(
        "Entire Bible",
        f"[{bible_color}]{bible_bar}[/{bible_color}]",
        f"[bold]{percentages['bible']:.1f}%[/bold]"
    )
    
    console.print(table)
    
    # Display estimated completion times
    estimates = estimate_completion_times()
    console.print("\n[bold green]Estimated Completion Times:[/bold green]")
    console.print(f"Current Book: [bold]{estimates['book']}[/bold] days")
    console.print(f"Entire Bible: [bold]{estimates['bible']}[/bold] days")
    
    # Display completed chapters for current book
    completed_chapters = get_completed_chapters(book)
    display_chapter_grid(book, completed_chapters)
    
    # Display completed books
    completed_books = get_books_read()
    if completed_books:
        console.print("\n[bold blue]Completed Books:[/bold blue]")
        
        # Create a table for completed books (4 books per row)
        book_table = Table(show_header=False, box=box.SIMPLE)
        
        # Create columns based on the number of books
        cols = min(4, len(completed_books))
        for _ in range(cols):
            book_table.add_column("", justify="left")
        
        # Fill the table with books
        rows = []
        row = []
        for i, book in enumerate(completed_books):
            row.append(f"✓ {book}")
            if (i + 1) % cols == 0:
                rows.append(row)
                row = []
        
        # Add any remaining books
        if row:
            while len(row) < cols:
                row.append("")
            rows.append(row)
        
        # Add rows to the table
        for row in rows:
            book_table.add_row(*row)
        
        console.print(book_table)
    
    # Display downloaded books
    downloaded_books = get_downloaded_books()
    if downloaded_books:
        console.print("\n[bold green]Downloaded Books:[/bold green]")
        
        # Create a table for downloaded books (4 books per row)
        download_table = Table(show_header=False, box=box.SIMPLE)
        
        # Create columns based on the number of books
        cols = min(4, len(downloaded_books))
        for _ in range(cols):
            download_table.add_column("", justify="left")
        
        # Fill the table with books
        rows = []
        row = []
        for i, book in enumerate(downloaded_books):
            row.append(f"📥 {book}")
            if (i + 1) % cols == 0:
                rows.append(row)
                row = []
        
        # Add any remaining books
        if row:
            while len(row) < cols:
                row.append("")
            rows.append(row)
        
        # Add rows to the table
        for row in rows:
            download_table.add_row(*row)
        
        console.print(download_table)
    
       # Show commands
    console.print("\n[bold]Commands:[/bold]")
    console.print("  [cyan]u[/cyan] - Update reading progress")
    console.print("  [cyan]r[/cyan] - Go to a different book/chapter/verse")
    console.print("  [cyan]d[/cyan] - Download Bible content")
    console.print("  [cyan]e[/cyan] - Export Bible to JSON")
    console.print("  [cyan]b[/cyan] - Read downloaded Bible books")
    console.print("  [cyan]s[/cyan] - View statistics")
    console.print("  [cyan]x[/cyan] - Reset reading progress")
    console.print("  [cyan]q[/cyan] - Quit")

def update_reading_progress():
    """Handle updating reading progress."""
    # Get current progress first
    book, chapter, verse = get_current_progress()
    
    console.clear()
    console.print(Panel.fit("[bold blue]Update Reading Progress[/bold blue]", box=box.SIMPLE))
    
    # Display current position clearly
    console.print(f"\n[bold yellow]Current Position:[/bold yellow] {book} {chapter}:{verse}")
    
    # Display options
    console.print("\n[bold]Options:[/bold]")
    console.print(f"1. Mark current chapter ({book} {chapter}) as complete and advance to next chapter")
    console.print(f"2. Mark specific verse in current chapter as read")
    console.print("3. Cancel")
    
    choice = console.input("\n[bold]Choose an option (1-3):[/bold] ").strip()
    
    if choice == "1":
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM books WHERE name = ?", (book,))
        book_id = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT total_verses FROM chapters WHERE book_id = ? AND chapter_number = ?",
            (book_id, chapter)
        )
        result = cursor.fetchone()
        total_verses = result[0] if result else 30  # Default if not found
        
        conn.close()
        
        update_progress(book, chapter, total_verses, auto_advance=True)
        
        # Get the new position after update
        new_book, new_chapter, _ = get_current_progress()
        
        if new_book != book or new_chapter != chapter:
            console.print(f"[green]✓ Chapter {book} {chapter} marked as complete![/green]")
            console.print(f"[green]→ Advanced to {new_book} {new_chapter}:1[/green]")
        else:
            console.print(f"[green]✓ Chapter {book} {chapter} marked as complete![/green]")
    
    elif choice == "2":
        console.print(f"\n[bold]Marking progress in {book} {chapter}[/bold]")
        
        new_verse = console.input(f"[bold]Enter verse number where you stopped ([i]current: {verse}[/i]):[/bold] ").strip()
        if not new_verse:
            new_verse = verse
        else:
            try:
                new_verse = int(new_verse)
            except ValueError:
                console.print("[red]Invalid verse number. Using current verse.[/red]")
                new_verse = verse
        
        update_progress(book, chapter, int(new_verse))
        console.print(f"[green]✓ Progress updated to {book} {chapter}:{new_verse}![/green]")
    
    elif choice == "3":
        console.print("[yellow]Update canceled.[/yellow]")
    
    else:
        console.print("[red]Invalid choice.[/red]")
    
    # Wait for user to press Enter
    console.input("\nPress Enter to return to the dashboard...")

def jump_to_position():
    """Jump to a different reading position."""
    console.clear()
    console.print(Panel.fit("[bold blue]Jump to Position[/bold blue]", box=box.SIMPLE))
    
    # Get current progress
    current_book, current_chapter, current_verse = get_current_progress()
    console.print(f"\n[bold yellow]Current Position:[/bold yellow] {current_book} {current_chapter}:{current_verse}")
    
    # List all books
    console.print("\n[bold cyan]Available Books:[/bold cyan]")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM books ORDER BY book_order")
    all_books = [row[0] for row in cursor.fetchall()]
    
    book_table = Table(show_header=False, box=box.SIMPLE)
    cols = 4
    for _ in range(cols):
        book_table.add_column("", justify="left")
    
    # Fill the table with books
    rows = []
    row = []
    for i, book in enumerate(all_books):
        row.append(book)
        if (i + 1) % cols == 0:
            rows.append(row)
            row = []
    
    # Add any remaining books
    if row:
        while len(row) < cols:
            row.append("")
        rows.append(row)
    
    # Add rows to the table
    for row in rows:
        book_table.add_row(*row)
    
    console.print(book_table)
    
    # Get new position
    new_book = console.input("\n[bold]Enter book name (or press Enter to keep current):[/bold] ").strip()
    if not new_book:
        new_book = current_book
    else:
        # Find closest match
        match_found = False
        for book in all_books:
            if book.lower() == new_book.lower():
                new_book = book
                match_found = True
                break
        
        if not match_found:
            # Try partial match
            matches = [book for book in all_books if new_book.lower() in book.lower()]
            if matches:
                new_book = matches[0]
                console.print(f"[yellow]Using closest match: {new_book}[/yellow]")
            else:
                console.print(f"[red]Book '{new_book}' not found. Using current book.[/red]")
                new_book = current_book
    
    # Get book info
    cursor.execute("SELECT id, total_chapters FROM books WHERE name = ?", (new_book,))
    book_id, total_chapters = cursor.fetchone()
    
    console.print(f"[cyan]{new_book} has {total_chapters} chapters[/cyan]")
    
    new_chapter = console.input(f"[bold]Enter chapter (1-{total_chapters}):[/bold] ").strip()
    try:
        new_chapter = int(new_chapter)
        if new_chapter < 1 or new_chapter > total_chapters:
            console.print(f"[red]Chapter must be between 1 and {total_chapters}. Using chapter 1.[/red]")
            new_chapter = 1
    except ValueError:
        console.print("[red]Invalid chapter. Using chapter 1.[/red]")
        new_chapter = 1
    
    # Get verse count for this chapter
    cursor.execute(
        "SELECT total_verses FROM chapters WHERE book_id = ? AND chapter_number = ?",
        (book_id, new_chapter)
    )
    result = cursor.fetchone()
    total_verses = result[0] if result else 30
    
    console.print(f"[cyan]{new_book} {new_chapter} has {total_verses} verses[/cyan]")
    
    new_verse = console.input(f"[bold]Enter verse (1-{total_verses}):[/bold] ").strip()
    try:
        new_verse = int(new_verse)
        if new_verse < 1 or new_verse > total_verses:
            console.print(f"[red]Verse must be between 1 and {total_verses}. Using verse 1.[/red]")
            new_verse = 1
    except ValueError:
        console.print("[red]Invalid verse. Using verse 1.[/red]")
        new_verse = 1
    
    conn.close()
    
    # Update progress
    update_progress(new_book, new_chapter, new_verse)
    console.print(f"[bold green]✓ Position updated to {new_book} {new_chapter}:{new_verse}![/bold green]")
    
    # Wait for user to press Enter
    console.input("\nPress Enter to return to the dashboard...")

def download_bible_content():
    """Menu for downloading Bible content."""
    console.clear()
    console.print(Panel.fit("[bold blue]Download Bible Content[/bold blue]", box=box.SIMPLE))
    
    # Get downloaded books
    downloaded_books = get_downloaded_books()
    
    if downloaded_books:
        console.print("\n[bold green]Already Downloaded Books:[/bold green]")
        for book in downloaded_books:
            console.print(f"  ✓ {book}")
    
    console.print("\n[bold]Options:[/bold]")
    console.print("1. Download a specific book")
    console.print("2. Download current book")
    console.print("3. Cancel")
    
    choice = console.input("\n[bold]Choose an option (1-3):[/bold] ").strip()
    
    if choice == "1":
        console.clear()
        console.print(Panel.fit("[bold blue]Download a Specific Book[/bold blue]", box=box.SIMPLE))
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM books ORDER BY book_order")
        all_books = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Display books in columns
        book_table = Table(show_header=False, box=box.SIMPLE)
        cols = 4
        for _ in range(cols):
            book_table.add_column("", justify="left")
        
        # Fill the table with books
        rows = []
        row = []
        for i, book in enumerate(all_books):
            prefix = "✓" if book in downloaded_books else " "
            row.append(f"{prefix} {book}")
            if (i + 1) % cols == 0:
                rows.append(row)
                row = []
        
        # Add any remaining books
        if row:
            while len(row) < cols:
                row.append("")
            rows.append(row)
        
        # Add rows to the table
        for row in rows:
            book_table.add_row(*row)
        
        console.print(book_table)
        
        book_name = console.input("\n[bold]Enter the name of the book to download:[/bold] ").strip()
        
        # Find closest match
        match_found = False
        for book in all_books:
            if book.lower() == book_name.lower():
                book_name = book
                match_found = True
                break
        
        if not match_found:
            # Try partial match
            matches = [book for book in all_books if book_name.lower() in book.lower()]
            if matches:
                book_name = matches[0]
                console.print(f"[yellow]Using closest match: {book_name}[/yellow]")
                download_book(book_name)
            else:
                console.print(f"[red]Book '{book_name}' not found.[/red]")
        else:
            download_book(book_name)
    
    elif choice == "2":
        book, _, _ = get_current_progress()
        download_book(book)
    
    elif choice != "3":
        console.print("[red]Invalid choice.[/red]")
    
    # Wait for user to press Enter
    console.input("\nPress Enter to return to the dashboard...")

def export_bible_menu():
    """Menu for exporting Bible content to JSON."""
    console.clear()
    console.print(Panel.fit("[bold blue]Export Bible to JSON[/bold blue]", box=box.SIMPLE))
    
    # Get downloaded books
    downloaded_books = get_downloaded_books()
    
    if not downloaded_books:
        console.print("[yellow]No books have been downloaded yet. Nothing to export.[/yellow]")
        console.input("\nPress Enter to return to the dashboard...")
        return
    
    console.print("\n[bold green]Downloaded Books Available for Export:[/bold green]")
    for book in downloaded_books:
        console.print(f"  ✓ {book}")
    
    console.print("\n[bold]Export Options:[/bold]")
    console.print("1. Export all downloaded books")
    console.print("2. Export a specific book")
    console.print("3. Cancel")
    
    choice = console.input("\n[bold]Choose an option (1-3):[/bold] ").strip()
    
    if choice == "1":
        format_choice = console.input("\n[bold]Choose format ([n]ested or [f]lat):[/bold] ").strip().lower()
        format_type = "nested" if format_choice.startswith("n") else "flat"
        
        filename = console.input("\n[bold]Enter output filename (default: bible_export.json):[/bold] ").strip()
        if not filename:
            filename = "bible_export.json"
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        export_to_json(filename, format_type)
    
    elif choice == "2":
        book_name = console.input("\n[bold]Enter the name of the book to export:[/bold] ").strip()
        
        # Find closest match
        match_found = False
        for book in downloaded_books:
            if book.lower() == book_name.lower():
                book_name = book
                match_found = True
                break
        
        if not match_found:
            # Try partial match
            matches = [book for book in downloaded_books if book_name.lower() in book.lower()]
            if matches:
                book_name = matches[0]
                console.print(f"[yellow]Using closest match: {book_name}[/yellow]")
            else:
                console.print(f"[red]Book '{book_name}' not found in downloaded books.[/red]")
                console.input("\nPress Enter to return to the dashboard...")
                return
        
        format_choice = console.input("\n[bold]Choose format ([n]ested or [f]lat):[/bold] ").strip().lower()
        format_type = "nested" if format_choice.startswith("n") else "flat"
        
        filename = console.input(f"\n[bold]Enter output filename (default: {book_name.lower()}_export.json):[/bold] ").strip()
        if not filename:
            filename = f"{book_name.lower()}_export.json"
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        export_to_json(filename, format_type, book_name)
    
    elif choice != "3":
        console.print("[red]Invalid choice.[/red]")
    
    # Wait for user to press Enter
    console.input("\nPress Enter to return to the dashboard...")

def read_downloaded_book():
    """Read a downloaded book in a nice interface."""
    console.clear()
    console.print(Panel.fit("[bold blue]Read Bible[/bold blue]", box=box.SIMPLE))
    
    # Get downloaded books
    downloaded_books = get_downloaded_books()
    
    if not downloaded_books:
        console.print("[yellow]No books have been downloaded yet. Please download books first.[/yellow]")
        console.input("\nPress Enter to return to the dashboard...")
        return
    
    console.print("\n[bold]Select a downloaded book to read:[/bold]")
    
    # Display books in a table
    book_table = Table(show_header=False, box=box.SIMPLE)
    cols = 4
    for _ in range(cols):
        book_table.add_column("", justify="left")
    
    # Fill the table with books
    rows = []
    row = []
    for i, book in enumerate(downloaded_books):
        row.append(f"{i+1}. {book}")
        if (i + 1) % cols == 0:
            rows.append(row)
            row = []
    
    # Add any remaining books
    if row:
        while len(row) < cols:
            row.append("")
        rows.append(row)
    
    # Add rows to the table
    for row in rows:
        book_table.add_row(*row)
    
    console.print(book_table)
    
    # Get book selection
    book_choice = console.input("\n[bold]Enter book number or name:[/bold] ").strip()
    
    selected_book = None
    try:
        book_idx = int(book_choice) - 1
        if 0 <= book_idx < len(downloaded_books):
            selected_book = downloaded_books[book_idx]
    except ValueError:
        # Try to match by name
        for book in downloaded_books:
            if book_choice.lower() in book.lower():
                selected_book = book
                break
    
    if not selected_book:
        console.print("[red]Invalid book selection.[/red]")
        console.input("\nPress Enter to return to the dashboard...")
        return
    
    # Get chapters for this book
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM books WHERE name = ?", (selected_book,))
    book_id = cursor.fetchone()[0]
    
    cursor.execute(
        "SELECT total_chapters FROM books WHERE id = ?",
        (book_id,)
    )
    total_chapters = cursor.fetchone()[0]
    
    # Select chapter
    console.print(f"\n[bold]{selected_book} has {total_chapters} chapters.[/bold]")
    chapter_choice = console.input("\n[bold]Enter chapter number:[/bold] ").strip()
    
    try:
        chapter = int(chapter_choice)
        if chapter < 1 or chapter > total_chapters:
            console.print(f"[red]Chapter must be between 1 and {total_chapters}.[/red]")
            conn.close()
            console.input("\nPress Enter to return to the dashboard...")
            return
    except ValueError:
        console.print("[red]Invalid chapter number.[/red]")
        conn.close()
        console.input("\nPress Enter to return to the dashboard...")
        return
    
    # Get verses for this chapter
    cursor.execute(
        "SELECT verse_number, verse_text FROM verses WHERE book_id = ? AND chapter_number = ? ORDER BY verse_number",
        (book_id, chapter)
    )
    verses = cursor.fetchall()
    conn.close()
    
    if not verses:
        console.print(f"[yellow]No verses found for {selected_book} {chapter}. This chapter may not be downloaded.[/yellow]")
        console.input("\nPress Enter to return to the dashboard...")
        return
    
    # Display the chapter
    while True:
        console.clear()
        console.print(Panel.fit(f"[bold blue]{selected_book} Chapter {chapter}[/bold blue]", box=box.DOUBLE))
        
        # Display verses with nice formatting
        verse_panel = Panel(
            "\n".join([f"[bold cyan]{v[0]}[/bold cyan] {v[1]}" for v in verses]),
            title=f"{selected_book} {chapter}",
            title_align="left",
            border_style="green",
            padding=(1, 2),
            width=100
        )
        console.print(verse_panel)
        
        # Navigation options
        console.print("\n[bold]Navigation:[/bold]")
        console.print("  [cyan]p[/cyan] - Previous chapter")
        console.print("  [cyan]n[/cyan] - Next chapter")
        console.print("  [cyan]m[/cyan] - Mark as current reading position")
        console.print("  [cyan]b[/cyan] - Back to book selection")
        console.print("  [cyan]q[/cyan] - Back to main menu")
        
        nav_choice = console.input("\n[bold]Choose an option:[/bold] ").strip().lower()
        
        if nav_choice == 'p':
            if chapter > 1:
                chapter -= 1
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT verse_number, verse_text FROM verses WHERE book_id = ? AND chapter_number = ? ORDER BY verse_number",
                    (book_id, chapter)
                )
                verses = cursor.fetchall()
                conn.close()
                
                if not verses:
                    console.print(f"[yellow]No verses found for {selected_book} {chapter}. This chapter may not be downloaded.[/yellow]")
                    console.input("\nPress Enter to continue...")
                    chapter += 1  # Revert to previous chapter
            else:
                console.print("[yellow]Already at the first chapter.[/yellow]")
                console.input("\nPress Enter to continue...")
        
        elif nav_choice == 'n':
            if chapter < total_chapters:
                chapter += 1
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT verse_number, verse_text FROM verses WHERE book_id = ? AND chapter_number = ? ORDER BY verse_number",
                    (book_id, chapter)
                )
                verses = cursor.fetchall()
                conn.close()
                
                if not verses:
                    console.print(f"[yellow]No verses found for {selected_book} {chapter}. This chapter may not be downloaded.[/yellow]")
                    console.input("\nPress Enter to continue...")
                    chapter -= 1  # Revert to previous chapter
            else:
                console.print("[yellow]Already at the last chapter.[/yellow]")
                console.input("\nPress Enter to continue...")
        
        elif nav_choice == 'm':
            update_progress(selected_book, chapter, 1)
            console.print(f"[green]✓ Set {selected_book} {chapter}:1 as current reading position.[/green]")
            console.input("\nPress Enter to continue...")
        
        elif nav_choice == 'b':
            break
        
        elif nav_choice == 'q':
            return
        
        else:
            console.print("[red]Invalid choice.[/red]")
            console.input("\nPress Enter to continue...")

def reset_reading_progress():
    """Reset all reading progress while keeping downloaded books."""
    console.clear()
    console.print(Panel.fit("[bold red]Reset Reading Progress[/bold red]", box=box.DOUBLE))
    
    console.print("\n[bold yellow]Warning:[/bold yellow] This will reset all your reading progress and history.")
    console.print("Your downloaded Bible books will be kept intact.")
    console.print("You will be returned to Genesis 1:1.")
    
    confirm = console.input("\n[bold]Are you sure you want to reset your progress? (y/n):[/bold] ").strip().lower()
    
    if confirm == 'y' or confirm == 'yes':
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Delete all reading progress
            cursor.execute("DELETE FROM reading_progress")
            
            # Delete all reading history
            cursor.execute("DELETE FROM reading_history")
            
            # Reset to Genesis 1:1
            timestamp = datetime.datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO reading_progress (book_id, chapter_number, verse_number, timestamp) VALUES (?, ?, ?, ?)",
                (1, 1, 1, timestamp)
            )
            
            conn.commit()
            conn.close()
            
            console.print("\n[bold green]✓ Reading progress has been reset to Genesis 1:1[/bold green]")
            console.print("[green]All downloaded Bible books have been preserved.[/green]")
        except Exception as e:
            console.print(f"\n[bold red]Error resetting progress: {e}[/bold red]")
    else:
        console.print("\n[yellow]Reset cancelled.[/yellow]")
    
    console.input("\nPress Enter to return to the dashboard...")

def view_statistics():
    """Display detailed reading statistics."""
    console.clear()
    console.print(Panel.fit("[bold blue]Reading Statistics[/bold blue]", box=box.SIMPLE))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get reading history
    cursor.execute(
        """
        SELECT b.name, rh.chapter_number, rh.verse_number, rh.date_read
        FROM reading_history rh
        JOIN books b ON rh.book_id = b.id
        ORDER BY rh.date_read DESC
        LIMIT 100
        """
    )
    reading_history = cursor.fetchall()
    
    # Calculate reading streak
    cursor.execute(
        """
        SELECT DISTINCT substr(date_read, 1, 10) as read_date
        FROM reading_history
        ORDER BY read_date DESC
        LIMIT 30
        """
    )
    reading_dates = [row[0] for row in cursor.fetchall()]
    
    current_streak = 0
    if reading_dates:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        today_str = today.isoformat()
        yesterday_str = yesterday.isoformat()
        
        # Check if read today or yesterday
        if today_str in reading_dates or yesterday_str in reading_dates:
            current_streak = 1
            
            # Count backwards to find streak
            check_date = yesterday
            while True:
                check_date_str = check_date.isoformat()
                if check_date_str in reading_dates:
                    current_streak += 1
                    check_date -= datetime.timedelta(days=1)
                else:
                    break
    
    # Calculate average verses per session
    cursor.execute(
        """
        SELECT COUNT(*), COUNT(DISTINCT substr(date_read, 1, 10))
        FROM reading_history
        """
    )
    total_verses, total_days = cursor.fetchone()
    
    avg_verses_per_day = total_verses / max(total_days, 1)
    
    # Get most productive day
    cursor.execute(
        """
        SELECT substr(date_read, 1, 10) as read_date, COUNT(*) as verse_count
        FROM reading_history
        GROUP BY read_date
        ORDER BY verse_count DESC
        LIMIT 1
        """
    )
    result = cursor.fetchone()
    most_productive_day = result if result else ("No data", 0)
    
    conn.close()
    
    # Display statistics
    console.print(f"\n[bold green]Current Streak:[/bold green] [bold]{current_streak}[/bold] days")
    console.print(f"[bold green]Total Verses Read:[/bold green] [bold]{total_verses}[/bold]")
    console.print(f"[bold green]Average Daily Reading:[/bold green] [bold]{avg_verses_per_day:.1f}[/bold] verses")
    console.print(f"[bold green]Most Productive Day:[/bold green] [bold]{most_productive_day[0]}[/bold] with [bold]{most_productive_day[1]}[/bold] verses")
    
    # Display recent reading history
    if reading_history:
        console.print("\n[bold]Recent Reading History:[/bold]")
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("Date", style="cyan")
        table.add_column("Passage", style="green")
        
        # Group by date
        reading_by_date = {}
        for book, chapter, verse, date_read in reading_history:
            date_str = date_read.split("T")[0] if "T" in date_read else date_read.split()[0]
            passage = f"{book} {chapter}:{verse}"
            
            if date_str not in reading_by_date:
                reading_by_date[date_str] = []
            
            reading_by_date[date_str].append(passage)
        
        # Add to table
        for date_str, passages in sorted(reading_by_date.items(), reverse=True):
            # Format date
            try:
                date_obj = datetime.datetime.fromisoformat(date_str)
                formatted_date = date_obj.strftime("%b %d, %Y")
            except ValueError:
                formatted_date = date_str
            
            # Show the range of passages
            if len(passages) > 1:
                first_passage = passages[0]
                last_passage = passages[-1]
                table.add_row(formatted_date, f"{first_passage} → {last_passage} ({len(passages)} verses)")
            else:
                table.add_row(formatted_date, passages[0])
        
        console.print(table)
    else:
        console.print("\n[yellow]No reading history recorded yet.[/yellow]")
    
    # Wait for user to press Enter
    console.input("\nPress Enter to return to the dashboard...")

def main():
    """Main application loop."""
    # Check for database in home directory and migrate if needed
    migrate_database()
    
    # Initialize database if needed
    init_db()
    
    while True:
        display_dashboard()
        
        choice = console.input("\n[bold]Enter command (u/r/d/e/b/s/x/q):[/bold] ").strip().lower()
        
        if choice == 'u':
            update_reading_progress()
        elif choice == 'r':
            jump_to_position()
        elif choice == 'd':
            download_bible_content()
        elif choice == 'e':
            export_bible_menu()
        elif choice == 'b':
            read_downloaded_book()
        elif choice == 's':
            view_statistics()
        elif choice == 'x':
            reset_reading_progress()
        elif choice == 'q':
            console.print("[yellow]Goodbye![/yellow]")
            break
        else:
            console.print("[red]Invalid command.[/red]")
            console.input("Press Enter to continue...")

if __name__ == "__main__":
    main()