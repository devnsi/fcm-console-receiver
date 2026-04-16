#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "colorama",
#   "firebase-admin",
#   "python-dotenv",
#   "rich",
#   "typer",
# ]
# ///
import json
import random
from pathlib import Path
from typing import Annotated

import firebase_admin
import typer
from colorama import Fore, Style, init
from dotenv import load_dotenv
from firebase_admin import credentials, messaging
from rich import print_json

init(autoreset=True)
load_dotenv()
app = typer.Typer()

Topics = Annotated[list[str], typer.Option(
    "--topic",
    help="Topic to send to. Can be used multiple times.",
    envvar="FCM_TOPICS",
    callback=lambda x: sorted(set(t.strip() for item in x for t in item.split(",") if t.strip())),
    show_default=False,
    min=1
)]
secretsPathDefault = Path(__file__).parent / "secret.json"
SecretsPath = Annotated[str, typer.Option(
    "--secrets-path",
    help="Path to the secret JSON file.",
    exists=True,
    file_okay=True,
    dir_okay=False,
    resolve_path=True,
    callback=lambda v: v if Path(v).exists() else exec('raise typer.BadParameter("file missing")'),
    envvar="FCM_SECRET_PATH",
)]


def write(message: str, topic: str = "status"):
    print(f"{Fore.LIGHTBLACK_EX}[{topic}]{Style.RESET_ALL} {message}")


@app.command()
def send_topic_message(topics: Topics,
                       secret_path: SecretsPath = secretsPathDefault,
                       debug: bool = False,
                       dry_run: bool = False):
    # Initialize client.
    write(f"{Fore.MAGENTA}initializing sender...{Fore.RESET}")
    cred = credentials.Certificate(secret_path)
    firebase = firebase_admin.initialize_app(cred)

    # Construct message.
    message = messaging.Message(
        topic="._.",  # just as a placeholder.
        notification=messaging.Notification(
            title="Pizza Delivery",
            body=f"Your pizza is {random.randint(1, 120)} minutes out.",
        ),
        data={
            "toppings": ",".join(["cheese", "more cheese", "pigsblood"]),
            "request": "write an joke on the box",
        },
    )
    if debug:
        message_json = json.dumps(json.loads(str(message)), indent=4)
        write(f"{Fore.YELLOW}Message{Fore.RESET} |")
        print_json(message_json)

    # Send message for distribution.
    write(f"{Fore.MAGENTA}sending messages to {Style.BRIGHT}{len(topics)}{Style.NORMAL} topics...{Fore.RESET}")
    for topic in topics:
        message.topic = topic
        try:
            response = messaging.send(message, dry_run, firebase)
            write(f"{Style.BRIGHT}{response}{Style.NORMAL}", topic)
        except Exception as e:
            write(f"error sending message: {Fore.RED}{e}{Fore.RESET}", topic)
    write(f"{Fore.MAGENTA}derezzing...{Fore.RESET}")


if __name__ == "__main__":
    app()
