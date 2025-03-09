"""
User interface functions for the Bible tracker
"""

import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import tracker

# Initialize rich console for pretty display
console = Console()

def clear_screen():
    """Clear the console screen"""
    console.clear()

def display_dashboard():
    """Display the main dashboard."""
    clear_screen()
    console.print(Panel.fit("[bold blue]Bible Study Tracker v2.0[/bold blue]", box=box.DOUBLE))    
    # Get current progress
    book, chapter, verse = tracker.get_current_position()
    console.print(f"\n[bold green]Current Position:[/bold green] {book} {chapter}:{verse}")
    
    # Display verse content
    console.print("\n[bold yellow]Current Verse:[/bold yellow]")
    verse_text = tracker.get_verse_content(book, chapter, verse)
    console.print(f"{book} {chapter}:{verse} - {verse_text}")
    
    # Display next verse
    next_book, next_chapter, next_verse = tracker.get_next_verse()
    console.print(f"\n[bold cyan]Next Verse:[/bold cyan] {next_book} {next_chapter}:{next_verse}")
    
    # Generate JW.org link for compatibility
    formatted_book = next_book.lower().replace(' ', '-')
    if formatted_book[0].isdigit():
        formatted_book = formatted_book.replace(' ', '-', 1)
    jw_link = f"https://www.jw.org/en/library/bible/nwt/books/{formatted_book}/{next_chapter}/"
    console.print(f"[link={jw_link}]Continue reading on JW.org[/link]")
    
    # Show completion percentages
    percentages = tracker.get_progress_percentages()
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
    estimates = tracker.get_completion_estimates()
    console.print("\n[bold green]Estimated Completion Times:[/bold green]")
    console.print(f"Current Book: [bold]{estimates['book']}[/bold] days")
    console.print(f"Entire Bible: [bold]{estimates['bible']}[/bold] days")
    
    # Display completed chapters for current book
    display_chapter_grid(book)
    
    # Display completed books
    completed_books = tracker.get_completed_books()
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
    
    # Show commands
    console.print("\n[bold]Commands:[/bold]")
    console.print("  [cyan]u[/cyan] - Update reading progress")
    console.print("  [cyan]r[/cyan] - Go to a different book/chapter/verse")
    console.print("  [cyan]e[/cyan] - Export Bible to JSON")
    console.print("  [cyan]b[/cyan] - Read Bible books")
    console.print("  [cyan]s[/cyan] - View statistics")
    console.print("  [cyan]v[/cyan] - View version information")
    console.print("  [cyan]x[/cyan] - Reset reading progress")

    console.print("  [cyan]q[/cyan] - Quit")

def display_version_info():
    """Display version information."""
    clear_screen()
    console.print(Panel.fit("[bold blue]Bible Study Tracker[/bold blue]", box=box.DOUBLE))
    console.print("\n[bold cyan]Version:[/bold cyan] 2.0")
    console.print("\n[bold cyan]Release Date:[/bold cyan] March 2025")
    console.print("\n[bold cyan]Author:[/bold cyan] Sanoski")
    console.print("\n[bold cyan]GitHub:[/bold cyan] https://github.com/sanoski/Bible-Study-Tracker")
    console.print("\n[bold cyan]Changes in this version:[/bold cyan]")
    console.print("  • Complete code refactoring into modular architecture")
    console.print("  • Fixed database tracking issues")
    console.print("  • Improved reading statistics")
    console.print("  • Removed unnecessary dependencies")
    console.print("  • Performance improvements")
    
    console.input("\nPress Enter to return to the dashboard...")

def display_chapter_grid(book):
    """Display a grid of chapters showing which ones are completed."""
    console.print(f"\n[bold cyan]Chapter Completion in {book}:[/bold cyan]")
    
    # Get chapters with completion status
    chapters = tracker.get_book_chapters(book)
    if not chapters:
        console.print("[yellow]No chapter data found for this book.[/yellow]")
        return
    
    # Create a visual chapter grid
    chapter_grid = Table.grid(padding=1)
    
    # Determine number of columns based on total chapters
    cols = min(10, len(chapters))  # Max 10 columns
    
    # Create rows for the grid
    rows = []
    current_row = []
    
    for chap_num in sorted(chapters.keys()):
        if chapters[chap_num]:  # If chapter is completed
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

