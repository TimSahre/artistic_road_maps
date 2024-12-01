import yaml
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration parameters
config = {
    "place_name": "Spandau",  # Type in name of city
    "color_scheme": "pink",  # Available: "default", "dark", "pink", "green", "blue", "yellow", "violet", "red_gold", "midnight_teal", "ice_fire", "solar_flare", "emerald_glow", "copper_twilight", "nebula_dream"
    "config_file": "config.yml",  # Path to configuration file
    "font_path": "Protest_Revolution/ProtestRevolution-Regular.ttf",  # Custom font file path
    "custom_text_color": ""  # Custom text color (e.g., white). Leave empty to use the default color.
}

class MapVisualizer:
    def __init__(self, config):
        # Load the configuration from the file
        with open(config["config_file"], "r") as file:
            self.file_config = yaml.safe_load(file)
        
        self.place_name = config["place_name"]
        self.color_scheme = config["color_scheme"]
        self.font_path = config["font_path"]
        self.custom_text_color = config.get("custom_text_color")

        # Initialize custom font
        try:
            self.custom_font = FontProperties(fname=self.font_path)
        except FileNotFoundError:
            logging.warning(f"Font file '{self.font_path}' not found. Default font will be used.")
            self.custom_font = None

        self.validate_place_name()
        self.title, self.subtitle = self.generate_title_and_subtitle()
        self.output_file = self.generate_output_file()
        self.load_data()
    
    def validate_place_name(self):
        """
        Validates whether the entered place name is valid and exists.
        """
        try:
            logging.info(f"Validating place name: {self.place_name}")
            area = ox.geocode_to_gdf(self.place_name)
            if area.empty:
                raise ValueError
        except Exception as e:
            raise ValueError(f"The entered place '{self.place_name}' could not be found. "
                             f"Please check your input.") from e

    def generate_title_and_subtitle(self):
        """
        Dynamically generates the title and subtitle based on the place name.
        """
        logging.info("Generating dynamic title and subtitle...")
        area = ox.geocode_to_gdf(self.place_name)
        if area.empty:
            raise ValueError(f"No geodata found for the place '{self.place_name}'.")
        
        # Set title to the place name in uppercase
        title = self.place_name.upper()

        # Extract coordinates for the city's center
        centroid = area.geometry[0].centroid
        lat, lon = centroid.y, centroid.x

        # Format the coordinates for the subtitle
        lat_direction = "N" if lat >= 0 else "S"
        lon_direction = "E" if lon >= 0 else "W"
        subtitle = f"{abs(lat):.2f}° {lat_direction} / {abs(lon):.2f}° {lon_direction}"

        logging.info(f"Dynamic title: {title}, subtitle: {subtitle}")
        return title, subtitle

    def generate_output_file(self):
        """
        Dynamically generates the output filename based on the place name and color scheme.
        """
        logging.info("Generating dynamic output filename...")
        sanitized_name = self.place_name.replace(" ", "_").replace(",", "")
        output_dir = "Outputs"  # Specify the output directory
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
        output_file = os.path.join(output_dir, f"{sanitized_name}_{self.color_scheme}_StyledMap.png")
        logging.info(f"Dynamic output path: {output_file}")
        return output_file

    def load_data(self):
        """
        Loads the street and water network data for the given place.
        """
        logging.info(f"Loading city boundaries for: {self.place_name}")
        self.area = ox.geocode_to_gdf(self.place_name)
        if self.area.empty:
            raise ValueError(f"No data found for the place '{self.place_name}'.")

        logging.info("Loading road network...")
        self.G_roads = ox.graph_from_polygon(self.area.geometry[0], retain_all=True, simplify=True, network_type='all')
        if len(self.G_roads.edges) == 0:
            raise ValueError("Road network is empty.")

        logging.info("Loading water networks...")
        custom_filter_water = '["natural"~"water|wetland|bay"]'
        custom_filter_river = '["waterway"~"river|canal|stream"]'
        G1_water = ox.graph_from_polygon(self.area.geometry[0], network_type='all', 
                                         simplify=True, retain_all=True, custom_filter=custom_filter_water)
        G2_water = ox.graph_from_polygon(self.area.geometry[0], network_type='all', 
                                         simplify=True, retain_all=True, custom_filter=custom_filter_river)
        self.G_water = nx.compose(G1_water, G2_water)
        if len(self.G_water.edges) == 0:
            raise ValueError("Water network is empty.")
    
    def apply_styles(self):
        """
        Applies the selected color scheme to roads and water features.
        """
        # Retrieve color scheme
        scheme = self.file_config["color_schemes"][self.color_scheme]
        self.roadColors, self.roadWidths = [], []

        for u, v, data in self.G_roads.edges(data=True):
            if "highway" in data:
                road_type = data["highway"]

                # If road_type is a list, use the first entry
                if isinstance(road_type, list):
                    logging.warning(f"Highway type contains multiple values: {road_type}. Using the first entry.")
                    road_type = road_type[0]

                # Retrieve the style from the scheme, or default to "other"
                style = scheme["roads"].get(road_type, scheme["roads"]["other"])
            else:
                style = scheme["roads"]["other"]
            
            self.roadColors.append(style["color"])
            self.roadWidths.append(style["linewidth"])
        
        self.water_style = scheme["water"]
        self.background_color = scheme.get("background", "#061529")
    
    def render_map(self):
        """
        Renders the map and saves it to the output file.
        """
        self.apply_styles()
        
        # Create the map
        logging.info("Creating map...")
        fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
        ax.set_facecolor(self.background_color)
        fig.patch.set_facecolor(self.background_color)
        
        # Layer 2: Water networks
        for u, v, data in self.G_water.edges(data=True):
            if 'geometry' in data:
                x, y = data['geometry'].xy
                ax.plot(x, y, color=self.water_style["color"], linewidth=self.water_style["linewidth"], alpha=0.6, zorder=2)
            else:
                x = [self.G_water.nodes[u]['x'], self.G_water.nodes[v]['x']]
                y = [self.G_water.nodes[u]['y'], self.G_water.nodes[v]['y']]
                ax.plot(x, y, color=self.water_style["color"], linewidth=self.water_style["linewidth"], alpha=0.6, zorder=2)
        
        # Layer 3: Road network
        for i, (u, v, data) in enumerate(self.G_roads.edges(data=True)):
            if 'geometry' in data:
                x, y = data['geometry'].xy
                ax.plot(x, y, color=self.roadColors[i], linewidth=self.roadWidths[i], alpha=1, zorder=3)
            else:
                x = [self.G_roads.nodes[u]['x'], self.G_roads.nodes[v]['x']]
                y = [self.G_roads.nodes[u]['y'], self.G_roads.nodes[v]['y']]
                ax.plot(x, y, color=self.roadColors[i], linewidth=self.roadWidths[i], alpha=1, zorder=3)
        
        # Add text for title and subtitle
        text_color = self.custom_text_color or self.file_config["color_schemes"][self.color_scheme]["roads"]["motorway"]["color"]
        
        # Main title
        #ax.text(0.5, 0.95, self.title, transform=ax.transAxes, fontsize=30, color=text_color, 
                #ha="center", va="top", weight="bold", fontproperties=self.custom_font if self.custom_font else None)
        
        # Subtitle
        ax.text(0.5, 0.9, self.subtitle, transform=ax.transAxes, fontsize=50, color=text_color, 
                ha="center", va="top", fontproperties=self.custom_font if self.custom_font else None)
        
        ax.axis("off")
        fig.tight_layout(pad=0)
        fig.savefig(self.output_file, dpi=300, bbox_inches='tight', format="png", 
                    facecolor=fig.get_facecolor(), transparent=False)
        logging.info(f"Map successfully saved to: {self.output_file}")


if __name__ == "__main__":
    visualizer = MapVisualizer(config)
    visualizer.render_map()