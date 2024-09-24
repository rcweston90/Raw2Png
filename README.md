# RAW to Web-Compatible PNG/JPEG Converter

This is a terminal-based tool for converting RAW image files (NEF, CR2, ARW) to web-compatible PNG or JPEG files using NEF2PNG and Caesium Image Compressor.

## Features

- Converts RAW files (NEF, CR2, ARW) to PNG format
- Compresses PNG files to a target size of 5MB or less
- Supports parallel processing for faster conversion of multiple files
- Allows users to specify a custom output directory
- Option to preserve EXIF data during conversion and compression
- Automatically converts to JPEG if PNG compression is insufficient

## Requirements

- Python 3.x
- ImageMagick (for compression)

## Installation

1. Clone this repository or download the `nef_to_png_converter.py` file.
2. Install the required Python packages:

```
pip install rawpy imageio tqdm Pillow exif
```

3. Make sure ImageMagick is installed on your system and available in your PATH.

## Usage

Run the script from the command line:

```
python nef_to_png_converter.py [--preserve-exif]
```

- Use the `--preserve-exif` flag if you want to keep the EXIF data in the converted files.

The script will prompt you to enter:
1. The directory containing RAW files (NEF, CR2, ARW)
2. The custom output directory for compressed files

## How it works

1. The script scans the input directory for RAW files (NEF, CR2, ARW).
2. It converts these files to PNG format using parallel processing for improved speed.
3. The resulting PNG files are then compressed to a target size of 5MB or less.
4. If PNG compression is insufficient, the script attempts to convert the image to JPEG format.
5. The final web-compatible files are saved in the specified output directory.

## Notes

- The compression process uses ImageMagick and may take some time depending on the number and size of input files.
- If the `--preserve-exif` flag is used, the script will attempt to preserve EXIF data during conversion and compression.
- The script will automatically create the output directory if it doesn't exist.

## Contributing

Feel free to fork this repository and submit pull requests for any improvements or bug fixes.

## License

This project is open-source and available under the MIT License.
