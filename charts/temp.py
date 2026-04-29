import os
from PIL import Image

folder_path = "./charts"

images = [f for f in os.listdir(folder_path) if f.endswith(".png")]
images.sort()
images = images[:6]

imgs = [Image.open(os.path.join(folder_path, img)) for img in images]

# zakładamy grid 3x2
cols = 2
rows = 3

# rozmiar bazowy (dopasowany do pierwszego obrazka)
w, h = imgs[0].size

canvas = Image.new('RGB', (cols * w, rows * h), (255, 255, 255))

for idx, img in enumerate(imgs):
    img = img.resize((w, h))  # spójny rozmiar
    
    x = (idx % cols) * w
    y = (idx // cols) * h
    
    canvas.paste(img, (x, y))

output_path = os.path.join(folder_path, "joined_charts.png")
canvas.save(output_path, "PNG", quality=95, optimize=True)

print(f"Saved to: {output_path}")