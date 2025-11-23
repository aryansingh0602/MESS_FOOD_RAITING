#!/usr/bin/env python3
"""
Simple Mess Food Rating System
Author: <Your Name>
Date: 2025-11-24
"""

import csv
import os
from datetime import datetime, date

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "ratings.csv")


def ensure_data_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "date", "student", "dish", "rating", "comment"])


def add_rating(student: str, dish: str, rating: int, comment: str = ""):
    ensure_data_file()
    ts = datetime.now().isoformat(timespec="seconds")
    row = [ts, date.today().isoformat(), student.strip(), dish.strip(), str(int(rating)), comment.strip()]
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)
    print("Saved rating.")


def load_ratings():
    ensure_data_file()
    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                r["rating"] = int(r["rating"])
            except Exception:
                r["rating"] = None
            rows.append(r)
    return rows


def stats_overall(ratings):
    if not ratings:
        return {"count": 0, "avg": None}
    vals = [r["rating"] for r in ratings if isinstance(r["rating"], int)]
    if not vals:
        return {"count": len(ratings), "avg": None}
    return {"count": len(vals), "avg": sum(vals) / len(vals)}


def stats_per_dish(ratings):
    per = {}
    for r in ratings:
        dish = r["dish"] or "UNKNOWN"
        if dish not in per:
            per[dish] = []
        if isinstance(r["rating"], int):
            per[dish].append(r["rating"])
    summary = {}
    for dish, vals in per.items():
        summary[dish] = {"count": len(vals), "avg": (sum(vals) / len(vals)) if vals else None}
    return summary


def show_menu():
    print("\n=== MESS FOOD RATING ===")
    print("1. Add rating")
    print("2. Show overall stats")
    print("3. Show stats per dish")
    print("4. Export weekly summary")
    print("5. Exit")


def input_rating_flow():
    student = input("Your name / roll: ").strip()
    dish = input("Dish name (e.g., Dal, Roti, Paneer): ").strip()
    while True:
        raw = input("Rating (1-5): ").strip()
        try:
            rating = int(raw)
            if 1 <= rating <= 5:
                break
            else:
                print("Enter a number 1 to 5.")
        except ValueError:
            print("Enter a valid integer.")
    comment = input("Optional short comment (press enter to skip): ").strip()
    add_rating(student, dish, rating, comment)


def export_weekly_summary(outfile="weekly_summary.txt"):
    ratings = load_ratings()
    if not ratings:
        print("No ratings yet.")
        return
    today = date.today()
    week_ago = today.fromordinal(today.toordinal() - 6)
    recent = [r for r in ratings if r["date"] and date.fromisoformat(r["date"]) >= week_ago]
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(f"Weekly summary ({week_ago.isoformat()} to {today.isoformat()})\n\n")
        overall = stats_overall(recent)
        f.write(f"Total ratings in week: {overall['count']}\n")
        f.write(f"Average rating (week): {overall['avg'] if overall['avg'] is not None else 'N/A'}\n\n")
        f.write("Per-dish averages:\n")
        per = stats_per_dish(recent)
        for dish, s in sorted(per.items(), key=lambda x: (x[1]['avg'] or 0), reverse=True):
            f.write(f"- {dish}: count={s['count']}, avg={s['avg'] if s['avg'] is not None else 'N/A'}\n")
    print("Exported weekly summary to", outfile)


def main():
    ensure_data_file()
    while True:
        show_menu()
        choice = input("Choose: ").strip()
        if choice == "1":
            input_rating_flow()
        elif choice == "2":
            ratings = load_ratings()
            s = stats_overall(ratings)
            print(f"Total entries: {s['count']}")
            print(f"Average rating: {s['avg'] if s['avg'] is not None else 'N/A'}")
        elif choice == "3":
            ratings = load_ratings()
            per = stats_per_dish(ratings)
            print("\nStats per dish:")
            for dish, st in sorted(per.items(), key=lambda x: (x[1]['avg'] or 0), reverse=True):
                print(f"- {dish}: count={st['count']}, avg={st['avg'] if st['avg'] is not None else 'N/A'}")
        elif choice == "4":
            export_weekly_summary()
        elif choice == "5":
            print("Bye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
