# FCM-Console Receiver

<!-- tag::short[] -->
A lightweight, headless receiver for Firebase Cloud Messaging (FCM).
<!-- end::short[] -->

This project uses the Web Push Protocol to subscribe to FCM topics and receive notifications directly in the terminal.  
It provides a clean, colorized stream of incoming data and notification payloads.

## Execution

```bash
uv run https://github.com/devnsi/fcm-console-receiver/raw/refs/heads/main/src/fcm_console_receiver/show_notifications.py
```

## Interface

```
 Usage: fcm-console-receiver [OPTIONS]
           
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --project-id            TEXT  Firebase Project ID. [env var: FCM_PROJECT_ID] [required]                         │
│ *  --api-key               TEXT  Firebase Web API Key for authentication. [env var: FCM_API_KEY] [required]        │
│ *  --app-id                TEXT  Unique App ID for the registered client. [env var: FCM_APP_ID] [required]         │
│    --topic                 TEXT  Topic to subscribe to. Can be used multiple times. [env var: FCM_TOPICS]          │
│    --debug                       [default: no-debug]                                                               │
│    --version                     Show version and exit.                                                            │
│    --install-completion          Install completion for the current shell.                                         │
│    --show-completion             Show completion for the current shell, to copy it or customize the installation.  │
│    --help                        Show this message and exit.                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
