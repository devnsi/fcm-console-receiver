#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "colorama",
#   "fcm-receiver",
#   "pygments",
#   "python-dotenv",
#   "typer",
# ]
# ///

import builtins
import json
import threading
import time
from typing import Annotated

import typer
from colorama import Fore, Style, init
from dotenv import load_dotenv
from fcm_receiver import FCMClient
from pygments import highlight, lexers, formatters

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


def redefine_print(debug: bool = False):
    print_lock = threading.Lock()
    print_actual = builtins.print

    def filtered_print(*args, **kwargs):
        msg = " ".join(map(str, args))
        block_list = ["[fcm_socket]", "[fcm_client]"]
        ignore_print = not debug and any(msg.startswith(prefix) for prefix in block_list)
        if ignore_print:
            return
        with print_lock:
            print_actual(*args, **kwargs)

    builtins.print = filtered_print


def handle_status(status: str, _: str = "") -> None:
    print(f"{Fore.LIGHTBLACK_EX}[status]{Style.RESET_ALL} {Fore.MAGENTA}{status}{Style.RESET_ALL}")


def handle_data(payload: bytes, _: str, debug: bool = False) -> None:
    try:
        # Extract details.
        payload_str = payload.decode('utf-8')
        payload = json.loads(payload_str)
        data = payload.get("data", {})
        data = {k: unwrap(v) for k, v in data.items() if not k.startswith(("google.", "gcm."))}
        from_ = payload.get("from") or data.get("topic") or ""
        from_ = from_.replace("/topics/", "@") if "/" in from_ else ("@any" if from_.isdigit() else from_)
        notif = payload.get("notification", {})
        notif_title = notif.get("title") or data.pop("title", None) or "Notification"
        notif_body = notif.get("body") or data.pop("body", None) or data.pop("description", None) or ""
        priority = payload.get("priority") or ""

        # Print message.
        priority_str = "!" if priority == "high" else ""
        data_str = json.dumps(data, indent=None, sort_keys=True, ensure_ascii=False)
        data_colored = json_highlight(data_str, style="nord")
        msg_from = f"{Fore.LIGHTBLACK_EX}[{from_}]{priority_str}{Style.RESET_ALL}" if from_ else ""
        msg_title = f"{Fore.YELLOW}{Style.BRIGHT}{notif_title}{Style.RESET_ALL}"
        msg_body = f"| {notif_body}" if notif_body else ""
        msg_data = f"{data_colored}" if data else ""
        print(" ".join(part for part in [msg_from, msg_title, msg_body, msg_data] if part))
        if debug:
            payload_str = json.dumps(payload, indent=4, sort_keys=True, ensure_ascii=False)
            payload_colored = json_highlight(payload_str, style="arduino")
            print(f"{Fore.LIGHTBLACK_EX}[{from_}]{Fore.RESET} Raw | {payload_colored}")
    except Exception as e:
        print(f"{Fore.LIGHTBLACK_EX}[error]{Style.RESET_ALL} failed to receive: {Fore.RED}{e}{Fore.RESET}")


def json_highlight(data: str, style: str):
    return highlight(data, lexers.JsonLexer(), formatters.Terminal256Formatter(style=style)).strip()


def unwrap(v):
    try:
        return json.loads(v) if isinstance(v, str) and v.startswith(("{", "[")) else v
    except ValueError:
        return v


@app.command()
def run(project_id: ProjectId, api_key: ApiKey, app_id: AppId, topics: Topics, debug: bool = False):
    redefine_print(debug)

    client = FCMClient()
    client.project_id = project_id
    client.api_key = api_key
    client.app_id = app_id

    client.on_data_message = lambda m, s: handle_data(m, s, debug)
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
            time.sleep(100)

    except KeyboardInterrupt:
        handle_status("stopping listener...")
    finally:
        client.close()


if __name__ == "__main__":
    app()
