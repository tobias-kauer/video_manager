import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from torchvision.utils import save_image

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import numpy as np
#import base64
from PIL import Image
#import io
import json
import time
#from pathlib import Path


#import matplotlib.pyplot as plt

# --- CONFIGURATION ---
LATENT_DIM = 64
BATCH_SIZE = 64
EPOCHS = 100
IMAGE_SIZE = 64
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "model/dcgan_noBG_processed_generator_0100.pth"
OUTPUT_FOLDER = "web/data/tsne_images"
OUTPUT_FILE = "tsne_output.json"
image_path = "frame_user_001_00924.png"  # Path to the input image


#original_vector = torch.randn(LATENT_DIM).to(DEVICE)  # Example original vector


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

try:
    dcgan_generator.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
except RuntimeError as e:
    print(f"Error loading model: {e}")
    print("Attempting to load on CPU...")
    dcgan_generator.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    dcgan_generator = dcgan_generator.to(DEVICE)

dcgan_generator.eval()  # Set to evaluation mode


def calculate_similarity(original_vector, latent_vector, method="cosine"):
    original_vector = original_vector.cpu().numpy()
    latent_vector = latent_vector.cpu().numpy()

    if method == "cosine":
        # Cosine similarity
        similarity = np.dot(original_vector, latent_vector) / (
            np.linalg.norm(original_vector) * np.linalg.norm(latent_vector)
        )
        # Normalize to [0, 100]
        return (similarity + 1) / 2 * 100
    elif method == "euclidean":
        # Euclidean distance
        distance = np.linalg.norm(original_vector - latent_vector)
        max_distance = np.sqrt(len(original_vector))  # Maximum possible distance
        similarity = (1 - (distance / max_distance)) * 100
        return similarity
    else:
        raise ValueError("Invalid method. Use 'cosine' or 'euclidean'.")

def invert_image_to_latent(image_path, generator, latent_dim, device, num_steps=50, learning_rate=0.01):
    """
    Perform GAN inversion to find the latent vector corresponding to an input RGBA image.

    Args:
        image_path (str): Path to the input image.
        generator (torch.nn.Module): Pre-trained GAN generator model.
        latent_dim (int): Dimensionality of the latent space.
        device (torch.device): Device to run the model on (CPU or GPU).
        num_steps (int): Number of optimization steps.
        learning_rate (float): Learning rate for the optimizer.

    Returns:
        torch.Tensor: Optimized latent vector corresponding to the input image.
    """
    # Load and preprocess the image
    transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),  # Resize to match GAN input size
        transforms.ToTensor(),  # Convert to tensor
        transforms.Normalize([0.5], [0.5])  # Normalize to [-1, 1] (GAN input range)
    ])
    image = Image.open(image_path).convert("RGBA")  # Ensure the image is in RGBA format
    image_tensor = transform(image).unsqueeze(0).to(device)  # Add batch dimension

    # Ensure the generator is on the correct device
    generator = generator.to(device)

    # Initialize a random latent vector
    latent_vector = torch.randn(1, latent_dim, device=device, requires_grad=True)

    # Set up optimizer
    optimizer = torch.optim.Adam([latent_vector], lr=learning_rate)

    # Optimization loop
    for step in range(num_steps):
        optimizer.zero_grad()

        # Generate an image from the latent vector
        generated_image = generator(latent_vector)

        # Ensure the generated image has 4 channels (RGBA)
        if generated_image.shape[1] < 4:
            # Pad the generated image to add an alpha channel
            alpha_channel = torch.ones_like(generated_image[:, :1, :, :])  # Create an alpha channel (all ones)
            generated_image = torch.cat([generated_image, alpha_channel], dim=1)
        elif generated_image.shape[1] > 4:
            # Slice the generated image to keep only the first 4 channels
            generated_image = generated_image[:, :4, :, :]

        # Calculate the loss (mean squared error between input and generated image)
        loss = torch.nn.functional.mse_loss(generated_image, image_tensor)
        loss.backward()
        optimizer.step()

        if step % 10 == 0:
            print(f"Step {step}/{num_steps}, Loss: {loss.item()}")

    original_vector= latent_vector.detach()
    # Step 2: Fix the vector
    original_vector = original_vector.view(LATENT_DIM)  # Reshape to [64]
    original_vector = torch.tanh(original_vector)  # Normalize to [-1, 1]
    original_vector = original_vector * 2  # Scale to match the range [-2, 2]

    return original_vector


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

    # Step 3: Generate images and prepare output
    output = []
    batch_size = 64  # Define a batch size for processing
    num_batches = (num_samples + batch_size - 1) // batch_size  # Calculate the number of batches

    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, num_samples)
        latent_vectors = z[start_idx:end_idx]

        with torch.no_grad():
            generated_images = generator(latent_vectors).cpu()  # Shape: [batch_size, C, H, W]
            generated_images = (generated_images + 1) / 2  # Normalize to [0, 1]

            for i, generated_image in enumerate(generated_images):
                if use_base64:
                    # Convert image to base64
                    import io
                    import base64
                    buffer = io.BytesIO()
                    save_image(generated_image, buffer, format="PNG", normalize=True)
                    buffer.seek(0)
                    base64_image = f"data:image/png;base64,{base64.b64encode(buffer.read()).decode('utf-8')}"
                    output.append({
                        "position": z_reduced[start_idx + i].tolist(),
                        "imageUrl": base64_image
                    })
                else:
                    # Save image to file
                    image_path = os.path.join(output_folder, f"image_{start_idx + i:03d}.png")
                    save_image(generated_image, image_path, normalize=True)
                    output.append({
                        "position": z_reduced[start_idx + i].tolist(),
                        "imageUrl": image_path
                    })

    # Save the output as a JSON file
    with open(output_json, "w") as json_file:
        json.dump(output, json_file, indent=4)
    print(f"Output saved as JSON: {output_json}")

    return output