def update_reading_progress():
    """Handle updating reading progress."""
    # Get current progress first
    book, chapter, verse = tracker.get_current_position()
    
    clear_screen()
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
        success = tracker.mark_chapter_complete(book, chapter)
        
        if success:
            # Get the new position after update
            new_book, new_chapter, _ = tracker.get_current_position()
            
            if new_book != book or new_chapter != chapter:
                console.print(f"[green]✓ Chapter {book} {chapter} marked as complete![/green]")
                console.print(f"[green]→ Advanced to {new_book} {new_chapter}:1[/green]")
            else:
                console.print(f"[green]✓ Chapter {book} {chapter} marked as complete![/green]")
        else:
            console.print("[red]Error updating progress.[/red]")
    
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
        
        success = tracker.update_reading_position(book, chapter, int(new_verse))
        if success:
            console.print(f"[green]✓ Progress updated to {book} {chapter}:{new_verse}![/green]")
        else:
            console.print("[red]Error updating progress.[/red]")
    
    elif choice == "3":
        console.print("[yellow]Update canceled.[/yellow]")
    
    else:
        console.print("[red]Invalid choice.[/red]")
    
    # Wait for user to press Enter
    console.input("\nPress Enter to return to the dashboard...")

def jump_to_position():
    """Jump to a different reading position."""
    clear_screen()
    console.print(Panel.fit("[bold blue]Jump to Position[/bold blue]", box=box.SIMPLE))
    
    # Get current progress
    current_book, current_chapter, current_verse = tracker.get_current_position()
    console.print(f"\n[bold yellow]Current Position:[/bold yellow] {current_book} {current_chapter}:{current_verse}")
    
    # List all books
    console.print("\n[bold cyan]Available Books:[/bold cyan]")
    
    all_books = tracker.get_all_books()
    
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
    import db  # Local import to avoid circular import
    book_id = db.get_book_id(new_book)
    for book in db.BIBLE_BOOKS:
        if book["id"] == book_id:
            total_chapters = book["chapters"]
            break
    
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
    total_verses = db.get_total_verses(book_id, new_chapter)
    
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
    
    # Update progress
    success = tracker.update_reading_position(new_book, new_chapter, new_verse)
    if success:
        console.print(f"[bold green]✓ Position updated to {new_book} {new_chapter}:{new_verse}![/bold green]")
    else:
        console.print("[red]Error updating position.[/red]")
    
    # Wait for user to press Enter
    console.input("\nPress Enter to return to the dashboard...")

def export_bible_menu():
    """Menu for exporting Bible content to JSON."""
    clear_screen()
    console.print(Panel.fit("[bold blue]Export Bible to JSON[/bold blue]", box=box.SIMPLE))
    
    console.print("\n[bold]Export Options:[/bold]")
    console.print("1. Export all books")
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
        
        success = tracker.export_bible(filename, format_type)
        if success:
            console.print(f"[bold green]✓ Bible data exported to {filename}[/bold green]")
        else:
            console.print("[red]Error exporting Bible data.[/red]")
    
    elif choice == "2":
        book_name = console.input("\n[bold]Enter the name of the book to export:[/bold] ").strip()
        
        # Find closest match
        all_books = tracker.get_all_books()
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
            else:
                console.print(f"[red]Book '{book_name}' not found.[/red]")
                console.input("\nPress Enter to return to the dashboard...")
                return
        
        format_choice = console.input("\n[bold]Choose format ([n]ested or [f]lat):[/bold] ").strip().lower()
        format_type = "nested" if format_choice.startswith("n") else "flat"
        
        filename = console.input(f"\n[bold]Enter output filename (default: {book_name.lower()}_export.json):[/bold] ").strip()
        if not filename:
            filename = f"{book_name.lower()}_export.json"
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        success = tracker.export_bible(filename, format_type, book_name)
        if success:
            console.print(f"[bold green]✓ Book {book_name} exported to {filename}[/bold green]")
        else:
            console.print("[red]Error exporting book data.[/red]")
    
    elif choice != "3":
        console.print("[red]Invalid choice.[/red]")
    
    # Wait for user to press Enter
    console.input("\nPress Enter to return to the dashboard...")

