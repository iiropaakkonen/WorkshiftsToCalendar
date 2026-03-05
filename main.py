# main.py
from gmail_shifts import get_shifts
from workshifts_calendar import add_shifts_to_calendar

def main():
    print("Fetching shifts from Gmail...")
    shifts = get_shifts()
    print(f"Found {len(shifts)} upcoming shifts")

    print("Adding shifts to Google Calendar...")
    add_shifts_to_calendar(shifts)
    print("Done!")

if __name__ == "__main__":
    main()