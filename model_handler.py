# model_handler.py
import os
import subprocess
import uuid
from pathlib import Path

OUT_DIR = Path("outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_from_text(prompt: str, out_format: str = "glb", steps: int = 64) -> str:
    """
    Generate a 3D model from text prompt using Shap-E.
    This function tries to call a Shap-E example script (the repo includes a sample_text_to_3d.ipynb).
    If you installed shap-e as a package that exposes a CLI or Python API, replace the subprocess call with the API call.

    Returns:
        filepath to generated model (str)
    """
    uid = uuid.uuid4().hex[:8]
    out_name = f"model_{uid}.{out_format}"
    out_path = OUT_DIR / out_name

    # OPTION A: If you installed shap-e and have a sample script that writes a .glb
    # Replace 'path/to/sample_text_to_3d.py' with the actual script in your shap-e install.
    # The example below assumes there's a script you can call like:
    # python sample_text_to_3d.py --prompt "a wooden chair" --out outputs/model.glb --steps 64
    # If you don't have a script, use the Shap-E Python API per repo docs (see README).
    shap_e_script = Path("shap-e/examples/sample_text_to_3d.py")
    if shap_e_script.exists():
        cmd = [
            "python",
            str(shap_e_script),
            "--prompt", prompt,
            "--out", str(out_path),
            "--steps", str(steps)
        ]
        # You may need to adjust arguments depending on the repo script signature.
        print("Running Shap-E script:", " ".join(cmd))
        subprocess.check_call(cmd)
        if out_path.exists():
            return str(out_path)
        else:
            raise RuntimeError(f"Shap-E script did not produce output at {out_path}")

    # OPTION B: If shap-e installed as a package, try a python -c snippet (example only)
    try:
        import shap_e  # type: ignore
        # If shap_e exposes an API to produce mesh, call it here.
        # The actual API details depend on the version you installed. See the repo README.
        raise NotImplementedError("Shap-E is installed but automatic API wrapper isn't implemented in this template. "
                                  "Open model_handler.py and implement the API call per your shap-e version.")
    except ImportError:
        raise RuntimeError(
            "Shap-E not installed or sample script not found. "
            "Please run setup_shap_e.sh and follow the Shap-E README. "
            "See https://github.com/openai/shap-e for usage examples."
        )
