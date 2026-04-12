#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "colorama",
#   "fcm-receiver",
#   "python-dotenv",
#   "typer",
# ]
# ///
import builtins
import json
import sys
import threading
import time
from typing import Annotated

import typer
from colorama import Fore, Style, init
from dotenv import load_dotenv
from fcm_receiver import FCMClient

init(autoreset=True)
load_dotenv()
app = typer.Typer()

ProjectId = Annotated[str, typer.Option(
    envvar="FCM_PROJECT_ID",
    prompt=True,
    help="Firebase Project ID.")]
ApiKey = Annotated[str, typer.Option(
    envvar="FCM_API_KEY",
    prompt=True,
    help="Firebase Web API Key for authentication."
)]
AppId = Annotated[str, typer.Option(
    envvar="FCM_APP_ID",
    prompt=True,
    help="Unique App ID for the registered client."
)]
Topics = Annotated[list[str], typer.Option(
    "--topic",
    help="Topic to subscribe to. Can be used multiple times.",
    envvar="FCM_TOPICS",
    default_factory=list,
    callback=lambda x: sorted(set(t.strip() for item in x for t in item.split(",") if t.strip())),
    show_default=False
)]


def redefine_print():
    print_lock = threading.Lock()
    print_actual = builtins.print

    def filtered_print(*args, **kwargs):
        msg = " ".join(map(str, args))
        to_ignore = ["[fcm_socket]", "[fcm_client]"]
        if any(msg.startswith(prefix) for prefix in to_ignore):
            return
        with print_lock:
            print_actual(*args, **kwargs)

    builtins.print = filtered_print


def handle_status(status: str, _: str = "") -> None:
    print(f"{Fore.LIGHTBLACK_EX}[status]{Style.RESET_ALL} {Fore.MAGENTA}{status}{Style.RESET_ALL}")


def handle_data(payload: bytes, _: str) -> None:
    # Extract details.
    data = json.loads(payload.decode('utf-8'))
    from_ = str(data.get("from", ""))
    from_ = from_.replace("/topics/", "@") if "/" in from_ else ("console" if from_.isdigit() else from_)
    notif = data.get("notification", {})
    notif_title = notif.get("title", "Notification")
    notif_body = notif.get("body", "").strip()
    data_custom = data.get("data", {})
    data_filtered = {k: v for k, v in data_custom.items() if not k.startswith(("google.", "gcm."))}

    # Print message.
    msg_from = f"{Fore.LIGHTBLACK_EX}[{from_}]{Style.RESET_ALL}" if from_ else ""
    msg_title = f"{Fore.YELLOW}{Style.BRIGHT}{notif_title}{Style.RESET_ALL}"
    msg_body = f"| {notif_body}" if notif_body else ""
    msg_data = f"{Style.DIM}{Fore.BLUE}{json.dumps(data_filtered)}{Style.RESET_ALL}" if data_filtered else ""
    print(" ".join(part for part in [msg_from, msg_title, msg_body, msg_data] if part))


@app.command()
def run(project_id: ProjectId, api_key: ApiKey, app_id: AppId, topics: Topics, debug: bool = False):
    if not debug:
        redefine_print()

    client = FCMClient()
    client.project_id = project_id
    client.api_key = api_key
    client.app_id = app_id

    client.on_data_message = handle_data
    client.on_connection_status = handle_status

    try:
        handle_status("starting listener...")
        client.create_new_keys()
        client.register()

        for topic in topics:
            topic = topic.strip()
            handle_status(f"subscribing to {Style.BRIGHT}{topic}{Style.NORMAL}...")
            client.subscribe_to_topic(topic)

        client.start_listening()
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        handle_status("stopping client...")
    finally:
        client.close()
        sys.exit(0)


if __name__ == "__main__":
    app()
