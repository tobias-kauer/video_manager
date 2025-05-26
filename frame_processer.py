import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance

def remove_background_skin_mask(image_path):
    # Load and upscale to improve mask accuracy
    img = cv2.imread(image_path)
    img = cv2.resize(img, (256, 256))
    img_ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)

    # Skin color range in YCrCb (adjust if needed)
    lower = np.array([0, 133, 77], dtype=np.uint8)
    upper = np.array([255, 173, 127], dtype=np.uint8)
    mask = cv2.inRange(img_ycrcb, lower, upper)

    # Morphological operations to clean noise
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    # Create RGBA image
    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    img_rgba[:, :, 3] = mask

    # Resize back to 64x64
    result = cv2.resize(img_rgba, (64, 64))
    return result


def remove_background_skin_mask_directory(input_dir, output_dir, suffix="_noBG"):
    """
    Process all images in a directory to remove the background using a skin mask
    and save the processed images with an optional suffix.

    Args:
        input_dir (str): Directory containing the input images.
        output_dir (str): Directory where the processed images will be saved.
        suffix (str): Suffix to add to the output filenames (default is "_noBG").
    """
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            input_path = os.path.join(input_dir, filename)
            # Add the suffix to the output filename
            output_filename = os.path.splitext(filename)[0] + suffix + ".png"
            output_path = os.path.join(output_dir, output_filename)

            try:
                processed_img = remove_background_skin_mask(input_path)
                Image.fromarray(processed_img).save(output_path)
                #print(f"Processed {filename} -> {output_filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")


def process_images_in_folder(input_dir, output_dir, suffix="_processed", replace_transparent=True):
    """
    Process all image files in a folder by optionally replacing transparent pixels with white,
    converting them to black and white, and increasing contrast. Saves the processed
    images in a specified output folder with a customizable suffix added to their filenames.
    
    Args:
        folder_path (str): Path to the folder containing the images.
        output_folder (str): Path to the folder where processed images will be saved.
        suffix (str): Suffix to add to the processed file names (default: "_processed").
        replace_transparent (bool): Whether to replace transparent pixels with white (default: True).
    """
    # Ensure the input folder exists
    if not os.path.exists(input_dir):
        print(f"Folder '{input_dir}' does not exist.")
        return

    # Create the output folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process each file in the folder
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)

        # Check if the file is an image (e.g., PNG, JPG)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                # Open the image
                img = Image.open(file_path).convert("RGBA")

                # Optionally replace transparent pixels with white
                if not replace_transparent:
                # Split the image into RGB and alpha channels
                    r, g, b, alpha = img.split()

                    # Merge RGB channels into a single image
                    rgb = Image.merge("RGB", (r, g, b))

                    # Darken the RGB channels by reducing brightness
                    brightness_enhancer = ImageEnhance.Brightness(rgb)
                    rgb_darker = brightness_enhancer.enhance(0.4)  # Reduce brightness (0.5 = 50% darker)

                    # Convert the darkened RGB image to grayscale
                    grayscale = rgb_darker.convert("L")

                    # Merge the grayscale image back with the alpha channel
                    img = Image.merge("RGBA", (grayscale, grayscale, grayscale, alpha))

                else:
                    # Replace transparent pixels with white
                    background = Image.new("RGBA", img.size, (255, 255, 255, 255))  # White background
                    img = Image.alpha_composite(background, img)  # Combine with white background

                    # Convert the entire image to grayscale
                    img = img.convert("L")


                # Increase contrast
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(3.0)  # Adjust the factor as needed

                # Save the processed image in the output folder with the custom suffix
                new_filename = f"{os.path.splitext(filename)[0]}{suffix}{os.path.splitext(filename)[1]}"
                new_file_path = os.path.join(output_dir, new_filename)
                img.save(new_file_path)
                #print(f"Processed and saved: {new_file_path}")
            except Exception as e:
                print(f"Failed to process file '{filename}': {e}")
        else:
            print(f"Skipped non-image file: {filename}")



