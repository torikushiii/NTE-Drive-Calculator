<div align="center">

<img src="assets/app_icon.png" alt="NTE Drive Calc English" width="108">
<h1>NTE Drive Calc English</h1>
<p>English edition of <a href="https://github.com/hxwd94666/NTE-Drive-Calculator">NTE Drive Calc</a></p>

Import your *Neverness to Everness* inventory as a computable stock, appraise Modules and Cartridges with algorithms, build loadouts for every character, and equip them automatically.

[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-0078d4)](#environment)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776ab)](#development)
[![Download](https://img.shields.io/badge/download-English%20Windows%20build-238636)](https://github.com/torikushiii/NTE-Drive-Calculator-English/releases)
[![Downloads](https://img.shields.io/github/downloads/torikushiii/NTE-Drive-Calculator-English/total?label=downloads&color=238636)](https://github.com/torikushiii/NTE-Drive-Calculator-English/releases)
[![Stars](https://img.shields.io/github/stars/torikushiii/NTE-Drive-Calculator-English?label=stars&color=f4b400)](https://github.com/torikushiii/NTE-Drive-Calculator-English/stargazers)


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

Download the Windows 10/11 x64 installer from [this fork's releases](https://github.com/torikushiii/NTE-Drive-Calculator-English/releases).
Choose the `NTE_Drive_Calc_English_Setup_*.exe` asset, not GitHub's source-code archives.

The installer and application default to English and install separately from the upstream edition.
English builds are initially published as prereleases while Windows/game acceptance is pending.
The `SHA256SUMS.txt` asset records the installer checksum.
In-app downloads and update checks use this fork, including its English prereleases;
the upstream MirrorChyan and cloud-drive downloads are not used.

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

- English edition issues: <https://github.com/torikushiii/NTE-Drive-Calculator-English/issues>
- Upstream project: <https://github.com/hxwd94666/NTE-Drive-Calculator>

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

### Windows Builds

Maintainers can run **Build English Windows release** from this fork's GitHub Actions tab.
Leave `publish` off for a build artifact only; enable it to publish an English prerelease after
the existing packaging/component checks succeed. This workflow does not run the test suite or
interactive Windows/game acceptance. Increment `ENGLISH_RELEASE_REVISION` in `src/app/version.py`
for another English build of the same upstream version. See [English-edition internals](docs/i18n.md).

The Windows release uses PyInstaller to bundle the Python/PySide6 app, then Inno Setup 6 to create the installer. Run the following commands in the repository root on Windows 10/11 x64 with Python 3.11 x64 and the dependencies installed above, including the `build` group.

Packaging requires the release databases, manifests and images under `data/`, including `data/role_catalog/`, plus the approved prebuilt components under `third_party/`. The build does not compile `nte-core.exe`, `nte-analysis-core.exe` or the game DLLs from source. Their matching manifests and license files must be present; missing files, mismatched hashes or incompatible component capabilities stop packaging. See [External Integrations](docs/integrations.md) for the component delivery contracts.

#### Desktop App

Build the default directory bundle:

```powershell
uv run python build_exe.py
```

The executable is `dist/NTE_Drive_Calc/NTE_Drive_Calc.exe`. Distribute the entire `dist/NTE_Drive_Calc/` directory, including `_internal/`, not just the executable. The default build has no console window and requests administrator privileges on launch. Add `--console` to keep a console for diagnostics.

For a single-file bundle instead:

```powershell
uv run python build_exe.py --onefile
```

This writes `dist/NTE_Drive_Calc.exe`. Each app build replaces the previous directory and single-file outputs. The installer requires the default directory bundle, so rebuild without `--onefile` before packaging an installer.

#### Installer

Install Inno Setup 6, then build the app and installer together:

```powershell
uv run python build_installer.py
```

If the default directory bundle is already built, reuse it:

```powershell
uv run python build_installer.py --skip-app-build
```

If the Inno Setup compiler is not detected, provide its path explicitly, adjusting it to your installation:

```powershell
uv run python build_installer.py --skip-app-build --iscc "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

Alternatively, set the `INNO_SETUP_ISCC` environment variable to the full path of `ISCC.exe`.

The installer is written to `installer/output/NTE_Drive_Calc_Setup_<version>.exe`, using the version from `src/app/version.py` by default. It includes the ViGEmBus driver installer from `third_party/vigembus/bin/`, with a fallback to the MSI supplied by `vgamepad`. Use `--vigem-installer` to provide an external `.exe` or `.msi` instead.

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
