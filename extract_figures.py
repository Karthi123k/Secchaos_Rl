import os
import subprocess
import shutil

# Create figs/ directory
os.makedirs("figs", exist_ok=True)

# Define the custom styles and colors preamble
preamble = r"""\documentclass[tikz, border=10pt]{standalone}
\usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc, fit, backgrounds, decorations.pathreplacing}

% Custom Colors
\definecolor{secblue}{RGB}{0,102,179}
\definecolor{secred}{RGB}{204,51,51}
\definecolor{secgreen}{RGB}{51,153,102}
\definecolor{secorange}{RGB}{255,153,0}
\definecolor{lightgray}{RGB}{240,240,240}
\definecolor{darkgray}{RGB}{80,80,80}

% TikZ Styles
\tikzstyle{process} = [rectangle, rounded corners, minimum width=2.8cm, minimum height=0.8cm, text centered, text width=2.6cm, align=center, draw=secblue, fill=secblue!10, font=\small]
\tikzstyle{security} = [rectangle, rounded corners, minimum width=2.8cm, minimum height=0.8cm, text centered, text width=2.6cm, align=center, draw=secred, fill=secred!10, font=\small]
\tikzstyle{rlagent} = [rectangle, rounded corners, minimum width=2.8cm, minimum height=0.8cm, text centered, text width=2.6cm, align=center, draw=secgreen, fill=secgreen!10, font=\small\bfseries]
\tikzstyle{monitor} = [rectangle, rounded corners, minimum width=2.8cm, minimum height=0.8cm, text centered, text width=2.6cm, align=center, draw=secorange, fill=secorange!10, font=\small]
\tikzstyle{arrow} = [thick, ->, >=Stealth]
\tikzstyle{darrow} = [thick, <->, >=Stealth]
"""

# Let's extract the TikZ figures from ica2s.tex
with open("ica2s.tex", "r") as f:
    content = f.read()

# Helper function to extract tikzpicture blocks
def extract_tikz_blocks(text):
    blocks = []
    start = 0
    while True:
        pos = text.find(r"\begin{tikzpicture}", start)
        if pos == -1:
            break
        end = text.find(r"\end{tikzpicture}", pos)
        if end == -1:
            break
        blocks.append(text[pos:end + len(r"\end{tikzpicture}")])
        start = end + len(r"\end{tikzpicture}")
    return blocks

tikz_blocks = extract_tikz_blocks(content)
print(f"Found {len(tikz_blocks)} TikZ blocks.")

# Compile each TikZ picture individually to standalone PDF and convert to JPG
for i, block in enumerate(tikz_blocks):
    fig_name = f"fig_{i+1}"
    if "Framework Architecture" in content or "injector" in block:
        fig_name = "architecture"
    if "Initialize Environment" in block:
        fig_name = "workflow"
    if "Policy Network" in block:
        fig_name = "rl_cycle"
    if "Multi-Head Self-Attention" in block or "Shared Latent Features" in block:
        fig_name = "network_architecture"
        
    tex_filename = f"temp_{fig_name}.tex"
    print(f"Creating {tex_filename} for figure: {fig_name}")
    
    with open(tex_filename, "w") as tf:
        tf.write(preamble + "\n\\begin{document}\n" + block + "\n\\end{document}\n")
        
    # Compile
    subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_filename], stdout=subprocess.DEVNULL)
    
    # Convert to high-res JPEG (300 DPI) using pdftoppm
    pdf_filename = f"temp_{fig_name}.pdf"
    if os.path.exists(pdf_filename):
        print(f"Converting {pdf_filename} to JPEG...")
        # pdftoppm -jpeg -r 300 temp_architecture.pdf figs/architecture
        subprocess.run(["/home/karthik/bin/pdftoppm", "-jpeg", "-r", "300", pdf_filename, f"figs/{fig_name}"], stdout=subprocess.DEVNULL)
        # pdftoppm names it figs/architecture-1.jpg, rename it to figs/architecture.jpg
        out_jpg = f"figs/{fig_name}-1.jpg"
        if os.path.exists(out_jpg):
            shutil.move(out_jpg, f"figs/{fig_name}.jpg")
            print(f"Created figs/{fig_name}.jpg successfully.")
        else:
            print(f"Warning: Expected output {out_jpg} not found.")
    else:
        print(f"Error: {pdf_filename} failed to compile.")
        
    # Clean up temp files
    for ext in ["tex", "pdf", "aux", "log"]:
        temp_file = f"temp_{fig_name}.{ext}"
        if os.path.exists(temp_file):
            os.remove(temp_file)

# Convert learning curves to JPEG
print("Converting learning_curves.png to learning_curves.jpg...")
if os.path.exists("secchaos_output/learning_curves.png"):
    # Since pdftoppm is only for PDFs, let's use python PIL (pillow) or similar to convert PNG to JPG.
    try:
        from PIL import Image
        img = Image.open("secchaos_output/learning_curves.png")
        img.convert("RGB").save("figs/learning_curves.jpg", "JPEG", quality=95)
        print("Created figs/learning_curves.jpg successfully using PIL.")
    except ImportError:
        # Fall back to running image conversion via python script or standard linux tools
        print("PIL not installed, using matplotlib to save as JPG")
        import matplotlib.image as mpimg
        import matplotlib.pyplot as plt
        img = mpimg.imread("secchaos_output/learning_curves.png")
        plt.imsave("figs/learning_curves.jpg", img)
        print("Created figs/learning_curves.jpg successfully using matplotlib.")
else:
    print("Warning: secchaos_output/learning_curves.png not found.")

print("All figure extraction operations completed.")
