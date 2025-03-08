# Refactored Bible Study Tracker

## Overview
This is a modular, refactored version of the Bible Study Tracker with significant improvements to code structure, maintainability, and error handling. The original functionality has been preserved while preparing the codebase for future GUI implementation.


![refactor-tracker](https://github.com/user-attachments/assets/9b38c818-c53f-4b3a-8a38-fa53f43a0de6)


## ⚠️ TESTING PHASE ⚠️
**This refactored version is currently in testing. If you encounter any bugs, please report them as described below.**

## Key Improvements

### 1. Modular Architecture
The codebase has been reorganized into functional modules:
- `models.py` - Bible structure data and model-related functions
- `db.py` - Database operations and data access
- `tracker.py` - Reading progress tracking functionality
- `ui.py` - User interface components and screens
- `main.py` - Application entry point

### 2. Enhanced Error Handling
- Robust error handling throughout the codebase
- Graceful fallbacks for missing data
- Prevention of division by zero errors
- Better handling of database connectivity issues

### 3. Code Simplification
- Removed duplicate code
- Eliminated unused download/scraping functionality
- Streamlined database queries
- Improved function signatures and return types
- Type annotations for better code readability

### 4. Future-Ready
- Clear separation of UI and business logic
- Prepared for GUI implementation
- Consistent data access patterns
- Standardized error reporting

## How to Test

1. Clone the repository
   ```bash
   git clone https://github.com/sanoski/Bible-Study-Tracker.git
   cd Bible-Study-Tracker
   ```

2. Switch to the refactored code branch
   ```bash
   git checkout refactored-modular
   ```

3. Navigate to the refactored directory
   ```bash
   cd refactored
   ```

4. Run the application
   ```bash
   python main.py
   ```

## Reporting Bugs

If you encounter any issues while testing, please help improve this refactored version by reporting bugs:

1. Go to the [Issues](https://github.com/sanoski/Bible-Study-Tracker/issues) section of the repository
2. Click on "New Issue"
3. Select "Bug Report"
4. Provide the following information:
   - Clear, descriptive title
   - Steps to reproduce the bug
   - Expected behavior
   - Actual behavior
   - Screenshots (if applicable)
   - Your environment (OS, Python version)
   - Tag the issue with "refactored-version"

## Features

- Track your Bible reading progress
- View completion percentages for chapters, books, and the entire Bible
- Show reading statistics and streaks
- Navigate between verses and chapters
- Export Bible content to JSON
- Visualize completed chapters with a grid display
- Estimate completion times based on reading pace

## Future Plans

The modular structure of this refactored version lays the groundwork for:

- GUI implementation with various frameworks (Tkinter, PyQt, etc.)
- Mobile application development
- Web interface integration
- Enhanced visualization features
- Multilingual support
- Reading plans and schedules

## Contributing

Contributions to improve this refactored version are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the same terms as the original Bible Study Tracker.
