# Map Visualizer

A Python-based tool for generating customized, visually appealing maps of cities using street networks and waterways. This project leverages **OSMnx**, **NetworkX**, and **Matplotlib** to create maps with various color schemes and titles dynamically generated based on the city name.

## Features

- Dynamically fetches city boundaries and road networks using OpenStreetMap.
- Generates maps with customized color schemes for roads, water, and background.
- Supports user-defined map titles, subtitles, and custom fonts.
- Automatically saves the output map with a descriptive filename based on the city name and color scheme.
- Includes pre-configured **color schemes** like `default`, `dark`, `pink`, `green`, `blue`, `yellow`, `violet`, `red_gold`, and `midnight_teal`.

## Installation

### Prerequisites
- Python 3.9 or higher.
- Conda package manager (recommended for creating the environment).

### Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/map-visualizer.git
   cd map-visualizer
   ```

2. Create and activate the environment using Conda:
   ```bash
   conda env create -f environment.yml
   conda activate map_visualizer_env
   ```

3. Install additional Python dependencies if needed:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Edit the `config.yml` file to define the **color schemes** for your map.

2. Configure the parameters in the script:
   ```python
   config = {
       "place_name": "New York",  # Specify the city or location name
       "color_scheme": "red_gold",  # Select a color scheme from the YAML configuration
       "config_file": "config.yml",  # Path to the YAML configuration
       "font_path": "Protest_Revolution/ProtestRevolution-Regular.ttf",  # Optional custom font
       "custom_text_color": ""  # Specify a custom text color (optional)
   }
   ```

3. Run the script:
   ```bash
   python script.py
   ```

4. The generated map will be saved in the `Outputs` directory, with a filename based on the city name and selected color scheme (e.g., `New_York_red_gold_StyledMap.png`).

## Example

Here is an example output for **New York City** using the `red_gold` color scheme:

![New York City Map](Outputs/New_York_red_gold_StyledMap.png)

## Color Schemes

The project includes multiple pre-configured color schemes for roads, water, and backgrounds. Below are a few examples:

1. **Default**: Subtle greyscale theme.
2. **Dark**: Bold and dark theme.
3. **Pink**: Vibrant neon pink theme.
4. **Red-Gold**: A warm mix of reds and golds.
5. **Midnight-Teal**: Cool and modern teal-based theme.

You can define your custom color schemes in `config.yml`.

## Environment Setup

For reproducibility, the Python environment is managed with Conda. The dependencies are defined in `environment.yml`. To create the environment:

```bash
conda env create -f environment.yml
conda activate map_visualizer_env
```

## Dependencies

This project uses the following libraries:
- **OSMnx**: For fetching street networks and city boundaries.
- **NetworkX**: For processing graph-based data.
- **Matplotlib**: For map rendering and visualization.
- **PyYAML**: For configuration management.