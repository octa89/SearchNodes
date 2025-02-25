ArcGIS Pipe-to-Manhole Matcher
This repository contains a Python script that automates the process of spatially linking pipes to the nearest manholes in an ArcGIS geodatabase. Using ArcPy and Colorama for color-coded console output, the script prompts the user to select the appropriate feature classes and fields, then matches each pipe’s start and end points to the closest manhole based on geometry. The matched manhole IDs are written back to the pipe features, updating the specified fields.

Features
Interactive Selection:
Lists available feature classes and fields from your geodatabase.
Allows you to select the pipes and nodes (manholes) layers.
Prompts you to select the fields for AssetID, StartID, EndID, and ManholeID.
Spatial Analysis:
Uses ArcPy to extract geometries from feature classes.
Calculates distances between pipe endpoints and manhole locations.
Identifies the nearest manhole for both the start and end of each pipe.
Automated Update:
Updates the pipe feature class with the nearest manhole IDs.
Provides clear, color-coded console output using Colorama.
Requirements
Python 3.x
ArcGIS with ArcPy (ArcGIS Desktop or ArcGIS Pro)
Colorama
Install via pip:
bash
Copy
pip install colorama
Usage
Clone the repository:

bash
Copy
git clone (https://github.com/octa89/SearchNodes/edit/main/README.md)
cd arcgis-pipe-manhole-matcher
Ensure your ArcGIS environment is set up (so that ArcPy is available).

Run the script:

bash
Copy
python match_pipes_to_manholes.py
Follow the prompts:

Enter the path to your geodatabase.
Select the feature class representing pipes.
Select the feature class representing nodes (manholes).
Choose the fields for AssetID, StartID, EndID, and ManholeID.
The script will process the data and update the pipe layer with the nearest manhole IDs.
Contributing
Contributions are welcome! If you have suggestions, improvements, or bug fixes, please open an issue or submit a pull request.

License
This project is licensed under the MIT License.
