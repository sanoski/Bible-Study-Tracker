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
- A modern terminal with good Unicode and color support (see Terminal Compatibility section)

## Terminal Compatibility

This application uses the `rich` library to create formatted text, tables, progress bars, and other visual elements in the terminal. For the best experience, use a terminal that fully supports rich text formatting:

### Recommended Terminals

#### Windows (Best Experience)
- **Windows Terminal** - Microsoft's modern terminal with full support for rich formatting
- **PowerShell 7 with Windows Terminal** - Ideal combination for the best display quality

#### macOS
- **iTerm2** - Much better than the default Terminal.app, with full support for colors and formatting
- **Alacritty** - A fast, cross-platform terminal emulator with good formatting support
- **Kitty** - Fast, feature-rich terminal that handles rich formatting well

#### Linux
Some formatting issues have been observed in certain Linux terminals. For the best experience on Linux, use:
- **Konsole** (KDE)
- **GNOME Terminal** with a compatible font
- **Alacritty**
- **Kitty**

### Terminal Configuration Tips
1. **Use a Nerd Font** - Install a font like Cascadia Code, Fira Code Nerd Font, or JetBrains Mono Nerd Font
2. **Enable 256 colors or true color (24-bit)** in your terminal
3. **Use a wide terminal window** (at least 100 columns) for proper table formatting
4. **Ensure UTF-8 encoding** is set for your terminal

If you experience display issues, particularly with progress bars or special characters, try adjusting these settings or switching to a different terminal emulator.

## Installation

1. **Prerequisites**
   - **Python**: Make sure Python 3.7 or higher is installed
     - [Download Python](https://www.python.org/downloads/) if not already installed
     - During installation, ensure "Add Python to PATH" is checked (Windows)
   - **Pip**: The Python package installer should come with Python
     - If you don't have pip, [install it following these instructions](https://pip.pypa.io/en/stable/installation/)
     - Verify installation with `pip --version` in your terminal

2. **Clone or download the repository**
```bash
git clone https://github.com/yourusername/bible-study-tracker.git
cd bible-study-tracker
```
   - Alternatively, download the ZIP file from GitHub and extract it to a folder

3. **Install dependencies**
The application requires the following Python libraries:
```bash
pip install requests beautifulsoup4 rich
```
Or use the requirements file:
```bash
pip install -r requirements.txt
```

4. **Terminal Setup (Optional but Recommended)**
   - **Windows**: Install [Windows Terminal](https://aka.ms/terminal) from the Microsoft Store
   - **macOS**: Install [iTerm2](https://iterm2.com/) for better formatting
   - **All Platforms**: Install a [Nerd Font](https://www.nerdfonts.com/) like Cascadia Code or JetBrains Mono

4. **Run the application**
The application must be run from the root directory of the project where the `bible-tracker.py` file is located.

```bash
python bible-tracker.py
```

**Tip**: Most operating systems allow you to open a terminal directly in the project directory:
- **Windows**: Right-click in the folder and select "Open in Terminal" or "Open PowerShell window here"
- **macOS**: Right-click and select "New Terminal at Folder" (may require enabling in Finder preferences)
- **Linux**: Right-click and select "Open in Terminal" (varies by distribution)

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

### Terminal Display Issues
- **Broken Progress Bars**: If progress bars appear as strange characters, ensure your terminal supports Unicode block characters and is using a compatible font
- **Color Problems**: If colors don't display correctly, check that your terminal supports 256 colors or true color
- **Layout Issues**: If tables or panels look misaligned, try using a larger terminal window or reducing the text size

### Database Issues
- **Missing Database**: If the `bible_tracker.db` file is missing, the app will create a new one. However, you'll need to either download the books or restore the database from GitHub.
- **Corrupted Database**: If you encounter database errors, try replacing the database file with a fresh copy from the GitHub repository.
- **Database Reset**: If you want to start fresh while keeping all Bible content, use the `x` command to reset your reading progress.

### Platform-Specific Issues
- **Windows**: The app works best on Windows Terminal. Traditional Command Prompt may have limited formatting support.
- **Linux**: If using WSL on Windows, consider running the program natively in Windows Terminal instead for better formatting.
- **macOS**: The default Terminal.app has limited support for some rich text formatting features. iTerm2 is strongly recommended for a better experience.

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
- Improved cross-platform terminal compatibility

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This application uses the New World Translation from JW.org for verse content
- Bible structure data is based on the standard 66-book Protestant Bible canon
- Thanks to the developers of Rich, Requests, and BeautifulSoup libraries

## Disclaimer

This application is designed for personal Bible study and comes with a complete offline Bible database. The application and its creator are not affiliated with the Watch Tower Bible and Tract Society or JW.org. The Bible text has been retrieved from publicly accessible web pages for personal study purposes.
