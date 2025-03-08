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

### Complete Offline Bible
- **Pre-loaded Bible Content**: The application comes with all 66 books of the Bible pre-loaded in the database for immediate offline use.
- **Zero-Download Operation**: No internet connection required - all Bible content is included in the database file.
- **Verse Display**: View the text of your current verse directly in the app.
- **Reading Mode**: Read Bible books in a clean, distraction-free interface with easy navigation between chapters.
- **Export to JSON**: Export Bible content to JSON format for use in other applications.

### Statistics and Analysis
- **Reading Stats**: View your current reading streak, total verses read, and average reading pace.
- **Completion Estimates**: See estimates of how long it will take to finish your current book and the entire Bible based on your reading history.
- **Reading History**: Track which days you read and how many verses you covered.

## Requirements

- Python 3.7 or higher
- No internet connection required (all Bible content is included offline)
- Libraries: requests, beautifulsoup4, rich
- A modern terminal with good Unicode and color support (see Terminal Compatibility section)

**Important Note**: This application has been designed and tested for desktop/laptop computers only. It has not been tested on mobile devices or tablets and may not function correctly on these platforms. The terminal-based interface is optimized for computer use with physical keyboards.

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

5. **Run the application**
The application must be run from the root directory of the project where the `bible-tracker.py` file is located.

```bash
python bible-tracker.py
```

**Tip**: Most operating systems allow you to open a terminal directly in the project directory:
- **Windows**: Right-click in the folder and select "Open in Terminal" or "Open PowerShell window here"
- **macOS**: Right-click and select "New Terminal at Folder" (may require enabling in Finder preferences)
- **Linux**: Right-click and select "Open in Terminal" (varies by distribution)

**Important Note**: The repository includes a complete `bible_tracker.db` file with all 66 books of the Bible already pre-loaded for offline use. No internet connection is necessary for any operation.

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
| x | Reset reading progress (keeping Bible content) |
| d | Bible database information |
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

## Bible Content

The application comes with a complete Bible database containing all 66 books. There is no need to download any content as everything is pre-loaded:

- All Bible books are included in the database file
- All chapters and verses are available for offline reading
- The database structure is optimized for quick access and low resource usage
- You can export the content to JSON format if needed for other applications

If you need to restore the Bible database for any reason (corruption, accidental deletion), simply re-download the original `bible_tracker.db` file from the GitHub repository.

## Technical Details

### Database Structure
The app uses SQLite to store all data in a single file (`bible_tracker.db`) with these main tables:
- `books`: Information about all 66 books of the Bible
- `chapters`: Verse counts for each chapter
- `verses`: Bible text for all 66 books
- `reading_progress`: Your current reading position
- `reading_history`: Record of all verses you've read

### Components
1. **Database Management**: Functions for creating, updating, and querying the database
2. **User Interface**: Rich text-based interface with color coding and formatted tables
3. **Progress Calculation**: Functions for determining reading progress percentages
4. **Statistics Engine**: Code for analyzing reading patterns and estimating completion times

## Troubleshooting

### Terminal Display Issues
- **Broken Progress Bars**: If progress bars appear as strange characters, ensure your terminal supports Unicode block characters and is using a compatible font
- **Color Problems**: If colors don't display correctly, check that your terminal supports 256 colors or true color
- **Layout Issues**: If tables or panels look misaligned, try using a larger terminal window or reducing the text size

### Database Issues
- **Missing Database**: If the `bible_tracker.db` file is missing, the app will attempt to create a new structure. You should download a fresh copy of the database from the GitHub repository to ensure you have all Bible content.
- **Corrupted Database**: If you encounter database errors, try replacing the database file with a fresh copy from the GitHub repository.
- **Database Reset**: If you want to start fresh while keeping all Bible content, use the `x` command to reset your reading progress.

### Platform-Specific Issues
- **Windows**: The app works best on Windows Terminal. Traditional Command Prompt may have limited formatting support.
- **Linux**: If using WSL on Windows, consider running the program natively in Windows Terminal instead for better formatting.
- **macOS**: The default Terminal.app has limited support for some rich text formatting features. iTerm2 is strongly recommended for a better experience.

## Contributing

Contributions to improve the Bible Study Tracker are welcome! Here are some ways you can help:

- **Bug Reports**: File detailed issue reports on GitHub
- **Feature Ideas**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with bug fixes or new features
- **Documentation**: Help improve this README or add more detailed documentation

### Call for Code Restructuring

**Seeking Help with Modularization**: The current codebase would benefit greatly from being broken into smaller, more manageable modules. If you have experience with Python application architecture and would be interested in helping restructure the code into a more maintainable format, your contribution would be especially valuable. Ideal improvements would include:

- Separating the codebase into logical modules (database handling, UI, business logic)
- Implementing proper class structures
- Improving test coverage
- Enhancing maintainability while preserving functionality

If you're able to help with this refactoring effort, please reach out via GitHub issues or submit a pull request with your proposed changes.

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

- This application uses the New World Translation for verse content
- Bible structure data is based on the standard 66-book Protestant Bible canon
- Thanks to the developers of Rich, Requests, and BeautifulSoup libraries

## Disclaimer

This application is designed for personal Bible study and comes with a complete offline Bible database. The application and its creator are not affiliated with any Bible publishers or religious organizations. The Bible text is included for personal study purposes only.
