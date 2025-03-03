import requests

from bs4 import BeautifulSoup

import re



def get_scripture(book: str, chapter: int, verse: int):

    # Generate the correct book code based on book order

    book_order = {

        "genesis": 1, "exodus": 2, "leviticus": 3, "numbers": 4, "deuteronomy": 5,

        "joshua": 6, "judges": 7, "ruth": 8, "1 samuel": 9, "2 samuel": 10,

        "1 kings": 11, "2 kings": 12, "1 chronicles": 13, "2 chronicles": 14,

        "ezra": 15, "nehemiah": 16, "esther": 17, "job": 18, "psalms": 19,

        "proverbs": 20, "ecclesiastes": 21, "song of solomon": 22, "isaiah": 23,

        "jeremiah": 24, "lamentations": 25, "ezekiel": 26, "daniel": 27,

        "hosea": 28, "joel": 29, "amos": 30, "obadiah": 31, "jonah": 32,

        "micah": 33, "nahum": 34, "habakkuk": 35, "zephaniah": 36, "haggai": 37,

        "zechariah": 38, "malachi": 39, "matthew": 40, "mark": 41, "luke": 42,

        "john": 43, "acts": 44, "romans": 45, "1 corinthians": 46, "2 corinthians": 47,

        "galatians": 48, "ephesians": 49, "philippians": 50, "colossians": 51,

        "1 thessalonians": 52, "2 thessalonians": 53, "1 timothy": 54, "2 timothy": 55,

        "titus": 56, "philemon": 57, "hebrews": 58, "james": 59, "1 peter": 60,

        "2 peter": 61, "1 john": 62, "2 john": 63, "3 john": 64, "jude": 65,

        "revelation": 66

    }

    

    book_number = book_order.get(book.lower())

    if not book_number:

        print("Book not found in predefined list.")

        return

    

    # Correct formatting for sequence ID

    book_code = f"{book_number}"

    chapter_code = f"{chapter:03}"

    verse_code = f"{verse:03}"

    verse_id = f"v{book_code}{chapter_code}{verse_code}"

    

    print(f"DEBUG: Searching for verse ID: {verse_id}")  # Debug output

    

    formatted_book = book.lower().replace(' ', '-')

    if formatted_book[0].isdigit():

        formatted_book = formatted_book.replace(' ', '-', 1)

    url = f"https://www.jw.org/en/library/bible/nwt/books/{formatted_book}/{chapter}/"

    

    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)

    

    if response.status_code != 200:

        print("Failed to retrieve page.")

        return

    

    soup = BeautifulSoup(response.text, "html.parser")

    

    # Locate the verse container by its unique ID

    verse_container = soup.find("span", id=verse_id)

    if verse_container:

        # Remove the verse number (inside <sup class="verseNum">)

        verse_sup = verse_container.find("sup", class_="verseNum")

        if verse_sup:

            verse_sup.decompose()

        

        # Extract the cleaned verse text

        verse_text = verse_container.get_text(separator=" ", strip=True)

        verse_text = re.sub(r'^\d+ ', '', verse_text)  # Remove leading chapter numbers if present

        verse_text = re.sub(r'\s*[\*\+]\s*', ' ', verse_text).strip()

        

        print(f"{book.capitalize()} {chapter}:{verse} -", verse_text)

        return
