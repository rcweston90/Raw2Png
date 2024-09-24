import os
import glob
from tqdm import tqdm
import rawpy
import imageio
import subprocess

def convert_nef_to_png(input_file, output_file):
    try:
        with rawpy.imread(input_file) as raw:
            rgb = raw.postprocess()
        imageio.imsave(output_file, rgb)
        print(f"Successfully converted {input_file} to {output_file}")
        return True
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        return False

def convert_nef_files(input_dir, output_dir):
    nef_files = glob.glob(os.path.join(input_dir, "*.NEF"))

    print(f"Converting {len(nef_files)} NEF files to PNG...")
    all_conversions_successful = True
    for nef_file in tqdm(nef_files, desc="Converting"):
        base_name = os.path.basename(nef_file)
        png_file = os.path.join(output_dir, os.path.splitext(base_name)[0] + ".png")

        if not convert_nef_to_png(nef_file, png_file):
            all_conversions_successful = False

    return all_conversions_successful

def compress_png_files(input_dir):
    png_files = glob.glob(os.path.join(input_dir, "*.png"))
    target_size = 5 * 1024 * 1024  # 5 MB in bytes

    print(f"Compressing {len(png_files)} PNG files...")
    all_compressions_successful = True
    for png_file in tqdm(png_files, desc="Compressing"):
        output_file = png_file.replace('.png', '_compressed.png')
        quality = 60
        resize_factor = 0.5
        original_size = os.path.getsize(png_file) / 1024 / 1024

        print(f"\nCompressing {png_file}")
        print(f"Original size: {original_size:.2f} MB")

        while True:
            command = [
                "convert", png_file,
                "-quality", str(quality),
                "-resize", f"{resize_factor*100}%",
                "-define", "png:compression-level=9",
                "-strip",  # Remove metadata
                output_file
            ]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                current_size = os.path.getsize(output_file) / 1024 / 1024
                print(f"Quality: {quality}, Resize: {resize_factor*100:.1f}%, Size: {current_size:.2f} MB")
                
                if current_size <= target_size:
                    print(f"Successfully compressed to {current_size:.2f} MB")
                    break
                
                if quality > 40:
                    quality -= 10
                elif quality > 20:
                    quality -= 5
                elif resize_factor > 0.3:
                    resize_factor -= 0.1
                elif resize_factor > 0.2:
                    resize_factor -= 0.05
                else:
                    # Try JPEG conversion as a last resort
                    jpeg_output = output_file.replace('.png', '.jpg')
                    jpeg_command = [
                        "convert", png_file,
                        "-quality", "40",
                        "-resize", "40%",
                        "-strip",
                        jpeg_output
                    ]
                    subprocess.run(jpeg_command, check=True, capture_output=True, text=True)
                    jpeg_size = os.path.getsize(jpeg_output) / 1024 / 1024
                    if jpeg_size <= target_size:
                        print(f"Converted to JPEG. Final size: {jpeg_size:.2f} MB")
                        os.remove(output_file)  # Remove the PNG file
                        output_file = jpeg_output  # Update the output file name
                        break
                    else:
                        os.remove(jpeg_output)  # Remove the JPEG file if it's still too large
                        print(f"Warning: Could not compress to under 5 MB. Final size: {current_size:.2f} MB")
                        break
            except FileNotFoundError:
                print("Error: ImageMagick not found. Please make sure it's installed and in your PATH.")
                return False
            except subprocess.CalledProcessError as e:
                print(f"Error compressing {png_file}: {e}")
                all_compressions_successful = False
                break

    return all_compressions_successful

def main():
    print("NEF to Web-Compatible PNG/JPEG Converter")
    print("========================================")

    input_dir = input("Enter the directory containing NEF files: ").strip()
    output_dir = input("Enter the output directory for compressed files: ").strip()

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Step 1: Convert NEF to PNG
    conversion_successful = convert_nef_files(input_dir, output_dir)
    if not conversion_successful:
        print("Conversion process failed. Exiting.")
        return

    # Step 2: Compress PNG files
    compression_successful = compress_png_files(output_dir)
    if not compression_successful:
        print("Compression process failed. Exiting.")
        return

    if conversion_successful and compression_successful:
        print("Conversion and compression completed successfully!")
    else:
        print("Conversion and/or compression process encountered errors.")
    print(f"Web-compatible PNG/JPEG files are available in: {output_dir}")

if __name__ == "__main__":
    main()
