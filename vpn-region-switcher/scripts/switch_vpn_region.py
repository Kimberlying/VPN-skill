#!/usr/bin/env python3
"""Switch a VPN region from an intent or country code."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
REGION_MAP_PATH = SKILL_DIR / "references" / "region-map.json"


PROVIDER_BINARIES = {
    "mullvad": "mullvad",
    "nordvpn": "nordvpn",
    "protonvpn": "protonvpn-cli",
}


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_region_map() -> dict[str, Any]:
    with REGION_MAP_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_intent_index(region_map: dict[str, Any]) -> dict[str, str]:
    index: dict[str, str] = {}
    for intent, entry in region_map["intents"].items():
        index[normalize(intent)] = intent
        for alias in entry.get("aliases", []):
            index[normalize(alias)] = intent
    return index


def build_country_index(region_map: dict[str, Any]) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for code, entry in region_map["countries"].items():
        target = {"country": entry["country"], "country_code": code.upper()}
        index[normalize(code)] = target
        index[normalize(entry["country"])] = target
        for alias in entry.get("aliases", []):
            index[normalize(alias)] = target
    return index


def resolve_target(
    region_map: dict[str, Any], intent: str | None, country: str | None
) -> tuple[str | None, dict[str, str]]:
    if country:
        country_index = build_country_index(region_map)
        target = country_index.get(normalize(country))
        if not target:
            known = ", ".join(sorted(region_map["countries"].keys()))
            raise ValueError(f"Unknown country '{country}'. Known country codes: {known}")
        return None, target

    if intent:
        intent_index = build_intent_index(region_map)
        canonical = intent_index.get(normalize(intent))
        if not canonical:
            known = ", ".join(sorted(region_map["intents"].keys()))
            raise ValueError(f"Unknown intent '{intent}'. Known intents: {known}")
        entry = region_map["intents"][canonical]
        return canonical, {
            "country": entry["country"],
            "country_code": entry["country_code"].upper(),
            "note": entry.get("note", ""),
        }

    raise ValueError("Provide either --intent or --country.")


def provider_available(provider: str) -> bool:
    binary = PROVIDER_BINARIES.get(provider)
    return bool(binary and shutil.which(binary))


def detect_provider(custom_template: str | None, dry_run: bool) -> str:
    if custom_template:
        return "custom"
    for provider in ("mullvad", "nordvpn", "protonvpn"):
        if provider_available(provider):
            return provider
    if dry_run:
        print(
            "No supported VPN CLI found; showing Mullvad command shape for dry-run.",
            file=sys.stderr,
        )
        return "mullvad"
    raise RuntimeError(
        "No supported VPN CLI found. Install Mullvad/NordVPN/ProtonVPN CLI, "
        "or pass --provider custom --custom-template 'vpn connect {country_code_lower}'."
    )


def provider_commands(provider: str, target: dict[str, str]) -> list[list[str]]:
    code_upper = target["country_code"].upper()
    code_lower = target["country_code"].lower()
    country = target["country"]

    if provider == "mullvad":
        return [
            ["mullvad", "relay", "set", "location", code_lower],
            ["mullvad", "connect"],
        ]
    if provider == "nordvpn":
        return [["nordvpn", "connect", country]]
    if provider == "protonvpn":
        return [["protonvpn-cli", "connect", "--cc", code_upper]]
    raise ValueError(f"Provider '{provider}' does not have built-in commands.")


def status_commands(provider: str) -> list[list[str]]:
    if provider == "mullvad":
        return [["mullvad", "status"]]
    if provider == "nordvpn":
        return [["nordvpn", "status"]]
    if provider == "protonvpn":
        return [["protonvpn-cli", "status"]]
    raise ValueError("Status is not available for custom provider templates.")


def custom_commands(
    template: str, target: dict[str, str], resolved_intent: str | None
) -> list[list[str]]:
    values = {
        "country": target["country"],
        "country_code": target["country_code"].upper(),
        "country_code_upper": target["country_code"].upper(),
        "country_code_lower": target["country_code"].lower(),
        "intent": resolved_intent or "",
    }
    rendered = template.format(**values)
    return [shlex.split(rendered)]


def run_commands(commands: list[list[str]], dry_run: bool) -> int:
    for command in commands:
        print(f"$ {shlex.join(command)}")
        if dry_run:
            continue
        try:
            subprocess.run(command, check=True)
        except FileNotFoundError:
            print(f"Command not found: {command[0]}", file=sys.stderr)
            return 127
        except subprocess.CalledProcessError as exc:
            print(f"Command failed with exit code {exc.returncode}", file=sys.stderr)
            return exc.returncode
    return 0


def print_list(region_map: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(region_map, indent=2, ensure_ascii=False))
        return

    print("Known intents:")
    for intent, entry in sorted(region_map["intents"].items()):
        print(
            f"  {intent:10s} -> {entry['country']} "
            f"({entry['country_code'].upper()}): {entry.get('note', '')}"
        )

    print("\nKnown countries:")
    for code, entry in sorted(region_map["countries"].items()):
        print(f"  {code.upper():2s} -> {entry['country']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Switch a VPN region from an intent or explicit country."
    )
    parser.add_argument("-i", "--intent", help="Intent such as flights, hotels, shopping, youtube.")
    parser.add_argument("-c", "--country", help="Country name or ISO code such as India or IN.")
    parser.add_argument(
        "--provider",
        choices=["auto", "mullvad", "nordvpn", "protonvpn", "custom"],
        default="auto",
        help="VPN provider CLI to use. Default: auto.",
    )
    parser.add_argument(
        "--custom-template",
        default=os.environ.get("VPN_SWITCH_COMMAND"),
        help="Custom command template. Can also be set with VPN_SWITCH_COMMAND.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running them.")
    parser.add_argument("--list", action="store_true", help="List known intents and countries.")
    parser.add_argument("--json", action="store_true", help="Use JSON output with --list.")
    parser.add_argument("--status", action="store_true", help="Show VPN status for the selected provider.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    region_map = load_region_map()

    if args.list:
        print_list(region_map, args.json)
        return 0

    try:
        provider = (
            detect_provider(args.custom_template, args.dry_run)
            if args.provider == "auto"
            else args.provider
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 127

    if args.status:
        if provider == "custom":
            print("Status is not available for custom provider templates.", file=sys.stderr)
            return 2
        return run_commands(status_commands(provider), args.dry_run)

    try:
        resolved_intent, target = resolve_target(region_map, args.intent, args.country)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(
        "Resolved target: "
        f"{target['country']} ({target['country_code'].upper()})"
        + (f" for intent '{resolved_intent}'" if resolved_intent else "")
    )
    if target.get("note"):
        print(f"Note: {target['note']}")

    if provider == "custom":
        if not args.custom_template:
            print("--provider custom requires --custom-template or VPN_SWITCH_COMMAND.", file=sys.stderr)
            return 2
        commands = custom_commands(args.custom_template, target, resolved_intent)
    else:
        if not args.dry_run and not provider_available(provider):
            print(f"Provider CLI not found for '{provider}'.", file=sys.stderr)
            return 127
        commands = provider_commands(provider, target)

    print(f"Provider: {provider}")
    return run_commands(commands, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
