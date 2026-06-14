import argparse
from datetime import datetime
import os
import requests

# Put your verified generate_log function at the top level
def generate_log(data):
    if not isinstance(data, list):
        raise ValueError("Input data must be a list of log entries.")
    
    filename = f"log_{datetime.now().strftime('%Y%m%d')}.txt"
    
    with open(filename, "w") as file:
        for entry in data:
            file.write(f"{entry}\n")
            
    print(f"Log written to {filename}")


class TaskManager:
    """OOP Class to manage and track task operations."""
    def __init__(self):
        self.pending_tasks = []
        self.completed_tasks = []

    def add_task(self, description):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_entry = f"[{timestamp}] PENDING: {description}"
        self.pending_tasks.append(task_entry)
        print(f"✔ Added task: {description}")
        
        # Automatically generate/update log file
        all_logs = self.completed_tasks + self.pending_tasks
        generate_log(all_logs)

    def complete_task(self, keyword):
        moved = False
        still_pending = []
        
        for task in self.pending_tasks:
            if keyword.lower() in task.lower():
                completed_entry = task.replace("PENDING:", "COMPLETED:")
                self.completed_tasks.append(completed_entry)
                print(f"✔ Completed task matching keyword '{keyword}'")
                moved = True
            else:
                still_pending.append(task)
                
        if not moved:
            print(f"⚠ No pending task found matching keyword: '{keyword}'")
            
        self.pending_tasks = still_pending
        all_logs = self.completed_tasks + self.pending_tasks
        generate_log(all_logs)

    def fetch_api_task(self):
        """Uses third-party requests package to pull data."""
        print("Fetching data from external API...")
        try:
            response = requests.get("https://jsonplaceholder.typicode.com/posts/1", timeout=5)
            if response.status_code == 200:
                title = response.json().get("title", "External Task")
                self.add_task(f"API Sync - {title}")
            else:
                print("✖ Failed to fetch data from API.")
        except requests.RequestException as e:
            print(f"✖ API Connection Error: {e}")


def main():
    # Setup argparse CLI architecture
    parser = argparse.ArgumentParser(description="OOP Task Automation CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add-task command
    add_parser = subparsers.add_parser("add-task", help="Add a task")
    add_parser.add_argument("description", type=str, help="Task description text")

    # complete-task command
    complete_parser = subparsers.add_parser("complete-task", help="Complete a task")
    complete_parser.add_argument("keyword", type=str, help="Keyword to identify the task")

    # sync-api command
    subparsers.add_parser("sync-api", help="Fetch a task using requests from an external API")

    args = parser.parse_args()
    manager = TaskManager()

    # Wrap logic inside execution block
    if args.command == "add-task":
        manager.add_task(args.description)
    elif args.command == "complete-task":
        manager.complete_task(args.keyword)
    elif args.command == "sync-api":
        manager.fetch_api_task()
    else:
        parser.print_help()


# Strict execution safety barrier
if __name__ == "__main__":
    main()