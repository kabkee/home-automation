#!/usr/bin/env python3
"""
Log Roro commands to the command history file.
Usage:
  python3 scripts/log_command.py --platform smartthings --device "티비 등" --action "Turned OFF" --source user --result success --detail "거실 TV 등 꺼줘"

  python3 scripts/log_command.py --platform xiaomi --device "드레스룸" --action "Turned ON" --source automation --result success --detail "습도 60% > 50%"
"""
import json, os, sys, argparse
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'data')
COMMANDS_FILE = os.path.join(DATA_DIR, 'commands.json')

def load():
    if not os.path.exists(COMMANDS_FILE):
        return []
    try:
        with open(COMMANDS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save(commands):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(COMMANDS_FILE, 'w') as f:
        json.dump(commands, f, indent=2, ensure_ascii=False)
        f.write('\n')

def log(platform, device, action, source='user', result='success', detail=''):
    now = datetime.now(KST)
    entry = {
        "timestamp": int(now.timestamp()),
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "platform": platform,
        "device": device,
        "action": action,
        "detail": detail,
        "result": result,
    }
    commands = load()
    commands.append(entry)
    # Keep max 10000 entries
    if len(commands) > 10000:
        commands = commands[-10000:]
    save(commands)
    return entry

def list_entries(limit=20):
    commands = load()
    for entry in commands[-limit:]:
        print(f"[{entry['time']}] {entry['source']}/{entry['platform']}: {entry['device']} → {entry['action']} ({entry['result']})")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Log a Roro command')
    parser.add_argument('--platform', choices=['smartthings', 'xiaomi', 'system', 'paperclip'], default='smartthings')
    parser.add_argument('--device', default='')
    parser.add_argument('--action', default='')
    parser.add_argument('--source', choices=['user', 'automation', 'system'], default='user')
    parser.add_argument('--result', choices=['success', 'failed', 'pending'], default='success')
    parser.add_argument('--detail', default='')
    parser.add_argument('--list', action='store_true', help='Show recent entries')

    args = parser.parse_args()

    if args.list:
        list_entries()
    else:
        entry = log(args.platform, args.device, args.action, args.source, args.result, args.detail)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
