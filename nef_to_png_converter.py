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
        quality = 80
        resize_factor = 1.0

        while True:
            command = ["convert", png_file, "-quality", str(quality), "-resize", f"{resize_factor*100}%", output_file]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                
                if os.path.getsize(output_file) <= target_size:
                    print(f"Successfully compressed {png_file} to {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
                    break
                
                if quality > 20:
                    quality -= 10
                elif resize_factor > 0.5:
                    resize_factor -= 0.1
                else:
                    print(f"Warning: Could not compress {png_file} to under 5 MB. Final size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
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
    print("NEF to Web-Compatible PNG Converter")
    print("===================================")

    input_dir = input("Enter the directory containing NEF files: ").strip()
    output_dir = input("Enter the output directory for PNG files: ").strip()

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
    print(f"Web-compatible PNG files are available in: {output_dir}")

if __name__ == "__main__":
    main()
