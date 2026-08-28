import codecs
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# ============================================================
# Controller / SDK configuration
# ============================================================

CONTROLLERS = [
    ("YRC1000", Path(r"C:\Program Files (x86)\Yaskawa\MotoPlusIDE_YRC")),
    ("YRC1000u", Path(r"C:\Program Files (x86)\Yaskawa\MotoPlusIDE_YRCmicro")),
    ("DX200", Path(r"C:\Program Files (x86)\Yaskawa\MotoPlusIDE_DN")),
    ("FS100", Path(r"C:\Program Files (x86)\Yaskawa\MotoPlusIDE_FS")),
]


# ============================================================
# Project configuration
# ============================================================

# Source directory is the folder containing this Python script.
SOURCE_DIR = Path(__file__).resolve().parent

OUT = SOURCE_DIR / "output"

# ============================================================
# Source files
# ============================================================

SOURCE_FILES = [
    "debug.c",
    "Controller.c",
    "CtrlGroup.c",
    "IoServer.c",
    "MotionServer.c",
    "mpMain.c",
    "SimpleMessage.c",
    "StateServer.c",
]


# ============================================================
# Helper functions
# ============================================================


def run_command(command, description):
    """Run a command and stop the build if it fails."""

    print()
    print(description)
    print("-" * 60)

    print(" ".join(f'"{arg}"' if " " in str(arg) else str(arg) for arg in command))
    print()

    result = subprocess.run(command)

    if result.returncode != 0:
        print()
        print("=" * 60)
        print(f"BUILD FAILED: {description}")
        print(f"Exit code: {result.returncode}")
        print("=" * 60)
        sys.exit(result.returncode)


def get_compiler(sdk, controller):
    """Return the appropriate compiler for the controller."""

    if controller == "FS100":
        return (
            sdk
            / "mpbuilder"
            / "gnu"
            / "4.1.2-vxworks-6.8"
            / "x86-win32"
            / "bin"
            / "ccppc.exe"
        )

    return (
        sdk
        / "mpbuilder"
        / "gnu"
        / "4.3.3-vxworks-6.9"
        / "x86-win32"
        / "bin"
        / "ccpentium.exe"
    )


def get_application_version(source_dir):
    """
    Extract APPLICATION_VERSION from MotoROS.h.

    Expected format:

        #define APPLICATION_VERSION    "1.9.12.4"
    """

    version_file = source_dir / "MotoROS.h"

    if not version_file.is_file():
        print("ERROR: MotoROS.h not found:")
        print(f"  {version_file}")
        sys.exit(1)

    content = version_file.read_text(encoding="utf-8")

    match = re.search(
        r'^\s*#define\s+APPLICATION_VERSION\s+"([^"]+)"',
        content,
        re.MULTILINE,
    )

    if not match:
        print("ERROR: APPLICATION_VERSION not found in:")
        print(f"  {version_file}")
        sys.exit(1)

    version = match.group(1)

    print(f"Application version: {version}")

    return version


def compile_file(compiler, sdk, filename, controller, output_dir):
    """Compile one C source file."""

    source_dir = SOURCE_DIR

    source = source_dir / filename
    output = output_dir / f"{source.stem}.a"

    # ========================================================
    # FS100 compile command
    # ========================================================

    if controller == "FS100":
        command = [
            str(compiler),
            "-g",
            "-te500v2",
            "-fno-builtin",
            "-fsigned-char",
            "-Wall",
            "-Werror-implicit-function-declaration",
            "-DCPU=PPC32",
            "-DTOOL_FAMILY=gnu",
            "-DTOOL=e500v2gnu",
            "-D_WRS_KERNEL",
            "-DFS100",
            f"-I{source_dir}",
            f"-I{sdk / 'mpbuilder' / 'inc'}",
            "-c",
            str(source),
            "-o",
            str(output),
        ]

    # ========================================================
    # Existing compile command for other controllers
    # ========================================================

    else:
        command = [
            str(compiler),
            "-march=atom",
            "-nostdlib",
            "-fno-builtin",
            "-fno-defer-pop",
            "-fno-implicit-fp",
            "-fno-zero-initialized-in-bss",
            "-Wall",
            "-Werror-implicit-function-declaration",
            "-g",
            "-MD",
            "-MP",
            "-DCPU=_VX_ATOM",
            "-DTOOL_FAMILY=gnu",
            "-DTOOL=gnu",
            "-D_WRS_KERNEL",
            f"-D{controller}",
            f"-I{source_dir}",
            f"-I{sdk / 'mpbuilder' / 'inc'}",
            "-c",
            str(source),
            "-o",
            str(output),
        ]

    run_command(command, f"[{controller}] Compiling {filename}")


