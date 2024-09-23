import os
import glob
import subprocess
from tqdm import tqdm

def convert_nef_to_png(input_dir, output_dir):
    """
    Convert NEF files to PNG format using NEF2PNG.
    """
    nef_files = glob.glob(os.path.join(input_dir, "*.NEF"))
    
    print(f"Converting {len(nef_files)} NEF files to PNG...")
    for nef_file in tqdm(nef_files, desc="Converting"):
        base_name = os.path.basename(nef_file)
        png_file = os.path.join(output_dir, os.path.splitext(base_name)[0] + ".png")
        
        try:
            subprocess.run(["nef2png", nef_file, png_file], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error converting {nef_file}: {e}")
        except FileNotFoundError:
            print("Error: NEF2PNG tool not found. Please make sure it's installed and in your PATH.")
            return False
    
    return True

def compress_png_files(input_dir):
    """
    Compress PNG files using Caesium Image Compressor.
    """
    png_files = glob.glob(os.path.join(input_dir, "*.png"))
    
    print(f"Compressing {len(png_files)} PNG files...")
    for png_file in tqdm(png_files, desc="Compressing"):
        try:
            subprocess.run(["caesium", "-q", "80", png_file], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error compressing {png_file}: {e}")
        except FileNotFoundError:
            print("Error: Caesium Image Compressor not found. Please make sure it's installed and in your PATH.")
            return False
    
    return True

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
    if not convert_nef_to_png(input_dir, output_dir):
        print("Conversion process failed. Exiting.")
        return
    
    # Step 2: Compress PNG files
    if not compress_png_files(output_dir):
        print("Compression process failed. Exiting.")
        return
    
    print("\nConversion and compression completed successfully!")
    print(f"Web-compatible PNG files are available in: {output_dir}")

if __name__ == "__main__":
    main()
