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
    """
    Convert NEF files to PNG format using rawpy and imageio.
    """
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
    """
    Compress PNG files using Caesium Image Compressor.
    """
    png_files = glob.glob(os.path.join(input_dir, "*.png"))
    
    print(f"Compressing {len(png_files)} PNG files...")
    all_compressions_successful = True
    for png_file in tqdm(png_files, desc="Compressing"):
        command = ["caesium", "-q", "80", png_file]
        print(f"Running command: {' '.join(command)}")
        
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Command output:\n{result.stdout}")
        except FileNotFoundError:
            print("Error: Caesium Image Compressor not found. Please make sure it's installed and in your PATH.")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Error compressing {png_file}:")
            print(f"Command: {e.cmd}")
            print(f"Return code: {e.returncode}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            all_compressions_successful = False
    
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
        print("\nConversion and compression completed successfully!")
    else:
        print("\nConversion and/or compression process encountered errors.")
    print(f"Web-compatible PNG files are available in: {output_dir}")

if __name__ == "__main__":
    main()
