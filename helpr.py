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

    # The 'gallery-item' class is used by the new JavaScript
    return f"""
    <div class="column is-one-quarter-desktop is-half-tablet gallery-item">
      <div class="card model-card">
        <div class="model-grid">
          <figure class="image">
            <model-viewer data-src="{model_src}" alt="Original {title}" camera-controls auto-rotate camera-orbit="-45deg 90deg auto" shadow-intensity="1"></model-viewer>
            <figcaption class="has-text-centered is-size-7 mt-1">Original</figcaption>
          </figure>
          <figure class="image">
            <model-viewer data-src="{model_ours}" alt="Edited {title}" camera-controls auto-rotate camera-orbit="-45deg 90deg auto" shadow-intensity="1"></model-viewer>
            <figcaption class="has-text-centered is-size-7 mt-1">Edited</figcaption>
          </figure>
          <figure class="image">
            <model-viewer data-src="{model_neutral}" alt="Un-textured {title}" camera-controls auto-rotate camera-orbit="-45deg 90deg auto" shadow-intensity="1"></model-viewer>
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

    # Generate the HTML for all cards
    all_cards_html = "".join([create_card_html(folder) for folder in subfolders])

    # Assemble the final, self-contained section HTML
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
    
    <!-- This div will be populated with pagination buttons by the script -->
    <div id="gallery-pagination" class="buttons is-centered mt-5"></div>
  </div>
</section>

<!-- Styles and Script for the Responsive Paginated Gallery -->
<style>
  /* Hide all gallery items by default. JS will show the correct ones. */
  .gallery-item {{
    display: none;
  }}
</style>

<script>
  document.addEventListener('DOMContentLoaded', () => {{
    const galleryContainer = document.getElementById('model-gallery-container');
    const paginationContainer = document.getElementById('gallery-pagination');
    
    if (!galleryContainer) return;

    const allItems = Array.from(galleryContainer.querySelectorAll('.gallery-item'));
    let activeModels = [];

    const activateModels = (itemsToShow) => {{
      // Deactivate previously active models to save resources
      activeModels.forEach(viewer => viewer.removeAttribute('src'));
      activeModels = [];

      // Activate models for the new set of items
      itemsToShow.forEach(item => {{
        const viewers = item.querySelectorAll('model-viewer');
        viewers.forEach(viewer => {{
          if (viewer.dataset.src && !viewer.getAttribute('src')) {{
            viewer.setAttribute('src', viewer.dataset.src);
            activeModels.push(viewer);
          }}
        }});
      }});
    }};
    
    const showPage = (pageNumber, itemsPerPage) => {{
        const startIndex = (pageNumber - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const itemsToShow = [];

        allItems.forEach((item, index) => {{
            if (index >= startIndex && index < endIndex) {{
                item.style.display = 'block';
                itemsToShow.push(item);
            }} else {{
                item.style.display = 'none';
            }}
        }});
        activateModels(itemsToShow);
    }};

    const setupPagination = () => {{
        const isMobile = window.innerWidth <= 768;
        const itemsPerPage = isMobile ? 4 : 8;
        const totalPages = Math.ceil(allItems.length / itemsPerPage);

        paginationContainer.innerHTML = ''; // Clear old buttons

        if (totalPages > 1) {{
            for (let i = 1; i <= totalPages; i++) {{
                const button = document.createElement('button');
                button.className = 'button pagination-btn';
                button.dataset.page = i;
                button.textContent = `Page ${{i}}`;
                if (i === 1) {{
                    button.classList.add('is-link');
                }}
                
                button.addEventListener('click', () => {{
                    // Update button styles
                    paginationContainer.querySelectorAll('.pagination-btn').forEach(btn => btn.classList.remove('is-link'));
                    button.classList.add('is-link');
                    // Show the correct page
                    showPage(i, itemsPerPage);
                }});
                paginationContainer.appendChild(button);
            }}
        }}
        
        // Show the first page initially
        showPage(1, itemsPerPage);
    }};

    // Setup pagination on initial load and on window resize
    setupPagination();
    window.addEventListener('resize', setupPagination);
  }});
</script>
"""
    print(full_section_html)

if __name__ == "__main__":
    generate_full_section()
