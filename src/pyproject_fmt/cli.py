"""CLI interface parser."""

from __future__ import annotations

import os
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    ArgumentTypeError,
    Namespace,
)
from importlib.metadata import version
from pathlib import Path
from typing import Sequence

from packaging.version import Version

from .config import DEFAULT_INDENT, DEFAULT_MAX_SUPPORTED_PYTHON, Config


class PyProjectFmtNamespace(Namespace):
    """Options for pyproject-fmt tool."""

    inputs: list[Path]
    stdout: bool
    indent: int
    check: bool
    keep_full_version: bool
    max_supported_python: Version

    @property
    def configs(self) -> list[Config]:
        """:return: configurations"""
        return [
            Config(
                pyproject_toml=toml,
                toml=toml.read_text(encoding="utf-8"),
                indent=self.indent,
                keep_full_version=self.keep_full_version,
                max_supported_python=self.max_supported_python,
            )
            for toml in self.inputs
        ]


def pyproject_toml_path_creator(argument: str) -> Path:
    """
    Validate that pyproject.toml can be formatted.

    :param argument: the string argument passed in
    :return: the pyproject.toml path
    """
    path = Path(argument).absolute()
    if path.is_dir():
        path /= "pyproject.toml"
    if not path.exists():
        msg = "path does not exist"
        raise ArgumentTypeError(msg)
    if not path.is_file():
        msg = "path is not a file"
        raise ArgumentTypeError(msg)
    if not os.access(path, os.R_OK):
        msg = "cannot read path"
        raise ArgumentTypeError(msg)
    if not os.access(path, os.W_OK):
        msg = "cannot write path"
        raise ArgumentTypeError(msg)
    return path


def _build_cli() -> ArgumentParser:
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        prog="pyproject-fmt",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        help="print package version of pyproject_fmt",
        version=f"%(prog)s ({version('pyproject-fmt')})",
    )
    group = parser.add_mutually_exclusive_group()
    msg = "print the formatted text to the stdout (instead of update in-place)"
    group.add_argument("-s", "--stdout", action="store_true", help=msg)
    msg = "check and fail if any input would be formatted, printing any diffs"
    group.add_argument("--check", action="store_true", help=msg)
    msg = "keep full dependency versions. For example do not change version 1.0.0 to 1"
    parser.add_argument("--keep-full-version", action="store_true", help=msg)
    parser.add_argument(
        "--indent",
        type=int,
        default=DEFAULT_INDENT,
        help="number of spaces to indent",
    )
    parser.add_argument(
        "--max-supported-python",
        type=Version,
        default=DEFAULT_MAX_SUPPORTED_PYTHON,
        help="latest Python version the project supports (e.g. 3.13)",
    )
    msg = "pyproject.toml file(s) to format"
    parser.add_argument("inputs", nargs="+", type=pyproject_toml_path_creator, help=msg)
    return parser


def cli_args(args: Sequence[str]) -> PyProjectFmtNamespace:
    """
    Load the tools options.

    :param args: CLI arguments
    :return: the parsed options
    """
    parser = _build_cli()
    result = PyProjectFmtNamespace()
    parser.parse_args(namespace=result, args=args)
    return result


__all__ = [
    "PyProjectFmtNamespace",
    "cli_args",
]
