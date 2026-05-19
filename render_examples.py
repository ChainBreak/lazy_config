"""Render all examples into a single EXAMPLES.md file.

Discovers every examples/example_*.py file (sorted), runs each one,
captures its output, then writes EXAMPLES.md containing the source code
and the captured output side-by-side in clean markdown.

Each example is run with cwd set to examples/configs/ so that
GhostConfig.create("training.yaml") resolves correctly. The project root
is added to PYTHONPATH so ghostconfig is importable without being installed.
"""
import os
import pathlib
import subprocess
import sys
import textwrap

EXAMPLES_DIR = pathlib.Path(__file__).parent / "examples"
CONFIGS_DIR = EXAMPLES_DIR / "configs"
YAML_PATH = CONFIGS_DIR / "training.yaml"
OUTPUT_PATH = pathlib.Path(__file__).parent / "EXAMPLES.md"
PROJECT_ROOT = pathlib.Path(__file__).parent


def discover_example_paths() -> list[pathlib.Path]:
    return sorted(EXAMPLES_DIR.glob("example_*.py"))


def run_example(path: pathlib.Path) -> tuple[str, int]:
    example_text = path.read_text()
    indented_example = textwrap.indent(example_text, "    ")
    script = f"try:\n{indented_example}\nexcept Exception as exception:\n    print(exception)\n"
    environment = {**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=CONFIGS_DIR,
        env=environment,
    )
    return result.stdout, result.returncode


def extract_docstring(source: str) -> str:
    """Return the first triple-quoted docstring, stripped of indentation."""
    stripped = source.lstrip()
    for quote in ('"""', "'''"):
        if stripped.startswith(quote):
            end = stripped.index(quote, len(quote))
            raw = stripped[len(quote):end]
            return textwrap.dedent(raw).strip()
    return ""


def format_example_section(path: pathlib.Path, source: str, output: str, exit_code: int) -> str:
    number = path.stem  # e.g. "example_01"
    title = number.replace("_", " ").title()

    docstring = extract_docstring(source)
    description = f"\n{docstring}\n" if docstring else ""

    output_block = output.rstrip()
    if exit_code != 0:
        output_label = "Output (error)"
    else:
        output_label = "Output"

    return (
        f"## {title}\n"
        f"{description}\n"
        f"### Code\n\n"
        f"```python\n{source.rstrip()}\n```\n\n"
        f"### {output_label}\n\n"
        f"```\n{output_block}\n```\n"
    )


def build_markdown(sections: list[str], yaml_content: str) -> str:
    header = (
        "# GhostConfig Examples\n\n"
        "Each example below is a self-contained script demonstrating one "
        "aspect of `GhostConfig`. The output shown was produced by running "
        "the script directly.\n\n"
        "## Config file: `training.yaml`\n\n"
        "All examples load from this shared config file:\n\n"
        f"```yaml\n{yaml_content.rstrip()}\n```\n"
    )
    return header + "\n---\n\n" + "\n---\n\n".join(sections)


def main() -> None:
    example_paths = discover_example_paths()
    if not example_paths:
        print(f"No example files found in {EXAMPLES_DIR}")
        sys.exit(1)

    yaml_content = YAML_PATH.read_text()

    sections = []
    for path in example_paths:
        print(f"Running {path.name} …", end=" ", flush=True)
        source = path.read_text()
        output, exit_code = run_example(path)
        status = "ok" if exit_code == 0 else f"exit {exit_code}"
        print(status)
        sections.append(format_example_section(path, source, output, exit_code))

    markdown = build_markdown(sections, yaml_content)
    OUTPUT_PATH.write_text(markdown)
    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