def read_bible_book():
    """Read a Bible book in a nice interface."""
    while True:  # Outer loop for book selection
        clear_screen()
        console.print(Panel.fit("[bold blue]Read Bible[/bold blue]", box=box.SIMPLE))
        
        # Get all books
        all_books = tracker.get_all_books()
        
        console.print("\n[bold]Select a book to read:[/bold]")
        
        # Display books in a table
        book_table = Table(show_header=False, box=box.SIMPLE)
        cols = 4
        for _ in range(cols):
            book_table.add_column("", justify="left")
        
        # Fill the table with books
        rows = []
        row = []
        for i, book in enumerate(all_books):
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
        book_choice = console.input("\n[bold]Enter book number or name (or q to quit):[/bold] ").strip()
        
        if book_choice.lower() == 'q':
            return
            
        selected_book = None
        try:
            book_idx = int(book_choice) - 1
            if 0 <= book_idx < len(all_books):
                selected_book = all_books[book_idx]
        except ValueError:
            # Try to match by name
            for book in all_books:
                if book_choice.lower() in book.lower():
                    selected_book = book
                    break
        
        if not selected_book:
            console.print("[red]Invalid book selection.[/red]")
            console.input("\nPress Enter to try again...")
            continue  # Go back to book selection
        
        # Get book info
        import db  # Local import to avoid circular import
        book_id = db.get_book_id(selected_book)
        for book in db.BIBLE_BOOKS:
            if book["id"] == book_id:
                total_chapters = book["chapters"]
                break
        
        # Select chapter
        console.print(f"\n[bold]{selected_book} has {total_chapters} chapters.[/bold]")
        chapter_choice = console.input("\n[bold]Enter chapter number:[/bold] ").strip()
        
        try:
            chapter = int(chapter_choice)
            if chapter < 1 or chapter > total_chapters:
                console.print(f"[red]Chapter must be between 1 and {total_chapters}.[/red]")
                console.input("\nPress Enter to try again...")
                continue  # Go back to book selection
        except ValueError:
            console.print("[red]Invalid chapter number.[/red]")
            console.input("\nPress Enter to try again...")
            continue  # Go back to book selection
        
        # Get verses for this chapter
        verses = tracker.get_chapter_content(selected_book, chapter)
        
        if not verses:
            console.print(f"[yellow]No verses found for {selected_book} {chapter}.[/yellow]")
            console.input("\nPress Enter to try again...")
            continue  # Go back to book selection
        
        # Display the chapter
        chapter_loop = True
        while chapter_loop:
            clear_screen()
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
                    verses = tracker.get_chapter_content(selected_book, chapter)
                    
                    if not verses:
                        console.print(f"[yellow]No verses found for {selected_book} {chapter}.[/yellow]")
                        console.input("\nPress Enter to continue...")
                        chapter += 1  # Revert to previous chapter
                else:
                    console.print("[yellow]Already at the first chapter.[/yellow]")
                    console.input("\nPress Enter to continue...")
            
            elif nav_choice == 'n':
                if chapter < total_chapters:
                    chapter += 1
                    verses = tracker.get_chapter_content(selected_book, chapter)
                    
                    if not verses:
                        console.print(f"[yellow]No verses found for {selected_book} {chapter}.[/yellow]")
                        console.input("\nPress Enter to continue...")
                        chapter -= 1  # Revert to previous chapter
                else:
                    console.print("[yellow]Already at the last chapter.[/yellow]")
                    console.input("\nPress Enter to continue...")
            
            elif nav_choice == 'm':
                success = tracker.update_reading_position(selected_book, chapter, 1)
                if success:
                    console.print(f"[green]✓ Set {selected_book} {chapter}:1 as current reading position.[/green]")
                else:
                    console.print("[red]Error updating reading position.[/red]")
                console.input("\nPress Enter to continue...")
            
            elif nav_choice == 'b':
                chapter_loop = False  # Exit chapter loop but not function
            
            elif nav_choice == 'q':
                return  # Exit function completely
            
            else:
                console.print("[red]Invalid choice.[/red]")
                console.input("\nPress Enter to continue...")

