# VIChess

**VIChess** is an open-source chess application built with **Python** and **Flet**, designed to deliver a modern, responsive, and lightweight chess experience across desktop and mobile platforms.

## Features

- Local two-player (pass-and-play) mode
- Play against the built-in **VIChess AI**
- Full implementation of official chess rules:
  - Check and checkmate
  - Stalemate
  - Castling
  - En passant(coming soon)
  - Pawn promotion with piece selection
  - Draw detection:
    - Threefold repetition
    - Fifty-move rule
    - Insufficient material
- Smooth piece animations
- SVG-based chess pieces for crisp rendering on all display sizes
- Cross-platform support powered by **Flet**

## Architecture

VIChess is built on two internal components:

| Component    | Description                                                                                                         |
|--------------|---------------------------------------------------------------------------------------------------------------------|
| **VIUI**     | The user interface framework responsible for the application's design and layout.                                   |
| **VIRender** | The chess rendering engine responsible for board rendering, animations, move handling, highlights, and interaction. |

## VIRender

**VIRender** is completely free to use.

If you're developing your own chess project, you're welcome to reuse the rendering engine found in the `lib/` directory, including its board renderer and chess UI components.

Credit is appreciated but not required.

VIRender was originally developed for **VIChess** and is maintained by **radin6262**, the owner of this repository.

## Versioning

VIChess uses the following versioning format:

```text
major.minor
```

Examples:

- `1.0`
- `1.4`
- `2.0`

> Prior to version 3.0, internal builds were versioned using the `VIUI.VIRender` format.

## Platform Support

Starting with **VIChess 3.0**, official Android builds are provided **only for ARM64 (`arm64-v8a`) devices**.

This decision reduces APK size, improves performance, and reflects the fact that the vast majority of modern Android devices use 64-bit ARM processors.

The following architectures are **no longer officially supported**:

- `armeabi-v7a` (32-bit ARM)
- `x86_64` (Android emulators and select desktop environments)

If you require support for these architectures, you can build VIChess yourself from source using Flet's target architecture options.


## Installation From Source

Clone the repository:

```bash
git clone <repository-url>
cd VIChess
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run VIChess:

```bash
python main.py
```

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt`

## License

VIChess is open source.

Project License: MIT