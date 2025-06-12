import os
import torch
import torch.nn as nn
import torch.nn.functional as F
#from torch.utils.data import DataLoader
#from torchvision import transforms, datasets, utils
from torchvision.utils import save_image

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

#import base64
from PIL import Image
#import io
import json
#from pathlib import Path


#import matplotlib.pyplot as plt

# --- CONFIGURATION ---
LATENT_DIM = 64
BATCH_SIZE = 64
EPOCHS = 100
IMAGE_SIZE = 64
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "model/dcgan_noBG_generator_030.pth"
OUTPUT_FOLDER = "pca_images"


'''DATA_DIR = "hands_64_noBG"

# --- DATASET ---
transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),  # Scales to [0, 1]
    # Ensure alpha channel is preserved
])'''

'''# Custom dataset loader to handle RGBA images
class RGBAImageFolder(datasets.ImageFolder):
    def __getitem__(self, index):
        path, target = self.samples[index]
        sample = Image.open(path).convert("RGBA")  # Ensure RGBA format
        if self.transform is not None:
            sample = self.transform(sample)
        return sample, target

dataset = RGBAImageFolder(root=DATA_DIR, transform=transform)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)'''


os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"  # Enable CPU fallback for unsupported MPS operations

class DCGANGenerator(nn.Module):
    def __init__(self, latent_dim=100):
        super(DCGANGenerator, self).__init__()
        self.model = nn.Sequential(
            nn.ConvTranspose2d(latent_dim, 512, kernel_size=4, stride=1, padding=0),  # 1x1 -> 4x4
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.ConvTranspose2d(512, 256, kernel_size=4, stride=2, padding=1),  # 4x4 -> 8x8
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),  # 8x8 -> 16x16
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),  # 16x16 -> 32x32
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 4, kernel_size=4, stride=2, padding=1),  # 32x32 -> 64x64 — RGBA (was 3)
            nn.Tanh()
        )

    def forward(self, z):
        return self.model(z.view(z.size(0), z.size(1), 1, 1))

# --- Load the Trained Generator ---
dcgan_generator = DCGANGenerator(latent_dim=LATENT_DIM).to(DEVICE)
dcgan_generator.load_state_dict(torch.load(MODEL_PATH))
dcgan_generator.eval()  # Set to evaluation mode

def generate_dimensionality_reduction_visualization(
    generator, latent_dim, num_samples=100, reduction_method="tsne", output_folder="reduced_images", use_base64=False, output_json="output.json"
):
    """
    Generate images and visualize them in 3D space using t-SNE or PCA reduction.
    
    Args:
        generator: The trained generator model.
        latent_dim: The size of the latent space.
        num_samples: Number of latent vectors to generate.
        reduction_method (str): Dimensionality reduction method ("tsne" or "pca").
        output_folder (str): Folder where generated images will be saved.
        use_base64 (bool): Whether to encode images as base64 strings instead of saving them as files.
        output_json (str): Path to save the output JSON file.
    
    Returns:
        list: A list of dictionaries containing 3D coordinates and image URLs or base64 strings.
    """

    generator = generator.to("cpu")

    # Create the output folder if saving images
    if not use_base64:
        os.makedirs(output_folder, exist_ok=True)

    # Step 1: Generate latent vectors
    z = torch.randn(num_samples, latent_dim).to("cpu")  # Use CPU for compatibility with sklearn

    # Step 2: Apply dimensionality reduction
    if reduction_method.lower() == "tsne":
        print("Using t-SNE for dimensionality reduction...")
        z_reduced = TSNE(n_components=3).fit_transform(z.numpy())
    elif reduction_method.lower() == "pca":
        print("Using PCA for dimensionality reduction...")
        z_reduced = PCA(n_components=3).fit_transform(z.numpy())
    else:
        raise ValueError("Invalid reduction method. Choose 'tsne' or 'pca'.")

    # Step 3: Generate images and prepare output
    output = []
    for i, latent_vector in enumerate(z):
        with torch.no_grad():
            generated_image = generator(latent_vector.unsqueeze(0)).cpu()  # Shape: [1, C, H, W]
            generated_image = (generated_image + 1) / 2  # Normalize to [0, 1]

            if use_base64:
                # Convert image to base64
                import io
                import base64
                buffer = io.BytesIO()
                save_image(generated_image, buffer, format="PNG", normalize=True)
                buffer.seek(0)
                base64_image = f"data:image/png;base64,{base64.b64encode(buffer.read()).decode('utf-8')}"
                output.append({
                    "position": z_reduced[i].tolist(),
                    "imageUrl": base64_image
                })
            else:
                # Save image to file
                image_path = os.path.join(output_folder, f"image_{i:03d}.png")
                save_image(generated_image, image_path, normalize=True)
                output.append({
                    "position": z_reduced[i].tolist(),
                    "imageUrl": image_path
                })

    # Save the output as a JSON file
    with open(output_json, "w") as json_file:
        json.dump(output, json_file, indent=4)
    print(f"Output saved as JSON: {output_json}")

    return output


# Example Usage with PCA
output = generate_dimensionality_reduction_visualization(
    dcgan_generator, 
    latent_dim=LATENT_DIM, 
    num_samples=1000, 
    reduction_method="pca", 
    output_folder=OUTPUT_FOLDER, 
    use_base64=False, 
    output_json="pca_output.json"
)