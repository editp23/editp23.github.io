import pathlib
import sys
from textwrap import dedent

# ----------------------------------------------------------------------
RECON_ROOT  = pathlib.Path("static/media/recon")
EDIT_LABEL  = "Edited"          # default caption under edited mesh
NEUTRAL_LAB = "No texture"      # caption under neutral mesh
VIEWER_HEIGHT = 220             # px (keep in sync with CSS)
# ----------------------------------------------------------------------

def html_triplet(folder: pathlib.Path) -> str:
    """Return formatted HTML for one sub-folder."""
    idx  = folder.name
    base = f"static/media/recon/{idx}"

    return dedent(f"""
    <div class="column is-one-quarter-desktop is-half-tablet">
      <div class="card model-card">
        <div class="model-grid">

          <figure class="image">
            <model-viewer src="{base}/src.glb"
                          alt="Original mesh {idx}"
                          camera-controls auto-rotate
                          camera-orbit="-45deg 90deg auto" shadow-intensity="1"
                          style="height:{VIEWER_HEIGHT}px">
            </model-viewer>
            <figcaption class="has-text-centered is-size-7 mt-1">Original</figcaption>
          </figure>

          <figure class="image">
            <model-viewer src="{base}/ours-conv.glb"
                          alt="Edited mesh {idx}"
                          camera-controls auto-rotate
                          camera-orbit="-45deg 90deg auto" shadow-intensity="1"
                          style="height:{VIEWER_HEIGHT}px">
            </model-viewer>
            <figcaption class="has-text-centered is-size-7 mt-1">{EDIT_LABEL}</figcaption>
          </figure>

          <figure class="image">
            <model-viewer src="{base}/ours-conv-neutral.glb"
                          alt="Un-textured edit {idx}"
                          camera-controls auto-rotate
                          camera-orbit="-45deg 90deg auto" shadow-intensity="1"
                          style="height:{VIEWER_HEIGHT}px">
            </model-viewer>
            <figcaption class="has-text-centered is-size-7 mt-1">{NEUTRAL_LAB}</figcaption>
          </figure>

        </div>
        <p class="has-text-centered is-size-6 mt-3">Subfolder&nbsp;{idx}</p>
      </div>
    </div>
    """).strip()


def main() -> None:
    if not RECON_ROOT.exists():
        sys.exit(f"Directory not found: {RECON_ROOT}")

    # Sort numeric folder names (1, 2 … 10 … 23)
    folders = sorted(
        (p for p in RECON_ROOT.iterdir() if p.is_dir()),
        key=lambda p: int(p.name) if p.name.isdigit() else p.name
    )

    html_blocks = [html_triplet(f) for f in folders]
    print("\n\n".join(html_blocks))


if __name__ == "__main__":
    main()
