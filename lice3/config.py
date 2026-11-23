"""Setup configuration for lice3."""

import os
import sys
from dataclasses import dataclass, fields
from pathlib import Path
from typing import ClassVar

from rich.console import Console
from rich.panel import Panel

from lice3.constants import LICENSES

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - only used on Python 3.10
    import tomli as tomllib

APP_NAME = "lice"
SETTINGS_FILE_NAME = "config.toml"
SETTINGS_SECTION = "lice"


def _config_folder() -> Path:
    """Return the folder that holds the lice configuration file.

    ``XDG_CONFIG_HOME`` is honoured when set, otherwise ``~/.config`` is used.
    This matches the documented behaviour on every supported operating system.
    """
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config_home) if xdg_config_home else Path.home() / ".config"
    return base / APP_NAME


def _warn(message: str) -> None:
    """Print a non-fatal warning to stderr."""
    console = Console(stderr=True, width=80)
    console.print()
    console.print(
        Panel(
            message,
            title="[b]Warning[/b]",
            title_align="left",
            expand=False,
            style="yellow",
        )
    )


@dataclass
class Settings:
    """Settings for lice3."""

    default_license: str = "bsd3"
    organization: str = ""
    legacy: bool = False
    clipboard: bool = False

    settings_file_name: ClassVar[str] = SETTINGS_FILE_NAME

    @staticmethod
    def get_settings_folder() -> Path:
        """Return the folder that contains the settings file."""
        return _config_folder()

    def get_settings_path(self) -> Path:
        """Return the full path to the settings file."""
        return self.get_settings_folder() / self.settings_file_name

    def update_from(self, values: dict[str, object]) -> None:
        """Override known fields with type-compatible values from ``values``."""
        for field in fields(self):
            if field.name not in values:
                continue
            value = values[field.name]
            if isinstance(value, type(getattr(self, field.name))):
                setattr(self, field.name, value)


def _load_settings() -> Settings:
    """Load the settings from the optional TOML configuration file."""
    loaded = Settings()
    path = loaded.get_settings_path()
    if not path.is_file():
        return loaded

    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        _warn(f"Could not read the configuration file '[b]{path}[/b]': {error}")
        return loaded

    section = data.get(SETTINGS_SECTION)
    if isinstance(section, dict):
        loaded.update_from(section)
    return loaded


def check_default_license() -> str:
    """Check the default license is in the list of available licenses.

    Return the default license if it is in the list, otherwise return "bsd3".
    This is only used to ensure that the configuration file does not have an
    invalid default license hence crashing the application, and will be called
    automatically by 'Typer'
    """
    if settings.default_license not in LICENSES:
        console = Console(width=80)
        error_text = (
            f"[red]Invalid default license '[b]{settings.default_license}"
            "'[/b] in the configuration file, falling back to '[b]bsd3[/b]', "
            "unless specified otherwise on the command line.\n\nCheck that [b]"
            f"{settings.get_settings_path()}"
            "[/b]' has a valid value for [b]'default_license'[/b]."
        )
        panel = Panel(
            error_text,
            title="[b]Error[/b]",
            title_align="left",
            expand=False,
            style="red",
        )

        console.print()
        console.print(panel)
        settings.default_license = "bsd3"
    return settings.default_license


settings = _load_settings()
