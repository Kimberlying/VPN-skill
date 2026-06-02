# VPN Region Switcher Skill 使用说明

这是一个给 Codex 用的 VPN 地区切换 skill，也可以单独当命令行脚本用。

它的作用很简单：你告诉它要做什么，比如查机票、比酒店价格、看购物地区价、测试 YouTube/流媒体地区表现，它会自动映射到一个推荐 VPN 地区，然后调用你本机已有的 VPN 命令行工具进行切换。

注意：这个项目只负责切换 VPN 节点，不保证一定便宜、一定无广告或一定能访问某个地区内容。请遵守当地法律和各平台服务条款。

## 默认映射

| 场景 | 命令 intent | 推荐地区 |
| --- | --- | --- |
| 机票价格对比 | `flights` | 印度 `IN` |
| 酒店价格对比 | `hotels` | 越南 `VN` |
| 购物/电商地区价 | `shopping` | 巴西 `BR` |
| YouTube/流媒体地区测试 | `youtube` / `streaming` | 阿尔巴尼亚 `AL` |

这些映射都在 `vpn-region-switcher/references/region-map.json` 里，可以自己改。

## 安装方式

先克隆这个仓库：

```bash
git clone https://github.com/Kimberlying/VPN-skill.git
cd VPN-skill
```

如果你只是想用脚本，不需要额外安装：

```bash
cd vpn-region-switcher
python3 scripts/switch_vpn_region.py --list
```

如果你想作为 Codex skill 使用，可以把整个 `vpn-region-switcher` 文件夹放到你的 Codex skills 目录里：

```bash
mkdir -p ~/.codex/skills
cp -R vpn-region-switcher ~/.codex/skills/
```

重启或刷新 Codex 后，就可以用 `$vpn-region-switcher` 调用。

## 先 Dry Run

第一次建议先 dry-run，只看它准备执行什么命令，不会真的切换 VPN：

```bash
cd vpn-region-switcher
python3 scripts/switch_vpn_region.py --intent flights --dry-run
```

示例输出大概是：

```text
Resolved target: India (IN) for intent 'flights'
Provider: mullvad
$ mullvad relay set location in
$ mullvad connect
```

## 真实切换

确认命令没问题后，去掉 `--dry-run`：

```bash
python3 scripts/switch_vpn_region.py --intent flights
python3 scripts/switch_vpn_region.py --intent hotels
python3 scripts/switch_vpn_region.py --intent shopping
python3 scripts/switch_vpn_region.py --intent youtube
```

也可以直接指定国家：

```bash
python3 scripts/switch_vpn_region.py --country BR
python3 scripts/switch_vpn_region.py --country Albania
```

查看 VPN 状态：

```bash
python3 scripts/switch_vpn_region.py --status
```

## 支持的 VPN

脚本会自动检测这些命令行工具：

- `mullvad`
- `nordvpn`
- `protonvpn-cli`

也可以手动指定：

```bash
python3 scripts/switch_vpn_region.py --intent hotels --provider nordvpn
python3 scripts/switch_vpn_region.py --country IN --provider protonvpn
```

## 使用自己的 VPN 命令

如果你的 VPN 有自己的 CLI，可以用自定义模板：

```bash
python3 scripts/switch_vpn_region.py \
  --intent shopping \
  --provider custom \
  --custom-template 'myvpn connect {country_code_lower}'
```

也可以用环境变量：

```bash
VPN_SWITCH_COMMAND='myvpn connect {country_code_lower}' \
  python3 scripts/switch_vpn_region.py --intent youtube
```

可用占位符：

| 占位符 | 含义 | 示例 |
| --- | --- | --- |
| `{country}` | 国家名 | `India` |
| `{country_code}` | 大写国家代码 | `IN` |
| `{country_code_upper}` | 大写国家代码 | `IN` |
| `{country_code_lower}` | 小写国家代码 | `in` |
| `{intent}` | 解析后的场景名 | `flights` |

## 给 Codex 的使用示例

装成 skill 后，可以这样说：

```text
Use $vpn-region-switcher to switch my VPN for checking flight prices.
```

或者中文也可以：

```text
用 $vpn-region-switcher 帮我切到查机票适合的 VPN 地区。
```

```text
用 $vpn-region-switcher 切到酒店价格对比模式，先 dry-run。
```

```text
用 $vpn-region-switcher 帮我切到巴西节点测试购物地区价。
```

## 修改映射规则

打开这个文件：

```text
vpn-region-switcher/references/region-map.json
```

比如你想把 `flights` 从印度改成别的地区，就改：

```json
{
  "intents": {
    "flights": {
      "country": "India",
      "country_code": "IN"
    }
  }
}
```

建议国家代码使用 ISO 3166-1 alpha-2 格式，比如 `IN`、`VN`、`BR`、`AL`。

## 常见问题

### 提示 No supported VPN CLI found

说明你的电脑上没有检测到 `mullvad`、`nordvpn` 或 `protonvpn-cli`。

解决方式：

- 安装其中一个 VPN 的命令行工具
- 或者用 `--provider custom --custom-template`
- 或者设置 `VPN_SWITCH_COMMAND`

### 不想真的切换，只想看命令

加上 `--dry-run`：

```bash
python3 scripts/switch_vpn_region.py --intent flights --dry-run
```

### 可以保证省钱或无广告吗

不能。地区价格、广告展示和内容可用性会随平台策略、账号状态、支付方式、缓存、Cookie、设备环境等变化。这个 skill 只负责切换 VPN 地区，结果需要你自己验证。
