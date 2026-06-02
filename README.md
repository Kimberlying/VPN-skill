# VPN Skill

A Codex skill for switching VPN regions by intent.

It maps common tasks like airfare checks, hotel-price comparison, shopping localization, and YouTube/streaming tests to suggested VPN regions, then calls a supported VPN CLI or a custom command template.

## What It Does

Default intent mapping:

| Intent | Region |
| --- | --- |
| `flights` | India (`IN`) |
| `hotels` | Vietnam (`VN`) |
| `shopping` | Brazil (`BR`) |
| `youtube` / `streaming` | Albania (`AL`) |

The skill does not guarantee discounts, ad removal, or access to region-specific content. It only switches the VPN endpoint; you still need to verify the result on the target website or app and follow local law and service terms.

## Project Structure

```text
vpn-region-switcher/
├── SKILL.md
├── agents/openai.yaml
├── references/region-map.json
└── scripts/switch_vpn_region.py
```

## Quick Start

```bash
cd vpn-region-switcher
python3 scripts/switch_vpn_region.py --list
python3 scripts/switch_vpn_region.py --intent flights --dry-run
python3 scripts/switch_vpn_region.py --intent hotels
python3 scripts/switch_vpn_region.py --country BR
```

Use `--dry-run` first if you are not sure which VPN CLI is installed.

## Supported VPN Providers

The script can use:

- `mullvad`
- `nordvpn`
- `protonvpn-cli`
- any custom command template through `--provider custom` or `VPN_SWITCH_COMMAND`

Custom command example:

```bash
VPN_SWITCH_COMMAND='myvpn connect {country_code_lower}' \
  python3 scripts/switch_vpn_region.py --intent shopping
```

Supported placeholders:

- `{country}`: country name, for example `India`
- `{country_code}` / `{country_code_upper}`: uppercase country code, for example `IN`
- `{country_code_lower}`: lowercase country code, for example `in`
- `{intent}`: resolved intent name

## Edit Region Rules

Change intent aliases or target regions in:

```text
vpn-region-switcher/references/region-map.json
```

Keep country codes as ISO 3166-1 alpha-2 values where possible.
