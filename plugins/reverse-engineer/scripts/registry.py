import shutil

TOOL_DB = {
    "rizin": {
        "install": {
            "choco": "choco install rizin",
            "brew": "brew install rizin",
            "apt": "sudo apt install rizin",
        },
        "url": "https://rizin.re",
    },
    "objdump": {
        "install": {
            "apt": "sudo apt install binutils",
            "brew": "brew install binutils",
        },
        "url": "bundled with binutils",
    },
    "readelf": {
        "install": {
            "apt": "sudo apt install binutils",
            "brew": "brew install binutils",
        },
        "url": "bundled with binutils",
    },
    "nm": {
        "install": {
            "apt": "sudo apt install binutils",
            "brew": "brew install binutils",
        },
        "url": "bundled with binutils",
    },
    "strings": {
        "install": {
            "apt": "sudo apt install binutils",
            "brew": "brew install binutils",
            "choco": "choco install binutils",
        },
        "url": "bundled with binutils",
    },
    "ilspycmd": {
        "install": {"dotnet": "dotnet tool install -g ilspycmd"},
        "url": "https://github.com/icsharpcode/ILSpy",
    },
    "monodis": {
        "install": {"apt": "sudo apt install mono-utils", "brew": "brew install mono"},
        "url": "https://www.mono-project.com",
    },
    "jadx": {
        "install": {"brew": "brew install jadx", "choco": "choco install jadx"},
        "url": "https://github.com/skylot/jadx",
    },
    "cfr": {"install": {}, "url": "https://github.com/leibnitz27/cfr"},
    "javap": {"install": {}, "url": "bundled with JDK"},
    "js-beautify": {
        "install": {"npm": "npm install -g js-beautify"},
        "url": "https://github.com/beautifier/js-beautify",
    },
    "binwalk": {
        "install": {
            "pip": "pip install binwalk",
            "apt": "sudo apt install binwalk",
            "brew": "brew install binwalk",
        },
        "url": "https://github.com/ReFirmLabs/binwalk",
    },
    "uncompyle6": {
        "install": {"pip": "pip install uncompyle6"},
        "url": "https://github.com/rocky/python-uncompyle6",
    },
    "pycdc": {"install": {}, "url": "https://github.com/zrax/pycdc"},
    "pyinstxtractor": {
        "install": {"pip": "pip install pyinstxtractor"},
        "url": "https://github.com/extremecoders-re/pyinstxtractor",
    },
    "apktool": {
        "install": {"brew": "brew install apktool", "choco": "choco install apktool"},
        "url": "https://apktool.org",
    },
    "upx": {
        "install": {
            "apt": "sudo apt install upx-ucl",
            "brew": "brew install upx",
            "choco": "choco install upx",
        },
        "url": "https://upx.github.io",
    },
    "dumpbin": {"install": {}, "url": "bundled with Visual Studio"},
    "otool": {"install": {}, "url": "bundled with Xcode"},
    "wasm-decompile": {
        "install": {"apt": "sudo apt install wabt", "brew": "brew install wabt"},
        "url": "https://github.com/WebAssembly/wabt",
    },
}

TYPE_TOOLS = {
    "PE": ["rizin", "strings", "dumpbin", "objdump"],
    "PE/.NET": ["ilspycmd", "monodis", "strings"],
    "ELF": ["rizin", "strings", "readelf", "nm", "objdump"],
    "MachO": ["rizin", "strings", "otool"],
    "MachO-Universal": ["rizin", "strings", "otool"],
    "Java-class": ["jadx", "cfr", "javap"],
    "JAR": ["jadx", "cfr", "javap"],
    "APK": ["jadx", "apktool"],
    "DEX": ["jadx"],
    "ZIP": [],
    "Python-bytecode": ["uncompyle6", "pycdc"],
    "Python-source": [],
    "JavaScript": ["js-beautify"],
    "Script": [],
    "WASM": ["wasm-decompile"],
    "BZ2": ["strings"],
    "GZIP": ["strings"],
}


def is_available(name):
    return shutil.which(name) is not None


def suggest_tools(file_type):
    return TYPE_TOOLS.get(file_type, ["strings", "rizin"])


def install_hint(tool):
    info = TOOL_DB.get(tool, {})
    installs = info.get("install", {})
    if installs:
        first = next(iter(installs.values()))
        if first:
            return first
    return info.get("url", "manual install")


def check_all():
    available = []
    missing = []
    for t in sorted(TOOL_DB):
        path = shutil.which(t)
        if path:
            available.append({"name": t, "path": path})
        else:
            missing.append({"name": t, "install": install_hint(t)})
    return {"available": available, "missing": missing}


def require(tool):
    if not is_available(tool):
        hint = install_hint(tool)
        return {"error": f"{tool} not installed", "install": hint}
    return None