def reset_reading_progress():
    """Reset all reading progress while keeping downloaded books."""
    clear_screen()
    console.print(Panel.fit("[bold red]Reset Reading Progress[/bold red]", box=box.DOUBLE))
    
    console.print("\n[bold yellow]Warning:[/bold yellow] This will reset all your reading progress and history.")
    console.print("You will be returned to Genesis 1:1.")
    
    confirm = console.input("\n[bold]Are you sure you want to reset your progress? (y/n):[/bold] ").strip().lower()
    
    if confirm == 'y' or confirm == 'yes':
        success = tracker.reset_progress()
        if success:
            console.print("\n[bold green]✓ Reading progress has been reset to Genesis 1:1[/bold green]")
        else:
            console.print("\n[bold red]Error resetting progress[/bold red]")
    else:
        console.print("\n[yellow]Reset cancelled.[/yellow]")
    
    console.input("\nPress Enter to return to the dashboard...")

def view_statistics():
    """Display detailed reading statistics."""
    clear_screen()
    console.print(Panel.fit("[bold blue]Reading Statistics[/bold blue]", box=box.SIMPLE))
    
    stats = tracker.get_reading_statistics()
    
    # Display statistics
    console.print(f"\n[bold green]Current Streak:[/bold green] [bold]{stats['streak']}[/bold] days")
    console.print(f"[bold green]Total Verses Read:[/bold green] [bold]{stats['total_verses']}[/bold]")
    console.print(f"[bold green]Average Daily Reading:[/bold green] [bold]{stats['avg_per_day']:.1f}[/bold] verses")
    console.print(f"[bold green]Most Productive Day:[/bold green] [bold]{stats['most_productive_day'][0]}[/bold] with [bold]{stats['most_productive_day'][1]}[/bold] verses")
    
    # Display recent reading history
    if stats['reading_by_date']:
        console.print("\n[bold]Recent Reading History:[/bold]")
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("Date", style="cyan")
        table.add_column("Chapters Read", style="green")
        
        # Add to table
        for date_str, passages in sorted(stats['reading_by_date'].items(), reverse=True):
            # Format date
            try:
                date_obj = datetime.datetime.fromisoformat(date_str)
                formatted_date = date_obj.strftime("%b %d, %Y")
            except ValueError:
                formatted_date = date_str
            
            # Group by book and chapter
            book_chapters = {}
            for passage in passages:
                parts = passage.split()
                book_name = " ".join(parts[:-1])  # Handle books with spaces like "1 Samuel"
                chapter_verse = parts[-1]
                chapter = int(chapter_verse.split(':')[0])
                
                if book_name not in book_chapters:
                    book_chapters[book_name] = set()
                book_chapters[book_name].add(chapter)
            
            # Format the reading activity
            activity_summary = []
            for book, chapters in book_chapters.items():
                chapters_list = sorted(list(chapters))
                
                # Find consecutive ranges
                if len(chapters_list) == 1:
                    activity_summary.append(f"{book} {chapters_list[0]}")
                else:
                    # Look for consecutive chapters
                    ranges = []
                    start = chapters_list[0]
                    prev = start
                    
                    for chapter in chapters_list[1:] + [None]:
                        if chapter is None or chapter != prev + 1:
                            if start == prev:
                                ranges.append(f"{start}")
                            else:
                                ranges.append(f"{start}-{prev}")
                            if chapter is not None:
                                start = chapter
                        prev = chapter if chapter is not None else prev
                    
                    activity_summary.append(f"{book} {', '.join(ranges)}")
            
            table.add_row(formatted_date, ", ".join(activity_summary))
        
        console.print(table)
    else:
        console.print("\n[yellow]No reading history recorded yet.[/yellow]")
    
    # Wait for user to press Enter
    console.input("\nPress Enter to return to the dashboard...")