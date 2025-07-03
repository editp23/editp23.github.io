import os

# --- Configuration ---

# 1. The directory where your numbered model folders are located.
INPUT_MODEL_DIR = "static/media/recon"

# 2. A mapping from the folder name to the desired title on the card.
MODEL_TITLES = {
    "1": "Cartoonish car",
    "2": "Car with wings",
    "3": "Fox with open eyes",
    "4": "Golden R2D2",
    "5": "Robot with sunglasses",
    "6": "Terrier with beanie",
    "7": "Batman with backpack",
    "8": "Grogu with red robe",
    "9": "Fox with tuxedo",
    "10": "Gothic cathedral",
    "11": "Terrier with Paddington's hat",
    "12": "Vespa",
    "13": "Grogu in the-force pose",
    "14": "Superman in Superman pose",
    "15": "Batmobile",
    "16": "Lego figure of Grogu"
}

# --- HTML Template for a single card ---

def create_card_html(folder_name):
    """Generates the complete HTML for one card in the gallery."""
    
    title = MODEL_TITLES.get(folder_name, f"Model {folder_name}")

    model_src = f"static/media/recon/{folder_name}/src.glb"
    model_ours = f"static/media/recon/{folder_name}/ours-conv.glb"
    model_neutral = f"static/media/recon/{folder_name}/ours-conv-neutral.glb"

    # UPDATED: Removed 'auto-rotate' from the model-viewer tags by default.
    return f"""
    <div class="column is-one-quarter-desktop is-half-tablet gallery-item is-hidden-by-pagination">
      <div class="card model-card">
        <div class="model-grid">
          <figure class="image">
            <model-viewer data-src="{model_src}" alt="Original {title}" camera-controls camera-orbit="-45deg 90deg auto" shadow-intensity="1"></model-viewer>
            <figcaption class="has-text-centered is-size-7 mt-1">Original</figcaption>
          </figure>
          <figure class="image">
            <model-viewer data-src="{model_ours}" alt="Edited {title}" camera-controls camera-orbit="-45deg 90deg auto" shadow-intensity="1"></model-viewer>
            <figcaption class="has-text-centered is-size-7 mt-1">Edited</figcaption>
          </figure>
          <figure class="image">
            <model-viewer data-src="{model_neutral}" alt="Un-textured {title}" camera-controls camera-orbit="-45deg 90deg auto" shadow-intensity="1"></model-viewer>
            <figcaption class="has-text-centered is-size-7 mt-1">No texture</figcaption>
          </figure>
        </div>
        <p class="has-text-centered is-size-6 mt-3">{title}</p>
      </div>
    </div>"""

# --- Main script execution ---

def generate_full_section():
    """Finds all model folders and prints the complete HTML section with responsive pagination logic."""
    try:
        subfolders = [f for f in os.listdir(INPUT_MODEL_DIR) if os.path.isdir(os.path.join(INPUT_MODEL_DIR, f))]
        subfolders.sort(key=int)
    except (FileNotFoundError, ValueError):
        print(f"Error: Could not find or sort numbered subfolders in '{INPUT_MODEL_DIR}'.")
        return

    all_cards_html = "".join([create_card_html(folder) for folder in subfolders])

    full_section_html = f"""
<!-- ===================================================================
     Auto-Generated Responsive Paginated Gallery
     =================================================================== -->
<section class="section" id="recon-gallery">
  <div class="container is-max-desktop">
    <h2 class="title is-3 has-text-centered mb-5">
      Interactive 3D Reconstruction Gallery
    </h2>
  
    <div id="model-gallery-container" class="columns is-multiline is-variable is-4">
      {all_cards_html.strip()}
    </div>
    
    <div id="gallery-pagination" class="buttons is-centered mt-5"></div>
  </div>
</section>

<!-- Styles and Script for the Responsive Paginated Gallery -->
<style>
  .is-hidden-by-pagination {{
    display: none !important;
  }}
  @media screen and (max-width: 768px) {{
    #recon-gallery.section {{
      padding: 2rem 1rem;
    }}
    #model-gallery-container.columns {{
        justify-content: center;
    }}
    #model-gallery-container > .gallery-item {{
        flex: 0 0 85%;
        width: 85%;
    }}
  }}
</style>
"""
    print(full_section_html)

if __name__ == "__main__":
    generate_full_section()
