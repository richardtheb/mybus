# Transit Arrival Monitor

A cross-platform Python application that provides real-time transit arrival information for bus stops, trains, and other public transportation. The application continuously monitors and displays live arrival times with an intuitive console interface.

## Features

🚌 **Real-time Arrivals**: Live arrival predictions for buses, trains, and other transit vehicles
🔄 **Auto-refresh**: Automatically updates every 60 seconds
⌨️ **Keyboard Control**: Press any key to stop monitoring
🖥️ **Cross-platform**: Works on Windows, macOS, and Linux
🕒 **Smart Time Display**: Shows both absolute arrival times and countdown minutes
🚦 **Multiple Transit Types**: Supports buses, light rail, heavy rail, commuter rail, and ferries
⚡ **Visual Indicators**: Special highlighting for imminent arrivals (≤5 minutes)

## Requirements

- Python 3.7+
- Internet connection for API access
- Required packages (see Installation)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```shell script
pip install -r package_requirements.txt
```


Or install manually:
```shell script
pip install requests pytz
```


## Configuration

1. Copy `ProviderConfig.json` and customize it for your transit provider and stop:

```json
{
  "transport_provider": {
    "name": "MBTA",
    "base_url": "https://api-v3.mbta.com",
    "endpoints": {
      "arrivals": "/predictions?filter[stop]={stop_id}&sort=arrival_time"
    },
    "api_key": "YOUR_API_KEY_HERE",
    "headers": {
      "Content-Type": "application/json",
      "Accept": "application/vnd.api+json"
    }
  },
  "bus_stop": {
    "id": "YOUR_STOP_ID",
    "name": "Your Stop Name"
  },
  "request_settings": {
    "timeout": 30,
    "max_arrivals": 10
  }
}
```


2. Update the configuration with your specific details:
   - **API Key**: Obtain from your transit provider (if required)
   - **Stop ID**: The unique identifier for your transit stop
   - **Base URL**: API endpoint for your transit provider
   - **Stop Name**: Human-readable name for display

## Usage

Run the application:

```shell script
python transit_monitor.py
```


The application will:
1. Start monitoring and display "🚀 Starting transit arrival monitoring..."
2. Show live arrivals with route numbers, arrival times, and countdown minutes
3. Refresh automatically every 60 seconds
4. Continue until you press any key

### Sample Output

```
🚌 Live Arrivals for Massachusetts Ave @ Sidney St
Updated: 2:30:15 PM

🚌 Route 1 : 2:35 PM (⚡ 5 minutes)
🚇 Route Red : 2:38 PM (8 minutes)
🚌 Route 47 : 2:42 PM (12 minutes)
```


## Supported Transit Providers

The application is designed to work with any transit API that follows RESTful patterns. It has been tested with:

- **MBTA** (Massachusetts Bay Transportation Authority)
- Other GTFS-RT compatible APIs

To add support for other providers, update the `ProviderConfig.json` with the appropriate API endpoints and parameters.

## Key Components

- **KeyboardMonitor**: Cross-platform keyboard input detection
- **API Integration**: Robust HTTP request handling with error recovery
- **Time Calculations**: Accurate arrival time processing with timezone support
- **Display Engine**: Clean, emoji-enhanced console output
- **Configuration System**: Flexible JSON-based setup

## Error Handling

The application includes comprehensive error handling for:
- Network connectivity issues
- API timeouts and errors
- Invalid configuration files
- Missing or malformed data
- Platform-specific keyboard input variations

## Troubleshooting

**No arrivals showing**: 
- Verify your stop ID is correct
- Check that your API key is valid (if required)
- Ensure internet connectivity

**Application won't stop**:
- Try Ctrl+C as a fallback
- Check that your terminal supports keyboard input detection

**Configuration errors**:
- Validate your JSON syntax
- Ensure all required fields are present
- Check API endpoint URLs

## Contributing

Feel free to submit issues, feature requests, or pull requests. The code is structured to make it easy to add support for additional transit providers.

## License

This project is open source. Please check with your transit provider regarding their API usage terms and conditions.
