import os
import requests
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool

load_dotenv()
MAPS_API_KEY = os.getenv("MAPS_API_KEY")


# Google Maps - Places Nearby Search API
def search_places_on_route(origin: str, destination: str, place_type: str) -> dict:
    """Search for places along the route between two locations.
    
    Args:
        origin: Starting location
        destination: End location  
        place_type: What to search for (e.g., 'gas station', 'restaurant', 'hotel', 'atm', 'hospital')
    """
    # Get route to find midpoint
    dir_response = requests.get(
        "https://maps.googleapis.com/maps/api/directions/json",
        params={"origin": origin, "destination": destination, "key": MAPS_API_KEY},
        timeout=20,
    )
    dir_data = dir_response.json()

    if dir_data.get("status") != "OK":
        return {"error": "Could not find route"}

    # Get midpoint from route
    steps = dir_data["routes"][0]["legs"][0]["steps"]
    mid = steps[len(steps) // 2]["end_location"]

    # Search for places near midpoint
    places_response = requests.get(
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
        params={
            "location": f"{mid['lat']},{mid['lng']}",
            "radius": 5000,
            "keyword": place_type,
            "key": MAPS_API_KEY,
        },
        timeout=20,
    )
    places_data = places_response.json()

    if not places_data.get("results"):
        return {"error": f"No {place_type} found along the route"}

    # Return top 5 places
    places = []
    for p in places_data["results"][:5]:
        places.append({
            "name": p.get("name"),
            "rating": p.get("rating", "N/A"),
            "address": p.get("vicinity"),
            "maps_link": f"https://www.google.com/maps/place/?q=place_id:{p.get('place_id')}",
        })

    return {"query": place_type, "places": places}


# Google Maps - Directions API Call
def get_directions(origin: str, destination: str, mode: str = "driving") -> dict:
    """Get route summary using Google Directions API."""
    url = "https://maps.googleapis.com/maps/api/directions/json"
    r = requests.get(
        url,
        params={"origin": origin, "destination": destination, "mode": mode, "key": MAPS_API_KEY},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()

    if data.get("status") != "OK" or not data.get("routes"):
        return {"status": data.get("status"), "error": data.get("error_message", "No route found")}

    leg = data["routes"][0]["legs"][0]
    return {
        "origin": leg["start_address"],
        "destination": leg["end_address"],
        "distance": leg["distance"]["text"],
        "duration": leg["duration"]["text"],
        "google_maps_link": f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode={mode}",
    }

# Agent 
directions_tool = FunctionTool(get_directions)
places_tool = FunctionTool(search_places_on_route)

root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="Maps_Agent",
    instruction=(
        "You are a helpful Maps assistant.\n"
        "Use appropriate tools to answer user's query:\n"
        "1) TOOL: Get directions between two locations\n"
        "2) TOOL: Search for nearby places based on the location\n"
        "Always return a short answer + the Google Maps link if applicable"
    ),
    tools=[directions_tool, places_tool]
)