def build_output(compiler, controller, version, output_dir):
    """Link all object files into a versioned, controller-specific .out file."""

    object_files = [
        "Controller.a",
        "CtrlGroup.a",
        "debug.a",
        "IoServer.a",
        "MotionServer.a",
        "mpMain.a",
        "ParameterExtraction.a",
        "SimpleMessage.a",
        "StateServer.a",
    ]

    output = output_dir / f"MotoRos{controller.replace('0', '')}_{version}.out"

    command = [
        str(compiler),
        "-nostdlib",
        "-r",
        "-WI,-X",
        "-WI",
        *[str(output_dir / obj) for obj in object_files],
        "-o",
        str(output),
    ]

    run_command(command, f"[{controller}] Building {output.name}")

    return output


# ============================================================
# Build one controller
# ============================================================


def build_controller(controller, sdk):
    """Build the project using a specific MotoPlus SDK."""

    print()
    print("=" * 60)
    print(f"Building controller: {controller}")
    print(f"SDK: {sdk}")
    print("=" * 60)

    compiler = get_compiler(sdk, controller)
    source_dir = SOURCE_DIR

    if not sdk.is_dir():
        print("ERROR: SDK directory not found:")
        print(f"  {sdk}")
        sys.exit(1)

    if not compiler.is_file():
        print("ERROR: Compiler not found:")
        print(f"  {compiler}")
        sys.exit(1)

    if not source_dir.is_dir():
        print("ERROR: Source directory not found:")
        print(f"  {source_dir}")
        sys.exit(1)

    # Extract version from MotoROS.h.
    version = get_application_version(source_dir)

    # Create a controller-specific output directory.
    output_dir = OUT / controller

    # Clean output directory before compilation
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Source directory: {source_dir}")
    print(f"Output directory: {output_dir}")

    for filename in SOURCE_FILES:
        compile_file(
            compiler,
            sdk,
            filename,
            controller,
            output_dir,
        )

    copy_paremeter_extraction_lib(controller, output_dir)

    output_file = build_output(
        compiler,
        controller,
        version,
        output_dir,
    )

    shutil.copy2(output_file, OUT)

    print()
    print(f"[{controller}] Build successful!")
    print(f"Output: {output_file}")


def copy_paremeter_extraction_lib(controller, output_dir):
    # Copy the controller-specific ParameterExtraction library
    parameter_extraction_libs = {
        "DX200": "ParameterExtraction.dnLib",
        "FS100": "ParameterExtraction.fsLib",
        "YRC1000": "ParameterExtraction.yrcLib",
        "YRC1000u": "ParameterExtraction.yrcmLib",
    }

    source_lib = SOURCE_DIR / parameter_extraction_libs[controller]
    target_lib = output_dir / "ParameterExtraction.a"

    print(f"Copying {source_lib.name} -> {target_lib.name}")
    shutil.copy2(source_lib, target_lib)


# ============================================================
# Main
# ============================================================


def main():
    print("=" * 60)
    print("MotoPlus Multi-Controller Build")
    print("=" * 60)

    print(f"Script/source directory: {SOURCE_DIR}")

    os.environ["WIND_BASE"] = "C:\\"
    os.environ["WIND_HOST_TYPE"] = "x86-win32"
    os.environ["WIND_USR"] = "C:\\"

    # remove BOM from source files so the compiler does not complain
    for path in SOURCE_DIR.glob("*.[ch]"):
        with open(path, "rb") as f:
            has_bom = f.read(3) == codecs.BOM_UTF8

        if has_bom:
            text = path.read_text(encoding="utf-8-sig")
            path.write_text(text, encoding="utf-8")
            print(f"Removed BOM: {path}")

    for controller, sdk in CONTROLLERS:
        build_controller(controller, sdk)

    print()
    print("=" * 60)
    print("All builds successful!")
    print("=" * 60)


if __name__ == "__main__":
    main()
