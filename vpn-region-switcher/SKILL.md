---
name: vpn-region-switcher
description: Use this skill to choose and switch a VPN region from a user intent such as airfare comparison, hotel price comparison, shopping localization, streaming availability checks, privacy routing, or an explicit country/region request. It provides a script that maps intents to countries and calls supported VPN CLIs or a custom command template.
---

# VPN Region Switcher

## Overview

Use this skill when the user wants Codex to switch VPN regions, test region-specific content, compare regional prices, or route traffic through a named country. The skill prefers a dry run first when the installed VPN provider is unknown.

Respect service terms and local law. Do not claim that a region will guarantee discounts, ad removal, or access; the script only changes the VPN endpoint and the user must verify the result.

## Quick Start

From this skill directory:

```bash
python3 scripts/switch_vpn_region.py --list
python3 scripts/switch_vpn_region.py --intent flights --dry-run
python3 scripts/switch_vpn_region.py --intent hotels
python3 scripts/switch_vpn_region.py --country BR
python3 scripts/switch_vpn_region.py --status
```

Default intent mapping:

- `flights` -> India (`IN`)
- `hotels` -> Vietnam (`VN`)
- `shopping` -> Brazil (`BR`)
- `youtube` / `streaming` -> Albania (`AL`)

For Chinese user wording, translate intent before calling the script:

- flight tickets or "ji piao" -> `--intent flights`
- hotels or "jiu dian" -> `--intent hotels`
- general shopping, ecommerce, or "mai dong xi" -> `--intent shopping`
- YouTube or ad-behavior checks -> `--intent youtube`

## Provider Selection

Run `--dry-run` first unless the user has named a VPN provider or already confirmed one.

The script supports:

- `--provider auto` (default): use `VPN_SWITCH_COMMAND` if set, otherwise detect a known CLI.
- `--provider mullvad`: runs `mullvad relay set location <code>` then `mullvad connect`.
- `--provider nordvpn`: runs `nordvpn connect <country>`.
- `--provider protonvpn`: runs `protonvpn-cli connect --cc <code>`.
- `--provider custom`: runs a custom command template.

Custom template examples:

```bash
VPN_SWITCH_COMMAND='myvpn connect {country_code_lower}' python3 scripts/switch_vpn_region.py --intent flights
python3 scripts/switch_vpn_region.py --country Albania --provider custom --custom-template 'myvpn connect "{country}"'
```

Supported placeholders:

- `{country}`: display country name, for example `India`
- `{country_code}` / `{country_code_upper}`: ISO country code, for example `IN`
- `{country_code_lower}`: lowercase ISO country code, for example `in`
- `{intent}`: resolved intent name when one was provided

## Editing The Map

Edit `references/region-map.json` to change intent aliases, target countries, or notes. Keep country codes as ISO 3166-1 alpha-2 values where possible because most VPN CLIs accept or can derive from them.

When adding a fragile provider-specific command, add it to `scripts/switch_vpn_region.py` and verify with:

```bash
python3 scripts/switch_vpn_region.py --intent flights --provider <provider> --dry-run
python3 /Users/qianmeng/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```
