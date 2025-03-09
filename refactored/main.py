"""
Bible Tracker - Main Application

A console application to track Bible reading progress
"""

import db
import ui

def main():
    """Main application loop."""
    # Initialize database if needed
    db.init_db()
    
    while True:
        ui.display_dashboard()
        
        choice = ui.console.input("\n[bold]Enter command (u/r/e/b/s/x/q):[/bold] ").strip().lower()
        
        if choice == 'u':
            ui.update_reading_progress()
        elif choice == 'r':
            ui.jump_to_position()
        elif choice == 'e':
            ui.export_bible_menu()
        elif choice == 'b':
            ui.read_bible_book()
        elif choice == 's':
            ui.view_statistics()
        elif choice == 'x':
            ui.reset_reading_progress()
        elif choice == 'q':
            ui.console.print("[yellow]Goodbye![/yellow]")
            break
        else:
            ui.console.print("[red]Invalid command.[/red]")
            ui.console.input("Press Enter to continue...")

if __name__ == "__main__":
    main()
