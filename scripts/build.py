#!/usr/bin/env python3
"""Portrait + info card + heatmap + README tek komut."""

from __future__ import annotations

import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
os.chdir(ROOT)
sys.path.insert(0, HERE)

from config import DISPLAY_NAME, ROLE, prompt_user  # noqa: E402


def run(script: str) -> None:
    path = os.path.join(HERE, script)
    print(f"\n==> {script}")
    runpy.run_path(path, run_name="__main__")


def write_readme() -> None:
    user = prompt_user()
    readme = f"""<div align="center">
  <h3><code>{user}@github ~ $ ./contributions.sh</code></h3>
  <img src="./contrib-heatmap.svg" width="860" alt="contribution heatmap" />
  <br/><br/>
  <h3><code>{user}@github ~ $ whoami</code></h3>
  <table>
    <tr>
      <td valign="top"><img src="./portrait-ascii.svg" width="370" alt="ascii portrait" /></td>
      <td valign="top"><img src="./info-card.svg" width="490" alt="neofetch info card" /></td>
    </tr>
  </table>
  <p>{DISPLAY_NAME} · {ROLE}</p>
</div>
"""
    path = os.path.join(ROOT, "README.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(readme)
    print("wrote", path)


def main() -> None:
    run("make_ascii_svg.py")
    run("make_info_card.py")
    try:
        run("fetch_contributions.py")
    except SystemExit as exc:
        print("fetch skipped:", exc)
    run("render_heatmap_svg.py")
    write_readme()
    print("\ndone. username/username reposuna pushla, Actions'tan bir kere manuel çalıştır.")


if __name__ == "__main__":
    main()
