# noqa: I002
# typer needs to evaluate the type annotations so can't use __future__.annotations here

import sys
from ast import Module, parse, unparse
from pathlib import Path
from shutil import copyfile, rmtree
from tomllib import loads
from typing import Optional, cast

from tomli_w import dumps
from typer import run

from python_transpiler.main import transpile
from python_transpiler.utils import parse_python_version


def typer_main(
    output_dir: Path = Path("transpiled"),
    # typer doesn't support union with None https://github.com/tiangolo/typer/issues/533
    target: Optional[str] = None,  # noqa: UP007
    compile_all: bool = False,  # noqa: FBT002, FBT001
):
    if output_dir.exists():
        rmtree(output_dir)
    # TODO: figure out a better way to compile wheels that doesnt rely on it being a
    # pdm project.
    # https://github.com/DetachHead/python-transpiler/issues/15
    pyproject_toml = loads(  # type:ignore[no-any-expr]
        Path("pyproject.toml").read_text()
    )
    project_config: dict[str, object] = pyproject_toml[  # type:ignore[no-any-expr]
        "project"
    ]
    package_name = cast(str, project_config["name"])
    input_path = Path("." if compile_all else package_name).resolve()

    if not input_path.is_dir():
        raise Exception(f"package directory not found: {input_path}")
    # extremely cringe:
    input_files = [
        input_file
        for input_file in input_path.rglob("*")
        if input_file.is_file()
        and "__pycache__" not in input_file.parts
        and output_dir.resolve() not in input_file.parents
        and not [part for part in input_file.parts if part.startswith(".")]
    ]
    parent = input_path
    polyfills = set()
    for input_file in input_files:
        module: Module | None = None
        if input_file.suffix.lower() == ".py":
            module = parse(input_file.read_text(), input_file)
            polyfills.update(
                transpile(
                    module,
                    (
                        parse_python_version(target)
                        if target
                        else (sys.version_info[0], sys.version_info[1])
                    ),
                )
            )
        output_file = (
            output_dir
            / ("." if compile_all else package_name)
            / input_file.relative_to(parent)
        )
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(unparse(module))

    if polyfills:
        if "dependencies" not in project_config:
            project_config["dependencies"] = {}
        lockfile = output_dir / "poetry.lock"
        # if we need to change the deps we can't use the lockfile
        if lockfile.exists():
            lockfile.unlink()
    for polyfill in polyfills:
        project_config["dependencies"] += polyfill  # type:ignore[operator]
    (output_dir / "pyproject.toml").write_text(
        dumps(pyproject_toml)  # type:ignore[no-any-expr]
    )
    readme_file = cast(str | None, project_config.get("readme"))
    if readme_file:
        copyfile(readme_file, output_dir / Path(readme_file).name)


def main():
    run(typer_main)


if __name__ == "__main__":
    main()
