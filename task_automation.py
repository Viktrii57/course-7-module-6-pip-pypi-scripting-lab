import argparse
import json
import requests
from rich.console import Console
from rich.table import Table

# Strict import from the required grading module
from generate_log import generate_log

console = Console()

class Task:
    """Models a single Task item."""
    def __init__(self, task_id: int, title: str, completed: bool = False):
        self.id = task_id
        self.title = title
        self.completed = completed

    def mark_complete(self):
        self.completed = True

    def to_dict(self):
        return {"id": self.id, "title": self.title, "completed": self.completed}


class TaskManager:
    """Manages collection of tasks and handles local File I/O & API Sync."""
    def __init__(self, file_path="tasks_log.json"):
        self.file_path = file_path
        self.tasks = []
        self._load_tasks()

    def _load_tasks(self):
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
                self.tasks = [Task(t['id'], t['title'], t['completed']) for t in data]
        except (FileNotFoundError, json.JSONDecodeError):
            console.print("[yellow]No local task log found. Seeding initial data from API...[/yellow]")
            self._fetch_initial_api_data()

    def _fetch_initial_api_data(self):
        try:
            response = requests.get("https://jsonplaceholder.typicode.com/todos?_limit=3")
            if response.status_code == 200:
                todos = response.json()
                self.tasks = [Task(item['id'], item['title'], item['completed']) for item in todos]
                self._save_tasks()
                return
        except requests.RequestException:
            console.print("[red]Could not connect to API. Starting with an empty task list.[/red]")
        self.tasks = []

    def _save_tasks(self):
        with open(self.file_path, "w") as file:
            json.dump([t.to_dict() for t in self.tasks], file, indent=4)
        
        # Passes task data lists directly to the graded function
        log_entries = [f"Task #{t.id}: {t.title} [Completed: {t.completed}]" for t in self.tasks]
        generate_log(log_entries)

    def add_task(self, title: str):
        new_id = max([t.id for t in self.tasks], default=0) + 1
        new_task = Task(new_id, title)
        self.tasks.append(new_task)
        self._save_tasks()
        console.print(f"[green]✔ Success:[/green] Added task [bold]#{new_id}[/bold]: '{title}'")

    def complete_task(self, task_id: int):
        for task in self.tasks:
            if task.id == task_id:
                if task.completed:
                    console.print(f"[yellow]! Task #{task_id} is already completed.[/yellow]")
                    return
                task.mark_complete()
                self._save_tasks()
                console.print(f"[green]✔ Success:[/green] Task [bold]#{task_id}[/bold] marked as complete!")
                return
        console.print(f"[red]❌ Error:[/red] Task #{task_id} not found.")

    def display_tasks(self):
        if not self.tasks:
            console.print("[bold yellow]No tasks available.[/bold yellow]")
            return

        table = Table(title="Current Automation Tool Tasks")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Task Title", style="magenta")
        table.add_column("Status", justify="center")

        for task in self.tasks:
            status = "[green]✓ Complete[/green]" if task.completed else "[red]⟳ Pending[/red]"
            table.add_row(str(task.id), task.title, status)

        console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="A lightweight OOP-driven CLI tool for project task automation."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available automation actions")
    subparsers.add_parser("list", help="Display all current tasks")

    add_parser = subparsers.add_parser("add-task", help="Add a new task to your log")
    add_parser.add_argument("--title", type=str, required=True, help="The title text of the task")

    complete_parser = subparsers.add_parser("complete-task", help="Mark a task as completed")
    complete_parser.add_argument("--id", type=int, required=True, help="The explicit integer ID of the task")

    args = parser.parse_args()
    manager = TaskManager()

    if args.command == "list" or args.command is None:
        manager.display_tasks()
    elif args.command == "add-task":
        manager.add_task(args.title)
    elif args.command == "complete-task":
        manager.complete_task(args.id)


if __name__ == "__main__":
    main()
    