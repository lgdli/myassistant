<p align="center">
  <a href="https://myassistant.ai">
    <picture>
      <source srcset="packages/console/app/src/asset/logo-ornate-dark.svg" media="(prefers-color-scheme: dark)">
      <source srcset="packages/console/app/src/asset/logo-ornate-light.svg" media="(prefers-color-scheme: light)">
      <img src="packages/console/app/src/asset/logo-ornate-light.svg" alt="MyAssistant logo">
    </picture>
  </a>
</p>
<p align="center">Den open source AI-kodeagent.</p>
<p align="center">
  <a href="https://myassistant.ai/discord"><img alt="Discord" src="https://img.shields.io/discord/1391832426048651334?style=flat-square&label=discord" /></a>
  <a href="https://www.npmjs.com/package/myassistant-ai"><img alt="npm" src="https://img.shields.io/npm/v/myassistant-ai?style=flat-square" /></a>
  <a href="https://github.com/anomalyco/myassistant/actions/workflows/publish.yml"><img alt="Build status" src="https://img.shields.io/github/actions/workflow/status/anomalyco/myassistant/publish.yml?style=flat-square&branch=dev" /></a>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh.md">简体中文</a> |
  <a href="README.zht.md">繁體中文</a> |
  <a href="README.ko.md">한국어</a> |
  <a href="README.de.md">Deutsch</a> |
  <a href="README.es.md">Español</a> |
  <a href="README.fr.md">Français</a> |
  <a href="README.it.md">Italiano</a> |
  <a href="README.da.md">Dansk</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.pl.md">Polski</a> |
  <a href="README.ru.md">Русский</a> |
  <a href="README.bs.md">Bosanski</a> |
  <a href="README.ar.md">العربية</a> |
  <a href="README.no.md">Norsk</a> |
  <a href="README.br.md">Português (Brasil)</a> |
  <a href="README.th.md">ไทย</a> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a> |
  <a href="README.bn.md">বাংলা</a> |
  <a href="README.gr.md">Ελληνικά</a> |
  <a href="README.vi.md">Tiếng Việt</a>
</p>

[![MyAssistant Terminal UI](packages/web/src/assets/lander/screenshot.png)](https://myassistant.ai)

---

### Installation

```bash
# YOLO
curl -fsSL https://myassistant.ai/install | bash

# Pakkehåndteringer
npm i -g myassistant-ai@latest        # eller bun/pnpm/yarn
scoop install myassistant             # Windows
choco install myassistant             # Windows
brew install anomalyco/tap/myassistant # macOS og Linux (anbefalet, altid up to date)
brew install myassistant              # macOS og Linux (officiel brew formula, opdateres sjældnere)
sudo pacman -S myassistant            # Arch Linux (Stable)
paru -S myassistant-bin               # Arch Linux (Latest from AUR)
mise use -g myassistant               # alle OS
nix run nixpkgs#myassistant           # eller github:anomalyco/myassistant for nyeste dev-branch
```

> [!TIP]
> Fjern versioner ældre end 0.1.x før installation.

### Desktop-app (BETA)

MyAssistant findes også som desktop-app. Download direkte fra [releases-siden](https://github.com/anomalyco/myassistant/releases) eller [myassistant.ai/download](https://myassistant.ai/download).

| Platform              | Download                              |
| --------------------- | ------------------------------------- |
| macOS (Apple Silicon) | `myassistant-desktop-darwin-aarch64.dmg` |
| macOS (Intel)         | `myassistant-desktop-darwin-x64.dmg`     |
| Windows               | `myassistant-desktop-windows-x64.exe`    |
| Linux                 | `.deb`, `.rpm`, eller AppImage        |

```bash
# macOS (Homebrew)
brew install --cask myassistant-desktop
# Windows (Scoop)
scoop bucket add extras; scoop install extras/myassistant-desktop
```

#### Installationsmappe

Installationsscriptet bruger følgende prioriteringsrækkefølge for installationsstien:

1. `$OPENCODE_INSTALL_DIR` - Tilpasset installationsmappe
2. `$XDG_BIN_DIR` - Sti der følger XDG Base Directory Specification
3. `$HOME/bin` - Standard bruger-bin-mappe (hvis den findes eller kan oprettes)
4. `$HOME/.myassistant/bin` - Standard fallback

```bash
# Eksempler
OPENCODE_INSTALL_DIR=/usr/local/bin curl -fsSL https://myassistant.ai/install | bash
XDG_BIN_DIR=$HOME/.local/bin curl -fsSL https://myassistant.ai/install | bash
```

### Agents

MyAssistant har to indbyggede agents, som du kan skifte mellem med `Tab`-tasten.

- **build** - Standard, agent med fuld adgang til udviklingsarbejde
- **plan** - Skrivebeskyttet agent til analyse og kodeudforskning
  - Afviser filredigering som standard
  - Spørger om tilladelse før bash-kommandoer
  - Ideel til at udforske ukendte kodebaser eller planlægge ændringer

Derudover findes der en **general**-subagent til komplekse søgninger og flertrinsopgaver.
Den bruges internt og kan kaldes via `@general` i beskeder.

Læs mere om [agents](https://myassistant.ai/docs/agents).

### Dokumentation

For mere info om konfiguration af MyAssistant, [**se vores docs**](https://myassistant.ai/docs).

### Bidrag

Hvis du vil bidrage til MyAssistant, så læs vores [contributing docs](./CONTRIBUTING.md) før du sender en pull request.

### Bygget på MyAssistant

Hvis du arbejder på et projekt der er relateret til MyAssistant og bruger "myassistant" som en del af navnet; f.eks. "myassistant-dashboard" eller "myassistant-mobile", så tilføj en note i din README, der tydeliggør at projektet ikke er bygget af MyAssistant-teamet og ikke er tilknyttet os på nogen måde.

### FAQ

#### Hvordan adskiller dette sig fra Claude Code?

Det minder meget om Claude Code i forhold til funktionalitet. Her er de vigtigste forskelle:

- 100% open source
- Ikke låst til en udbyder. Selvom vi anbefaler modellerne via [MyAssistant Zen](https://myassistant.ai/zen); kan MyAssistant bruges med Claude, OpenAI, Google eller endda lokale modeller. Efterhånden som modeller udvikler sig vil forskellene mindskes og priserne falde, så det er vigtigt at være provider-agnostic.
- LSP-support out of the box
- Fokus på TUI. MyAssistant er bygget af neovim-brugere og skaberne af [terminal.shop](https://terminal.shop); vi vil skubbe grænserne for hvad der er muligt i terminalen.
- Klient/server-arkitektur. Det kan f.eks. lade MyAssistant køre på din computer, mens du styrer den eksternt fra en mobilapp. Det betyder at TUI-frontend'en kun er en af de mulige clients.

---

**Bliv en del af vores community** [Discord](https://discord.gg/myassistant) | [X.com](https://x.com/myassistant)
