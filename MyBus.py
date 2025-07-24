import json
import requests
import logging
from datetime import datetime, timezone
import pytz
from multiprocessing import Queue
import pygame
import time

# Initialize Pygame
pygame.init()

# Constants for display
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
BACKGROUND_COLOR = (0, 0, 0)  # Black
TEXT_COLOR = (255, 255, 0)  # Yellow
HEADER_COLOR = (255, 255, 255)  # White
ARRIVAL_COLOR = (0, 255, 0)  # Green
WARNING_COLOR = (255, 165, 0)  # Orange
URGENT_COLOR = (255, 0, 0)  # Red

# Fonts
header_font = pygame.font.Font(None, 46)
route_font = pygame.font.Font(None, 38)
time_font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 28)


class BusArrivalDisplay:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Live Bus Arrivals")
        self.clock = pygame.time.Clock()
        self.running = True

    def get_arrival_color(self, minutes_to_arrival):
        """Get color based on arrival time"""
        if minutes_to_arrival is None:
            return TEXT_COLOR
        elif minutes_to_arrival == 0:
            return URGENT_COLOR
        elif minutes_to_arrival <= 5:
            return WARNING_COLOR
        else:
            return ARRIVAL_COLOR


    def draw_header(self, stop_name):
        """Draw the header section"""
        # Main title
        title_text = header_font.render("Live Bus Arrivals", True, HEADER_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(title_text, title_rect)

        # Stop name
        stop_text = route_font.render(f"{stop_name}", True, TEXT_COLOR)
        stop_rect = stop_text.get_rect(center=(SCREEN_WIDTH // 2, 65))
        self.screen.blit(stop_text, stop_rect)

        # Current time
        current_time = datetime.now().strftime('%I:%M:%S %p')
        time_text = time_font.render(f"Updated: {current_time}", True, TEXT_COLOR)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.screen.blit(time_text, time_rect)

        # Separator line
        pygame.draw.line(self.screen, TEXT_COLOR, (50, 110), (SCREEN_WIDTH - 50, 110), 2)

    def draw_column_headers(self):
        """Draw column headers"""
        y_pos = 125

        route_header = route_font.render("Route", True, HEADER_COLOR)
        self.screen.blit(route_header, (SCREEN_WIDTH ** 0.3, y_pos))

        time_header = route_font.render("Arrival", True, HEADER_COLOR)
        self.screen.blit(time_header, (SCREEN_WIDTH ** 0.6, y_pos))

        countdown_header = route_font.render("Countdown", True, HEADER_COLOR)
        self.screen.blit(countdown_header, (SCREEN_WIDTH ** 0.8, y_pos))

        # Separator line
        pygame.draw.line(self.screen, TEXT_COLOR, (50, y_pos + 25), (SCREEN_WIDTH - 50, y_pos + 25), 1)

    def draw_arrivals(self, arrivals):
        """Draw the arrival information"""
        start_y = 160
        line_height = 40
        max_visible = 8  # Maximum arrivals to show on screen

        visible_arrivals = arrivals[:max_visible]

        for i, arrival in enumerate(visible_arrivals):
            y_pos = start_y + (i * line_height)

            route_name = arrival.get('route_short_name', 'Unknown')
            route_type = arrival.get('route_type', 'Bus')
            formatted_time = arrival.get('formatted_time', 'Unknown')
            minutes_to_arrival = arrival.get('minutes_to_arrival')


            # Route information
            route_text = route_font.render(f"{route_name}", True, TEXT_COLOR)
            self.screen.blit(route_text, (100, y_pos))

            # Arrival time
            time_text = time_font.render(formatted_time, True, TEXT_COLOR)
            self.screen.blit(time_text, (300, y_pos))

            # Countdown with appropriate color
            if minutes_to_arrival is not None:
                if minutes_to_arrival == 0:
                    countdown_text = "🚨 ARRIVING NOW"
                    color = URGENT_COLOR
                elif minutes_to_arrival == 1:
                    countdown_text = "1 minute"
                    color = WARNING_COLOR
                elif minutes_to_arrival <= 5:
                    countdown_text = f"⚡ {minutes_to_arrival} minutes"
                    color = WARNING_COLOR
                else:
                    countdown_text = f"{minutes_to_arrival} minutes"
                    color = ARRIVAL_COLOR
            else:
                countdown_text = "Unknown"
                color = TEXT_COLOR

            countdown_surface = time_font.render(countdown_text, True, color)
            self.screen.blit(countdown_surface, (500, y_pos))

            # Draw separator line between routes
            if i < len(visible_arrivals) - 1:
                pygame.draw.line(self.screen, (64, 64, 64),
                                 (50, y_pos + line_height - 5),
                                 (SCREEN_WIDTH - 50, y_pos + line_height - 5), 1)

    def draw_no_arrivals(self):
        """Draw message when no arrivals available"""
        no_data_text = route_font.render("🔭 No arrival information available", True, WARNING_COLOR)
        no_data_rect = no_data_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(no_data_text, no_data_rect)

        current_time = datetime.now().strftime('%I:%M:%S %p')
        time_text = time_font.render(f"📅 Last Updated: {current_time}", True, TEXT_COLOR)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(time_text, time_rect)

    def display_arrivals(self, arrivals):
        """Main display function - replaces the console print version"""
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False

        # Clear screen
        self.screen.fill(BACKGROUND_COLOR)

        if arrivals:
            # Get stop name from first arrival
            stop_name = arrivals[0].get('stop_name', 'Unknown Stop')

            # Draw all components
            self.draw_header(stop_name)
            self.draw_column_headers()
            self.draw_arrivals(arrivals)
        else:
            self.draw_header("Unknown Stop")
            self.draw_no_arrivals()

        # Update display
        pygame.display.flip()
        self.clock.tick(60)
        return True

    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()


# Global display instance
bus_display = None


def input_thread(a_list):
    raw_input()  # use input() in Python3
    a_list.append(True)


def safe_get_nested_value(data, *keys, default=None):
    """Safely get nested dictionary values"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data


def load_config(config_path="ProviderConfig.json"):
    """Load configuration with error handling"""
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Failed to load config: {e}")
        return None


def make_api_request(url, headers=None, timeout=30):
    """Make API request with proper error handling"""
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        return None


def calculate_time_to_arrival(arrival_time_str):
    """Calculate time to arrival in minutes"""
    if not arrival_time_str:
        return None

    try:
        # Parse the arrival time (ISO format)
        arrival_time = datetime.fromisoformat(arrival_time_str.replace('Z', '+00:00'))

        # Get current time in the same timezone
        current_time = datetime.now(timezone.utc)

        # Calculate difference in minutes
        time_diff = arrival_time - current_time
        minutes_to_arrival = int(time_diff.total_seconds() / 60)

        return minutes_to_arrival if minutes_to_arrival > 0 else 0
    except (ValueError, TypeError) as e:
        logging.warning(f"Could not parse arrival time {arrival_time_str}: {e}")
        return None


def format_arrival_time(arrival_time_str):
    """Format arrival time for display"""
    if not arrival_time_str:
        return "Unknown"

    try:
        # Parse the arrival time and convert to local time
        arrival_time = datetime.fromisoformat(arrival_time_str.replace('Z', '+00:00'))

        # Convert to Eastern Time (MBTA is in Boston)
        eastern = pytz.timezone('US/Eastern')
        local_time = arrival_time.astimezone(eastern)

        return local_time.strftime('%I:%M %p')
    except (ValueError, TypeError):
        return arrival_time_str


def extract_route_info(included_data, route_id):
    """Extract route information from included data"""
    if not included_data or not route_id:
        return {"short_name": "Unknown", "long_name": "Unknown Route"}

    for item in included_data:
        if item.get('type') == 'route' and item.get('id') == route_id:
            attributes = item.get('attributes', {})
            return {
                "short_name": attributes.get('short_name', 'Unknown'),
                "long_name": attributes.get('long_name', 'Unknown Route'),
                "route_type": attributes.get('type', 0)
            }

    return {"short_name": "Unknown", "long_name": "Unknown Route", "route_type": 0}


def get_route_type_name(route_type):
    """Convert route type number to readable name"""
    route_types = {
        0: "Light Rail",
        1: "Heavy Rail",
        2: "Commuter Rail",
        3: "Bus",
        4: "Ferry"
    }
    return route_types.get(route_type, "Transit")



def get_bus_arrivals():
    """Get bus arrivals with comprehensive error handling"""
    # Load configuration
    config = load_config()
    if config is None:
        logging.error("Configuration not available")
        return []

    # Extract configuration values safely
    provider_config = config.get('transport_provider', {})
    bus_stop = config.get('bus_stop', {})
    request_settings = config.get('request_settings', {})

    base_url = provider_config.get('base_url')
    endpoint_template = safe_get_nested_value(provider_config, 'endpoints', 'arrivals')
    api_key = provider_config.get('api_key')
    headers = provider_config.get('headers', {})
    stop_id = bus_stop.get('id')
    stop_name = bus_stop.get('name', 'Unknown Stop')
    timeout = request_settings.get('timeout', 30)
    max_arrivals = request_settings.get('max_arrivals', 10)

    # Validate required parameters
    if not all([base_url, endpoint_template, stop_id]):
        logging.error("Missing required configuration parameters")
        return []

    # Build URL with include parameter to get route information
    endpoint = endpoint_template.format(stop_id=stop_id)
    url = f"{base_url}{endpoint}&include=route&page[limit]={max_arrivals}"

    # Add API key to headers if available
    if api_key:
        headers = headers.copy()  # Don't modify original headers
        headers['X-API-Key'] = api_key

    # Make API request
    data = make_api_request(url, headers, timeout)
    if data is None:
        logging.error("Failed to fetch arrival data")
        return []

    # Process arrivals safely
    arrivals = []
    predictions = data.get('data', [])
    included_data = data.get('included', [])

    for prediction in predictions:
        attributes = prediction.get('attributes', {})
        relationships = prediction.get('relationships', {})

        arrival_time = attributes.get('arrival_time')
        departure_time = attributes.get('departure_time')

        # Use arrival_time if available, otherwise departure_time
        predicted_time = arrival_time or departure_time

        if predicted_time:
            # Get route information
            route_relationship = relationships.get('route', {})
            route_data = route_relationship.get('data', {})
            route_id = route_data.get('id') if route_data else None

            route_info = extract_route_info(included_data, route_id)

            # Calculate time to arrival
            minutes_to_arrival = calculate_time_to_arrival(predicted_time)
            formatted_time = format_arrival_time(predicted_time)

            arrivals.append({
                'route_short_name': route_info['short_name'],
                'route_long_name': route_info['long_name'],
                'route_type': get_route_type_name(route_info.get('route_type', 3)),
                'arrival_time': predicted_time,
                'formatted_time': formatted_time,
                'minutes_to_arrival': minutes_to_arrival,
                'direction_id': attributes.get('direction_id'),
                'status': attributes.get('status'),
                'stop_name': stop_name
            })

    # Sort by arrival time
    arrivals.sort(key=lambda x: x['arrival_time'] if x['arrival_time'] else '')

    return arrivals


def display_arrivals(arrivals):
    """Display arrival information using pygame"""
    global bus_display

    if bus_display is None:
        bus_display = BusArrivalDisplay()

    # Use the pygame display instead of console prints
    return bus_display.display_arrivals(arrivals)


def run_monitoring():
    global bus_display

    q = Queue()
    print("🚀 Starting transit arrival monitoring...")
    print("❸️  Press ESC in the display window to stop")
    print()

    try:
        while True:
            # Fetch arrivals
            arrivals = get_bus_arrivals()

            # Display using pygame - returns False if user wants to quit
            if not display_arrivals(arrivals):
                break

            # Small delay to prevent excessive CPU usage
            time.sleep(1)

    except KeyboardInterrupt:
        print("Monitoring stopped by user")
    finally:
        if bus_display:
            bus_display.cleanup()


def main():
    """Main function with error handling"""
    try:
        run_monitoring()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print("❌ An error occurred while running the monitoring system")
    finally:
        # Ensure pygame is properly cleaned up
        if 'bus_display' in globals() and bus_display:
            bus_display.cleanup()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING,  # Changed to WARNING to reduce console noise
                        format='%(asctime)s - %(levelname)s - %(message)s')
    main()
