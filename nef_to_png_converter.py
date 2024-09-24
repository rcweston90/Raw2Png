import os
import glob
from tqdm import tqdm
import rawpy
import imageio
import subprocess
from multiprocessing import Pool, cpu_count
import argparse
from PIL import Image
from PIL.ExifTags import TAGS
from exif import Image as ExifImage

def convert_raw_to_png(args):
    input_file, output_dir, preserve_exif = args
    try:
        output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + ".png")
        with rawpy.imread(input_file) as raw:
            rgb = raw.postprocess()
        imageio.imsave(output_file, rgb)
        
        if preserve_exif:
            # Copy EXIF data from RAW to PNG
            with open(input_file, 'rb') as raw_file:
                raw_image = ExifImage(raw_file)
            
            png_image = Image.open(output_file)
            exif_data = png_image.getexif()
            
            for tag_id in raw_image.list_all():
                tag = TAGS.get(tag_id, tag_id)
                data = raw_image.get(tag_id)
                if data is not None:
                    exif_data[tag_id] = data
            
            png_image.save(output_file, exif=exif_data)
        
        print(f"Successfully converted {input_file} to {output_file}")
        return True
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        return False

def convert_raw_files(input_dir, output_dir, preserve_exif):
    raw_files = glob.glob(os.path.join(input_dir, "*.NEF")) + \
                glob.glob(os.path.join(input_dir, "*.CR2")) + \
                glob.glob(os.path.join(input_dir, "*.ARW"))

    print(f"Converting {len(raw_files)} RAW files to PNG...")
    print("File types found:")
    print(f"NEF files: {len(glob.glob(os.path.join(input_dir, '*.NEF')))}")
    print(f"CR2 files: {len(glob.glob(os.path.join(input_dir, '*.CR2')))}")
    print(f"ARW files: {len(glob.glob(os.path.join(input_dir, '*.ARW')))}")

    # Use multiprocessing to parallelize the conversion process
    num_processes = cpu_count()
    with Pool(processes=num_processes) as pool:
        args = [(file, output_dir, preserve_exif) for file in raw_files]
        results = list(tqdm(pool.imap(convert_raw_to_png, args), total=len(raw_files), desc="Converting"))

    all_conversions_successful = all(results)
    return all_conversions_successful

def compress_png_files(output_dir, preserve_exif):
    png_files = glob.glob(os.path.join(output_dir, "*.png"))
    target_size = 5 * 1024 * 1024  # 5 MB in bytes

    print(f"Compressing {len(png_files)} PNG files...")
    all_compressions_successful = True
    for png_file in tqdm(png_files, desc="Compressing"):
        output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(png_file))[0] + '_compressed.png')
        quality = 50
        resize_factor = 0.4
        original_size = os.path.getsize(png_file) / 1024 / 1024

        print(f"\nCompressing {png_file}")
        print(f"Original size: {original_size:.2f} MB")

        while True:
            command = [
                "convert", png_file,
                "-quality", str(quality),
                "-resize", f"{resize_factor*100}%",
                "-define", "png:compression-level=9",
            ]
            
            if not preserve_exif:
                command.append("-strip")  # Remove metadata only if not preserving EXIF
            
            command.append(output_file)
            
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                current_size = os.path.getsize(output_file) / 1024 / 1024
                print(f"Quality: {quality}, Resize: {resize_factor*100:.1f}%, Size: {current_size:.2f} MB")
                
                if current_size <= target_size:
                    print(f"Successfully compressed to {current_size:.2f} MB")
                    break
                
                if quality > 30:
                    quality -= 10
                elif quality > 20:
                    quality -= 5
                elif resize_factor > 0.3:
                    resize_factor -= 0.05
                elif resize_factor > 0.2:
                    resize_factor -= 0.02
                else:
                    # Try JPEG conversion with higher quality first
                    jpeg_output = output_file.replace('.png', '.jpg')
                    for jpeg_quality in [80, 60, 40]:
                        jpeg_command = [
                            "convert", png_file,
                            "-quality", str(jpeg_quality),
                            "-resize", "50%",
                        ]
                        if not preserve_exif:
                            jpeg_command.append("-strip")
                        jpeg_command.append(jpeg_output)
                        
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
    parser = argparse.ArgumentParser(description="RAW to Web-Compatible PNG/JPEG Converter")
    parser.add_argument("--preserve-exif", action="store_true", help="Preserve EXIF data during conversion and compression")
    args = parser.parse_args()

    print("RAW to Web-Compatible PNG/JPEG Converter")
    print("========================================")

    input_dir = input("Enter the directory containing RAW files (NEF, CR2, ARW): ").strip()
    output_dir = input("Enter the custom output directory for compressed files: ").strip()

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created custom output directory: {output_dir}")

    # Step 1: Convert RAW to PNG
    conversion_successful = convert_raw_files(input_dir, output_dir, args.preserve_exif)
    if not conversion_successful:
        print("Conversion process failed. Exiting.")
        return

    # Step 2: Compress PNG files
    compression_successful = compress_png_files(output_dir, args.preserve_exif)
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
