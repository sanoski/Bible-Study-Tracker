# Bible Study Tracker

A command-line application for tracking your progress reading the New World Translation of the Bible. This tool helps you maintain consistent Bible reading habits by remembering your position, showing your progress, and providing detailed statistics about your reading journey.

![dashboard](https://github.com/user-attachments/assets/bff6eb6d-fde4-46ae-bea2-687132fdfad8)

## Features

### Core Functionality
- **Position Tracking**: Never lose your place in the Bible again. The app remembers exactly which book, chapter, and verse you're reading.
- **Progress Visualization**: See your progress through the current chapter, book, and the entire Bible with colorful progress bars.
- **Chapter Completion Grid**: Visual display showing which chapters you've completed in your current book.
- **Automatic Advancement**: When you mark a chapter complete, the app automatically advances to the next chapter.
- **Position Jumping**: Easily jump to any book, chapter, and verse in the Bible without losing your progress history.

### Content Features
- **Complete Offline Bible**: The database includes all 66 books of the Bible pre-downloaded for immediate offline use.
- **Verse Display**: View the text of your current verse directly in the app.
- **Reading Mode**: Read Bible books in a clean, distraction-free interface with easy navigation between chapters.
- **Export to JSON**: Export Bible content to JSON format for use in other applications.

### Statistics and Analysis
- **Reading Stats**: View your current reading streak, total verses read, and average reading pace.
- **Completion Estimates**: See estimates of how long it will take to finish your current book and the entire Bible based on your reading history.
- **Reading History**: Track which days you read and how many verses you covered.

## Requirements

- Python 3.7 or higher
- No internet connection required for normal use (all Bible content is included offline)
- Libraries: requests, beautifulsoup4, rich

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/bible-study-tracker.git
cd bible-study-tracker
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python bible-tracker.py
```

**Important Note**: The repository includes a complete `bible_tracker.db` file with all 66 books of the Bible already downloaded for offline use. No internet connection or downloading from JW.org is necessary for normal operation.

## Usage Guide

### Main Commands
Navigate the application using these single-key commands:

| Command | Description |
|---------|-------------|
| u | Update your reading progress |
| r | Jump to a different book/chapter/verse |
| b | Read Bible books |
| e | Export Bible content to JSON |
| s | View your reading statistics |
| x | Reset reading progress (keeping downloaded content) |
| d | Download Bible content (only needed if database is corrupted) |
| q | Quit the application |

### Tracking Your Reading

#### Mark a Chapter Complete
1. Press `u` to update your progress
2. Select option 1 to mark the current chapter as complete
3. The app will automatically advance to the next chapter

#### Mark a Specific Verse
1. Press `u` to update your progress
2. Select option 2 to mark a specific verse
3. Enter the verse number where you stopped reading

### Reading the Bible

#### Read a Book
1. Press `b` to access the Bible reader
2. Select a book from the list
3. Enter a chapter number to start reading
4. Use the navigation commands (`n` for next chapter, `p` for previous chapter) to move through the book

### Exporting Bible Content
1. Press `e` to access the export menu
2. Choose to export all books or a specific book
3. Select a format (nested or flat JSON)
4. Enter an output filename
5. The app will create a JSON file with the selected Bible content

## Downloading Bible Content (Rarely Needed)

**Important**: The application comes with a complete Bible database. The download functionality should only be used in exceptional circumstances such as:
- If the database file becomes corrupted
- If the GitHub repository is unavailable and you need to recreate the database

To respect JW.org's resources, please use the included database rather than re-downloading Bible content unnecessarily.

If you must download content:
1. Press `d` to access the download menu
2. Choose option 1 to download a specific book or option 2 to download your current book
3. The app will download all verses in the book and store them in the database

## Technical Details

### Database Structure
The app uses SQLite to store all data in a single file (`bible_tracker.db`) with these main tables:
- `books`: Information about all 66 books of the Bible
- `chapters`: Verse counts for each chapter
- `verses`: Bible text for all 66 books
- `reading_progress`: Your current reading position
- `reading_history`: Record of all verses you've read

### Components
1. **Bible Scraper**: The `bible_scraper_v2.py` module handles fetching verse content from JW.org (rarely needed)
2. **Database Management**: Functions for creating, updating, and querying the database
3. **User Interface**: Rich text-based interface with color coding and formatted tables
4. **Progress Calculation**: Functions for determining reading progress percentages
5. **Statistics Engine**: Code for analyzing reading patterns and estimating completion times

## Troubleshooting

### Database Issues
- **Missing Database**: If the `bible_tracker.db` file is missing, the app will create a new one. However, you'll need to either download the books or restore the database from GitHub.
- **Corrupted Database**: If you encounter database errors, try replacing the database file with a fresh copy from the GitHub repository.
- **Database Reset**: If you want to start fresh while keeping all Bible content, use the `x` command to reset your reading progress.

### Reading and Navigation
- **Display Issues**: If the formatted display doesn't look right, make sure your terminal supports the Rich library's formatting.

## Respecting JW.org Resources

This application is designed to minimize the need for accessing JW.org for Bible content. To be respectful:

1. **Use the included database** rather than re-downloading content from JW.org
2. Only use the download functionality if absolutely necessary
3. If you need to download content, space out your requests (the app already includes delays between requests)
4. Do not modify the code to remove these built-in rate limits

## Contributing

Contributions to improve the Bible Study Tracker are welcome! Here are some ways you can help:

- **Bug Reports**: File detailed issue reports on GitHub
- **Feature Ideas**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with bug fixes or new features
- **Documentation**: Help improve this README or add more detailed documentation

## Technical Roadmap / Future Improvements

Potential enhancements for future versions:
- Daily reading reminders and notifications
- Multiple reading profiles for different users
- Reading plans (chronological, thematic, etc.)
- Verse search functionality
- Verse highlighting and note-taking
- Mobile application version

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This application uses the New World Translation from JW.org for verse content
- Bible structure data is based on the standard 66-book Protestant Bible canon
- Thanks to the developers of Rich, Requests, and BeautifulSoup libraries

## Disclaimer

This application is designed for personal Bible study and comes with a complete offline Bible database. The application and its creator are not affiliated with the Watch Tower Bible and Tract Society or JW.org. The Bible text has been retrieved from publicly accessible web pages for personal study purposes.
