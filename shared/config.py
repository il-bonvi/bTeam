# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

CONFIG_FILE = Path(__file__).resolve().parent.parent / "bteam_config.json"
# Use cross-platform path: user home directory instead of Windows-specific drive
DEFAULT_STORAGE_DIR = Path.home() / "bTeam"


def load_config() -> Dict[str, str]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_config(config: Dict[str, str]) -> None:
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def get_storage_dir() -> Path:
    config = load_config()
    raw = config.get("storage_dir")
    if raw:
        return Path(raw)
    return DEFAULT_STORAGE_DIR


def set_storage_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    config = load_config()
    config["storage_dir"] = str(path)
    save_config(config)
    return path


def ensure_storage_dir(path: Optional[Path] = None) -> Path:
    target = path or get_storage_dir()
    target.mkdir(parents=True, exist_ok=True)
    set_storage_dir(target)
    return target


def get_intervals_api_key() -> Optional[str]:
    """Ottiene la API key di Intervals.icu"""
    config = load_config()
    return config.get("intervals_api_key")


def set_intervals_api_key(api_key: str) -> None:
    """Salva la API key di Intervals.icu (senza spazi)"""
    config = load_config()
    config["intervals_api_key"] = api_key.strip()
    save_config(config)


def clear_intervals_api_key() -> None:
    """Rimuove la API key"""
    config = load_config()
    config.pop("intervals_api_key", None)
    save_config(config)
