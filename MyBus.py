 # -*- coding: utf-8 -*-
import json
import requests
import logging
from datetime import datetime, timezone
import time
import os
import tty

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
        return arrival_time.strftime('%I:%M %p')
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


def get_route_type(route_type):
    """Convert route type number to emoji"""
    route_types = {
        0: "🚈",
        1: "🚃",
        2: "🚋",
        3: "🚌",
        4: "⛴️"
    }
    return route_types.get(route_type, "Transit")


def clear_screen():
    """Clear the console screen"""
    os.system('clear')


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
    """Display arrival information"""
    # Clear screen for clean updates
    clear_screen()

    # Get current time for display
    current_time = datetime.now().strftime('%I:%M:%S %p')

    if arrivals:
        # Print header with stop information
        stop_name = arrivals[0]['stop_name']
        print(f"Live Arrivals for {stop_name}")
        print(f"Updated: {current_time}")
        print()

        for i, arrival in enumerate(arrivals, 1):
            route_name = arrival.get('route_short_name', 'Unknown')
            route_type = arrival.get('route_type', 'Transit')
            formatted_time = arrival.get('formatted_time', 'Unknown')
            minutes_to_arrival = arrival.get('minutes_to_arrival')
            status = arrival.get('status', 'Scheduled')
            direction_id = arrival.get('direction_id', '')

            # Format time to arrival
            if minutes_to_arrival is not None:
                if minutes_to_arrival == 0:
                    time_display = "⚡Arriving now!"
                elif minutes_to_arrival == 1:
                    time_display = "⏱️ 1 minute"
                elif minutes_to_arrival <= 5:
                    time_display = f"{minutes_to_arrival} minutes"
                else:
                    time_display = f"{minutes_to_arrival} minutes"
            else:
                time_display = "Unknown"

            # Format direction
            direction_text = f" (Direction {direction_id})" if direction_id != '' else ""

            
            print(f"{route_type} Route {route_name} : {formatted_time} ({time_display})")
            print(f"")
    else:
        print(f“­⛔ No arrival information available")
        print(f"Last Updated: {current_time}")
        print()


def run_monitoring():
    print("Starting transit arrival monitoring...")
    print("Press ctl-C to stop")
    print()
    outtahere =  False
    while not outtahere:
        # Fetch and display arrivals
        arrivals = get_bus_arrivals()
        display_arrivals(arrivals)
        # Wait for 60 seconds
        time.sleep(60)
        clear_screen()
    else:
        quit()

def main():
    """Main function with error handling"""
    try:
        run_monitoring()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print("⛔ An error occurred while running the monitoring system")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING,  # Changed to WARNING to reduce console noise
                        format='%(asctime)s - %(levelname)s - %(message)s')
    main()
