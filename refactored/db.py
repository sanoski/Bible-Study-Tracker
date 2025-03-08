"""
Database operations for the Bible tracker
"""

import sqlite3
import datetime
import math
from typing import Tuple, List, Dict
from models import BIBLE_BOOKS

# Database path in the same directory as the program
DB_PATH = "bible_tracker.db"

def get_connection():
    """Get a connection to the database"""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize the database with Bible structure."""
    conn = get_connection()
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
    
    # Add verses table for text
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
        # Populate books table
        for book in BIBLE_BOOKS:
            cursor.execute(
                "INSERT INTO books (id, name, total_chapters, book_order) VALUES (?, ?, ?, ?)",
                (book["id"], book["name"], book["chapters"], book["id"])
            )
    
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
    conn = get_connection()
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

def get_book_id(book_name):
    """Get the ID of a book by name"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM books WHERE name = ?", (book_name,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    return None

def get_book_name(book_id):
    """Get the name of a book by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM books WHERE id = ?", (book_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    return None

def get_total_verses(book_id, chapter):
    """Get the total number of verses in a chapter"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT total_verses FROM chapters WHERE book_id = ? AND chapter_number = ?",
        (book_id, chapter)
    )
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    return 30  # Default if not found

def get_verse_text(book_id, chapter, verse):
    """Get the text of a verse"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT verse_text FROM verses WHERE book_id = ? AND chapter_number = ? AND verse_number = ?",
        (book_id, chapter, verse)
    )
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    return "Verse text not available."

def get_next_verse() -> Tuple[str, int, int]:
    """Get the next verse to read."""
    book, chapter, verse = get_current_progress()
    
    conn = get_connection()
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
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM books WHERE name = ?", (book,))
        result = cursor.fetchone()
        if not result:
            return False
        
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
        
        # Record the exact verse marked
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
        return True
    except Exception as e:
        print(f"Error updating progress: {e}")
        return False
    finally:
        conn.close()

def reset_reading_progress():
    """Reset all reading progress while keeping verses."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
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
        return True
    except Exception as e:
        print(f"Error resetting progress: {e}")
        return False
    finally:
        conn.close()

def export_to_json(output_file="bible_export.json", format_type="nested", book_filter=None):
    """Export Bible data to JSON file."""
    import json
    
    conn = get_connection()
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
    
    return True

def get_all_books():
    """Get all books in the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM books ORDER BY book_order")
    books = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return books

def get_completed_chapters(book_name):
    """Get a list of completed chapters for a specific book."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get book ID
    cursor.execute("SELECT id FROM books WHERE name = ?", (book_name,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return []
    
    book_id = result[0]
    
    # Query to find completed chapters
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

def get_books_read():
    """Get a list of completely read books based on reading history."""
    conn = get_connection()
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

def get_reading_stats():
    """Get reading statistics"""
    conn = get_connection()
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
    total_verses = total_verses or 0
    total_days = total_days or 1
    
    avg_verses_per_day = total_verses / total_days
    
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
    
    # Get reading by date
    reading_by_date = {}
    for book, chapter, verse, date_read in reading_history:
        date_str = date_read.split("T")[0] if "T" in date_read else date_read.split()[0]
        passage = f"{book} {chapter}:{verse}"
        
        if date_str not in reading_by_date:
            reading_by_date[date_str] = []
        
        reading_by_date[date_str].append(passage)
    
    conn.close()
    
    return {
        "streak": current_streak,
        "total_verses": total_verses,
        "avg_per_day": avg_verses_per_day,
        "most_productive_day": most_productive_day,
        "reading_by_date": reading_by_date
    }

def calculate_percentages():
    """Calculate completion percentages based on actual reading history."""
    book, chapter, verse = get_current_progress()
    
    conn = get_connection()
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

def estimate_completion_times():
    """Estimate days to complete current book and entire Bible."""
    book, chapter, verse = get_current_progress()
    
    conn = get_connection()
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
    
    # Calculate estimates based on reading history
    reading_rate = get_reading_rate()
    days_to_complete_book = math.ceil(remaining_verses_in_book / reading_rate) if reading_rate > 0 else 30
    days_to_complete_bible = math.ceil(remaining_verses_in_bible / reading_rate) if reading_rate > 0 else 365
    
    return {
        "book": days_to_complete_book,
        "bible": days_to_complete_bible
    }

def get_reading_rate():
    """Calculate the average verses read per day."""
    conn = get_connection()
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

def get_chapter_verses(book_id, chapter):
    """Get all verses for a specific chapter"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT verse_number, verse_text FROM verses WHERE book_id = ? AND chapter_number = ? ORDER BY verse_number",
        (book_id, chapter)
    )
    verses = cursor.fetchall()
    
    conn.close()
    return verses