def generate_dimensionality_reduction_visualization_with_similarity_analysis(
    generator, latent_dim, num_samples=100, reduction_method="tsne", output_folder="reduced_images", use_base64=False, output_json="output.json", similarity_vector=None, batch_size=100, overwrite=False
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

    # Create the output folder and the images subfolder
    images_folder = os.path.join(output_folder, "images")
    os.makedirs(images_folder, exist_ok=True)


    # Step 1: Generate latent vectors
    z = torch.randn(num_samples, latent_dim).to("cpu")  # Use CPU for compatibility with sklearn

    # Step 2: Apply dimensionality reduction
    if reduction_method.lower() == "tsne":
        print("Using t-SNE for dimensionality reduction...")
        z_reduced = TSNE(n_components=50).fit_transform(z.numpy())
    elif reduction_method.lower() == "pca":
        print("Using PCA for dimensionality reduction...")
        z_reduced = PCA(n_components=3).fit_transform(z.numpy())
    else:
        raise ValueError("Invalid reduction method. Choose 'tsne' or 'pca'.")

    # Step 3: Process latent vectors in batches
    output = []
    num_batches = (num_samples + batch_size - 1) // batch_size  # Calculate the number of batches
    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, num_samples)
        batch_z = z[start_idx:end_idx]
        batch_z_reduced = z_reduced[start_idx:end_idx]

        print(f"Processing batch {batch_idx + 1}/{num_batches}...")

        for i, latent_vector in enumerate(batch_z):
            with torch.no_grad():
                generated_image = generator(latent_vector.unsqueeze(0)).cpu()  # Shape: [1, C, H, W]
                generated_image = (generated_image + 1) / 2  # Normalize to [0, 1]

                # Calculate similarity score
                similarity_score = calculate_similarity(similarity_vector, latent_vector, method="cosine")

                if use_base64:
                    # Convert image to base64
                    import io
                    import base64
                    buffer = io.BytesIO()
                    save_image(generated_image, buffer, format="PNG", normalize=True)
                    buffer.seek(0)
                    base64_image = f"data:image/png;base64,{base64.b64encode(buffer.read()).decode('utf-8')}"
                    output.append({
                        "position": batch_z_reduced[i].tolist(),
                        "imageUrl": base64_image,
                        "similarity": float(similarity_score)
                    })
                else:
                    # Save image to file
                    image_path = os.path.join(images_folder, f"image_{start_idx + i:03d}.png")
                    save_image(generated_image, image_path, normalize=True)

                    # Construct relative path for the image URL
                    relative_image_path = os.path.relpath(image_path, start=output_folder)

                    output.append({
                        "position": batch_z_reduced[i].tolist(),
                        "imageUrl": relative_image_path,
                        "similarity": float(similarity_score)
                    })


    
    # Save the output as a JSON file in the specified folder
    json_path = os.path.join(output_folder, output_json)
    # Save the output as a JSON file
    if os.path.exists(json_path) and not overwrite:
        print(f"Existing JSON file found: {json_path}. Overwriting first {num_samples} entries...")
        with open(json_path, "r") as json_file:
            existing_data = json.load(json_file)
        
        # Overwrite the first `num_samples` entries
        existing_data[:num_samples] = output

        # Save the updated data back to the file
        with open(json_path, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)
    else:
        # Save the new data as a JSON file
        with open(json_path, "w") as json_file:
            json.dump(output, json_file, indent=4)


    return output

def reset_model(generator):
    """
    Reset the generator model to ensure a clean state.
    """
    generator.apply(lambda m: m.reset_parameters() if hasattr(m, 'reset_parameters') else None)


def modelviz_train(uuid):
    '''original_vector = invert_image_to_latent(image_path, dcgan_generator, LATENT_DIM, DEVICE)

    # Debug the vector
    print(f"Latent vector shape: {original_vector.shape}")
    print(f"Latent vector min: {original_vector.min()}, max: {original_vector.max()}")
    print(f"Latent vector values: {original_vector}")'''

    #reset_model(dcgan_generator)

    # Construct the image path dynamically
    image_path = os.path.join(
        "web", "videos", uuid, "processed_colour", "frame_0099_noBG_processed.png"
    )

    # Debug the constructed image path
    print(f"Using image path: {image_path}")

    # Example Usage with PCA
    output = generate_dimensionality_reduction_visualization_with_similarity_analysis(
        dcgan_generator, 
        latent_dim=LATENT_DIM, 
        num_samples=128, 
        reduction_method="pca", 
        output_folder=OUTPUT_FOLDER, 
        use_base64=False, 
        output_json=OUTPUT_FILE,
        similarity_vector=invert_image_to_latent(image_path, dcgan_generator, LATENT_DIM, DEVICE),
        batch_size=128,
        overwrite=False
    )

    #time.sleep(20)  # Simulate some processing time