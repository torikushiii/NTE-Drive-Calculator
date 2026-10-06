<div align="center">

<img src="https://raw.githubusercontent.com/hxwd94666/NTE-Drive-Calc/main/assets/app_icon.png" alt="NTE Drive Calc" width="108">
<h1>异环驱动计算器</h1>
<p><strong>NTE Drive Calc</strong></p>

Import your *Neverness to Everness* inventory as a computable stock, appraise Modules and Cartridges with algorithms, build loadouts for every character, and equip them automatically.

[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-0078d4)](#environment)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776ab)](#development)
[![Download](https://img.shields.io/badge/download-GitHub%20Release-238636)](https://github.com/hxwd94666/NTE-Drive-Calculator/releases)
[![Downloads](https://img.shields.io/github/downloads/hxwd94666/NTE-Drive-Calculator/total?label=downloads&color=238636)](https://github.com/hxwd94666/NTE-Drive-Calculator/releases)
[![Stars](https://img.shields.io/github/stars/hxwd94666/NTE-Drive-Calculator?label=stars&color=f4b400)](https://github.com/hxwd94666/NTE-Drive-Calculator/stargazers)


[Download](#download) · [Features](#features) · [Quick Start](#quick-start) · [Feedback](#feedback)

**English** · [简体中文](README.zh-CN.md)

🐧QQ Group: 1029030672 🎮Discord Server: https://discord.gg/P3ZvMN7Hwj

</div>

> This is the English edition of NTE Drive Calc. The interface is translated at runtime; game
> names use the official English localization. The in-game OCR scanner still
> expects the game client to be set to Simplified Chinese.

<a id="intro"></a>

## 📖 About

NTE Drive Calc is a Windows desktop companion tool for Module and Cartridge progression in *Neverness to Everness*.

The project serves gear calculation, loadout building and understanding of the game, and it opposes use for cheats, for undermining fair play, or for harming the lawful rights of Perfect World and other rights holders. Collaboration on legitimate features is welcome; see [Purpose, Anti-Abuse and Collaboration Statement](RESPONSIBLE_USE.md) for the project's purpose, private source access and authorization boundaries.

It solves the problems players run into more and more in the late game:

- Your inventory holds more and more gear, and judging and equipping it by hand costs too much
- Several characters compete for the same gear, and it's unclear how to split it more sensibly
- No consistent standard for whether a newly farmed Module or Cartridge is worth keeping
- You want to manage your account's inventory long term without always doing the math and remembering it yourself

The tool builds a local inventory from screenshot recognition, then combines character blueprints, set requirements, stat weights and character priorities to produce practical loadouts and automated equipping.

<a id="features"></a>

## ⭐️ Features

| Capability      | What it solves                     |
|---------|----------------------------|
| 📷 Inventory Import | Scan screenshots or fetch in one click to turn Modules and Cartridges into a computable stock |
| 🔍 Appraisal | See who a piece of gear suits, what it scores and whether it is worth keeping |
| 🧮 Loadout Generation | Generate Module and Cartridge plans from character blueprints, sets, weights and priorities |
| 📐 Auto-Equip | Carry out automated equipping in the game from the generated loadouts |
| 📈 Character Marginals | Work out which stats the current character lacks most and adjust stat weights accordingly |
| 🧹 Module Management | After a scan, automatically lock or discard gear by score, rarity and type |

<a id="preview"></a>

## 🔥 Interface Preview

<table>
  <tr>
    <td align="center" width="50%">
      <strong>Loadout Results</strong><br>
      <sub>See each character's final Modules, Cartridges and score changes</sub><br><br>
      <img src="config/github/1.png" alt="Loadout Results">
    </td>
    <td align="center" width="50%">
      <strong>Gear Appraisal</strong><br>
      <sub>Score a single piece quickly and judge which characters it suits and whether it is worth keeping</sub><br><br>
      <img src="config/github/2.png" alt="Gear Appraisal">
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <strong>Module Management</strong><br>
      <sub>Automatically lock, discard or clear status by rule</sub><br><br>
      <img src="config/github/3.png" alt="Module Management">
    </td>
    <td align="center" width="50%">
      <strong>Character Marginals</strong><br>
      <sub>See which stat is the more worthwhile pick next for the current character</sub><br><br>
      <img src="config/github/4.png" alt="Character Marginals">
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <strong>Loadout Optimization</strong><br>
      <sub>Swap and optimize the Modules and Cartridges you are not happy with in a loadout</sub><br><br>
      <img src="config/github/5.png" alt="Loadout Optimization">
    </td>
    <td align="center" width="50%">
      <strong>Character Management</strong><br>
      <sub>Customize a character's progression direction to influence loadout allocation</sub><br><br>
      <img src="config/github/6.png" alt="Character Management">
    </td>
  </tr>
</table>

<a id="download"></a>

## ⬇️ Download & Install

We recommend downloading the latest installer:

- GitHub Release: <https://github.com/hxwd94666/NTE-Drive-Calculator/releases>
- MirrorChyan (paid): <https://mirrorchyan.com/zh/projects?rid=NTE-Drive-Calc&channel=stable>
- Quark Drive (free): <https://pan.quark.cn/s/82f16b845aec>
- Baidu Netdisk (free): <https://pan.baidu.com/s/1sPVqCpzmkQwKYCGstcZuIQ?pwd=ygke>
- Xunlei Drive (free): <https://pan.xunlei.com/s/VP0W_ptzSZwkVamy2UvF_CliA1?pwd=2hb6#>
> Saving each update to your own cloud drive earns the author a small commission, and saving from the mobile app earns more; you can treat this as a way to support the project without spending anything.

During installation, we recommend leaving `Install ViGEmBus virtual gamepad driver` checked. The scanning feature needs a virtual gamepad driver to simulate inventory page-turning.

<a id="quick-start"></a>

## 🚀 Quick Start

1. Install and open the app.
2. Open the in-game Module or Cartridge inventory.
3. Use Inventory Sync on the Dashboard, or Full Scan under Calculate, to get your data.
4. Once you have the data, pick the characters you want loadouts for in the Calculate feature.
5. Choose an allocation strategy and click Start.
6. Review the loadout results, then confirm and save the gear locks.
7. In the game, go to the character page, open the loadout page and click Equip

<a id="scenarios"></a>

## 🧰 Common Scenarios

- Loadout generation: import your inventory data and generate loadout plans from weights.
- Wondering whether a piece of gear is worth it: use Appraisal to see the score, which characters it suits and whether it is worth keeping.
- Wondering what a character is missing: use Character Marginals to see the current stat gain ranking.
- Inventory too full: automatically discard low-scoring gear and lock high-scoring gear by score, rarity and type.

<a id="environment"></a>

## 🖥️ System Requirements

- Windows 10/11 x64
- Game language: Simplified Chinese
- Recommended resolution: 1080p, 2K, 4K or 2560x1600
- The scanning feature requires the ViGEmBus virtual gamepad driver

<a id="feedback"></a>

## ❓️ Feedback

If you run into a recognition error, a failed installation, a scanning problem or loadout results that do not match expectations, please include as much of the following as you can:

- Screenshots of the problem
- Steps to reproduce
- The log file generated after enabling runtime logs on the Settings page
- The app version you are running

Where to report:

- GitHub Issues: <https://github.com/hxwd94666/NTE-Drive-Calc/issues>

<a id="development"></a>

## 🧑‍💻 Local Development

> [!IMPORTANT]
> Before preparing a fork for development, please join the QQ group `1029030672` and message the group owner directly. The main repository is under continuous development and commits are usually organized around version releases or development handovers; a fork's HEAD may not be the current collaboration baseline. Confirm the current baseline and merge approach before you start developing.

The project uses Python 3.11, SQLite and PySide6. See [System Architecture](docs/architecture.md) and [External Integrations](docs/integrations.md) for the detailed design; developer documentation starts from the [documentation index](docs/README.md).

After installing [uv](https://docs.astral.sh/uv/), run this in the repository root:

```powershell
uv sync --locked --group build --group dev
uv run python main.py
```

If you are not using `uv`, create a virtual environment and install the runtime, test and packaging dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e . coverage mypy pytest ruff pyinstaller
```

Run the tests:

```powershell
uv run python tools/quality/run_tests.py core -j 3
uv run python tools/quality/run_tests.py full
```

Build the desktop app:

```powershell
uv run python build_exe.py
```

Build the installer:

```powershell
uv run python build_installer.py
```

## 📑 License & Third-Party Components

The project's own source code is released under [AGPL-3.0](LICENSE). The `nte-core.exe`, the `nte-mods-plugin` `dwmapi.dll`, the fallback `nte-mod-loader.exe` and ViGEmBus distributed with the program are independent components; see [NOTICE](NOTICE) and `third_party/` for their origins, applicable terms and notices. The root license does not rewrite their respective licenses or authorizations.

This tool is an unofficial player tool. Game names, characters, assets and related rights belong to their respective rights holders; before using packet capture, plugins or automation features, confirm the applicable game rules, terms of service and local laws yourself.


## 💖 Support Us 

[<img width="150" alt="Support us" src="https://pic1.afdiancdn.com/static/img/welcome/button-sponsorme.png">](https://afdian.com/a/hxwd94666)

If you like our project, consider supporting it~

Donors can currently join the group to report bugs and request new features right away!

## 👥 Contributors

<a href="https://github.com/hxwd94666/NTE-Drive-Calc/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=hxwd94666/NTE-Drive-Calc" alt="contributors">
</a>

## 🤝 Acknowledgements

- 异环工坊 (WeChat Mini Program): provides the character scoring standards and stat weight references
- [nte-dps-toolkit](https://github.com/kongbaiz/nte-dps-toolkit): provides the core protocol parsing code and plugin support for equipping
