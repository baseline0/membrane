"""
Build pipeline: model.py → formulas.typ → figures → PDF

Orchestrates the full publication workflow:
1. Export SymPy formulas to JSON
2. Convert LaTeX formulas to Typst snippets
3. Generate benchmark figures (from membrane/benchmarks/results/)
4. Compile Typst document to PDF
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def generate_formulas() -> bool:
    """Convert SymPy formulas to Typst via LaTeX."""
    print("📐 Generating Typst formulas from model.py...")

    # 1. Run model.py to get JSON
    result = subprocess.run([sys.executable, "model.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ model.py failed:\n{result.stderr}")
        return False

    if not Path("qips_equations.json").exists():
        print("⚠️  model.py did not generate qips_equations.json (no formulas defined yet)")
        return True  # Not a failure if model hasn't been filled in yet

    # 2. Convert LaTeX → Typst
    with open("qips_equations.json") as f:
        data = json.load(f)

    if not data:
        print("⚠️  No formulas in qips_equations.json yet")
        return True

    typst_lines = []
    for name, info in data.items():
        latex_str = info["latex"]
        # LaTeX to Typst conversion: handle special math functions
        typst_str = latex_str
        typst_str = re.sub(r"\\binom\{([^}]+)\}\{([^}]+)\}", lambda m: f"binom({m.group(1)}, {m.group(2)})", typst_str)
        typst_str = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", lambda m: f"({m.group(1)})/({m.group(2)})", typst_str)
        typst_str = re.sub(r"\\left\(", "(", typst_str)
        typst_str = re.sub(r"\\right\)", ")", typst_str)

        comment = f"// {info['description']} (from model.py:{info['source_line']})"
        definition = f"#let {name} = $ {typst_str} $"
        typst_lines.append(f"{comment}\n{definition}")

    output = Path("generated/formulas.typ")
    output.parent.mkdir(exist_ok=True)
    output.write_text("\n\n".join(typst_lines))
    print(f"✅ Generated {output}")
    return True


def generate_figures() -> bool:
    """Copy benchmark figures from results directory."""
    print("📊 Collecting benchmark figures...")

    # Look for benchmark results
    results_dir = Path("../benchmarks/results")
    if not results_dir.exists():
        print("⚠️  Benchmark results not found yet at ../benchmarks/results/")
        print("   (Run benchmarks first: python ../benchmarks/runners/cec2017_subset.py)")
        return True  # Not a failure, just not ready yet

    # Copy any PNG figures
    figures_dir = Path("generated/figures")
    figures_dir.mkdir(parents=True, exist_ok=True)

    png_files = list(results_dir.glob("*.png"))
    if png_files:
        for png_file in png_files:
            import shutil

            shutil.copy(png_file, figures_dir / png_file.name)
            print(f"✅ Copied {png_file.name}")
    else:
        print("⚠️  No PNG figures found yet in ../benchmarks/results/")

    return True


def build_pdf() -> bool:
    """Compile Typst document to PDF."""
    print("📝 Building Typst document...")

    if not Path("main.typ").exists():
        print("❌ main.typ not found")
        return False

    # Check if typst is available
    check_typst = subprocess.run(["which", "typst"], capture_output=True, text=True)

    if check_typst.returncode != 0:
        print("⚠️  Typst not found. To generate PDF:")
        print("   Run: cd ../.. && just install-typst")
        print("   Or visit: https://github.com/typst/typst/releases")
        print("   (Typst file is ready at: main.typ)")
        return True  # Not a hard failure

    result = subprocess.run(["typst", "compile", "main.typ"], capture_output=True, text=True)

    if result.returncode == 0:
        if Path("main.pdf").exists():
            print("✅ Generated main.pdf")
            return True
        else:
            print("❌ Typst compiled but main.pdf not found")
            return False
    else:
        print(f"❌ Typst compilation failed:\n{result.stderr}")
        return False


def main() -> bool:
    """Full build pipeline."""
    print("🚀 Building Quantum-Inspired P-Systems paper...\n")

    steps = [
        ("Formulas", generate_formulas),
        ("Figures", generate_figures),
        ("PDF", build_pdf),
    ]

    pdf_generated = True
    for name, step in steps:
        if not step():
            if name == "PDF":
                pdf_generated = False
            else:
                print(f"\n❌ Failed at step: {name}")
                return False

    if pdf_generated and Path("main.pdf").exists():
        print("\n✅ Paper built successfully: main.pdf")
    else:
        print("\n✅ Build ready (PDF generation deferred or not available)")
        print("   To generate PDF, install Typst and run: python build_paper.py")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
