"""
Reading progress tracking functionality
"""

import datetime
import math
from typing import Tuple, Dict, List
import db

def get_current_position() -> Tuple[str, int, int]:
    """Get the current reading position"""
    return db.get_current_progress()

def get_next_verse() -> Tuple[str, int, int]:
    """Get the next verse to read"""
    return db.get_next_verse()

def update_reading_position(book: str, chapter: int, verse: int, auto_advance=False) -> bool:
    """Update the current reading position"""
    return db.update_progress(book, chapter, verse, auto_advance)

def mark_chapter_complete(book: str, chapter: int) -> bool:
    """Mark a chapter as complete and advance to the next chapter"""
    # Get the total verses in this chapter
    book_id = db.get_book_id(book)
    if not book_id:
        return False
    
    total_verses = db.get_total_verses(book_id, chapter)
    
    # Mark as complete and auto-advance
    return db.update_progress(book, chapter, total_verses, auto_advance=True)

def reset_progress() -> bool:
    """Reset reading progress to Genesis 1:1"""
    return db.reset_reading_progress()

def get_progress_percentages() -> Dict[str, float]:
    """Calculate completion percentages"""
    return db.calculate_percentages()

def get_completion_estimates() -> Dict[str, int]:
    """Estimate days to complete current book and entire Bible"""
    return db.estimate_completion_times()

def get_verse_content(book: str, chapter: int, verse: int) -> str:
    """Get the content of a specific verse"""
    book_id = db.get_book_id(book)
    if not book_id:
        return "Book not found."
    
    return db.get_verse_text(book_id, chapter, verse)

def get_book_chapters(book_name: str) -> Dict[int, bool]:
    """Get all chapters for a book with completion status"""
    completed_chapters = db.get_completed_chapters(book_name)
    book_id = db.get_book_id(book_name)
    
    if not book_id:
        return {}
    
    # Get total chapters
    for book in db.BIBLE_BOOKS:
        if book["id"] == book_id:
            total_chapters = book["chapters"]
            break
    else:
        return {}
    
    # Create dictionary with completion status
    chapters = {}
    for chapter_num in range(1, total_chapters + 1):
        chapters[chapter_num] = chapter_num in completed_chapters
    
    return chapters

def get_completed_books() -> List[str]:
    """Get a list of completed books"""
    return db.get_books_read()

def get_reading_statistics() -> Dict:
    """Get reading statistics"""
    return db.get_reading_stats()

def get_all_books() -> List[str]:
    """Get all books in the Bible"""
    return db.get_all_books()

def get_chapter_content(book: str, chapter: int) -> List[Tuple[int, str]]:
    """Get all verses for a specific chapter"""
    book_id = db.get_book_id(book)
    if not book_id:
        return []
    
    return db.get_chapter_verses(book_id, chapter)

def export_bible(output_file="bible_export.json", format_type="nested", book_filter=None) -> bool:
    """Export Bible text to JSON"""
    return db.export_to_json(output_file, format_type, book_filter)
