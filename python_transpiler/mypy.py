from mypy.build import build as mypy_build, BuildResult
from mypy.modulefinder import BuildSource
from mypy.options import Options


def build(modules: list[str]) -> BuildResult:
    o = Options()
    o.preserve_asts = True
    o.incremental = False

    return mypy_build(
        sources=[BuildSource(f"{module}.py", module) for module in modules], options=o
    )
