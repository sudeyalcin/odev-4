from __future__ import annotations
from typing import List, Dict, Any, Tuple
import numpy as np
import requests
from geopy.geocoders import Nominatim
import time

def geocode_locations(locations: List[Dict[str, Any]]) -> List[Tuple[float, float]]:
    """
    Geocode each location["address"] into (lat, lng) using free Nominatim service.
    """
    geolocator = Nominatim(user_agent="aco_route_optimizer_v1.0")
    coords: List[Tuple[float, float]] = []

    for loc in locations:
        addr = loc["address"]
        try:
            # Try different address formats for better success rate
            address_variants = [
                f"{addr}, Turkey",  # Original with Turkey
                f"{addr}, Antalya, Turkey",  # Add city
                addr,  # Original without Turkey
                # Simplify address by removing detailed parts
                addr.split(',')[0] + ", Antalya, Turkey" if ',' in addr else f"{addr}, Antalya, Turkey"
            ]
            
            location = None
            for variant in address_variants:
                try:
                    print(f"  Trying: {variant}")
                    location = geolocator.geocode(variant, timeout=15)
                    if location:
                        print(f"  ✅ Success with: {variant}")
                        break
                    time.sleep(1)  # Be nice to the service
                except Exception as e:
                    print(f"  ⚠️ Failed with {variant}: {str(e)}")
                    time.sleep(1)
                    continue
            
            if location:
                coords.append((float(location.latitude), float(location.longitude)))
                print(f"  📍 {loc['name']}: {location.latitude:.6f}, {location.longitude:.6f}")
            else:
                # Fallback: Use approximate coordinates for Antalya/Muratpaşa
                print(f"  ⚠️ Using fallback coordinates for: {loc['name']}")
                # Approximate center of Muratpaşa, Antalya
                fallback_coords = (36.8969, 30.7133)  # Muratpaşa center
                coords.append(fallback_coords)
            
            time.sleep(2)  # Be extra nice to the free service
            
        except Exception as e:
            print(f"  ❌ Complete failure for {loc['name']}: {str(e)}")
            # Use fallback coordinates
            fallback_coords = (36.8969, 30.7133)  # Muratpaşa center
            coords.append(fallback_coords)
    
    return coords

def distance_matrix_meters(coords: List[Tuple[float, float]]) -> np.ndarray:
    """
    Build NxN driving distance matrix (meters) using free OSRM service.
    """
    n = len(coords)
    dist = np.zeros((n, n), dtype=float)
    
    # OSRM public server (free but rate limited)
    base_url = "http://router.project-osrm.org/table/v1/driving/"
    
    # Create coordinate string for OSRM
    coord_str = ";".join([f"{lng},{lat}" for lat, lng in coords])
    
    try:
        url = f"{base_url}{coord_str}?annotations=distance"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("code") != "Ok":
            raise ValueError(f"OSRM API error: {data.get('message', 'Unknown error')}")
        
        distances = data["distances"]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    dist[i, j] = 0.0
                else:
                    # OSRM returns distances in meters
                    dist[i, j] = float(distances[i][j])
        
        # Be nice to the free service
        time.sleep(1)
        
    except Exception as e:
        print(f"⚠️ OSRM API failed, using Euclidean distances as fallback: {str(e)}")
        # Fallback to Euclidean distance (not ideal but works)
        for i in range(n):
            for j in range(n):
                if i == j:
                    dist[i, j] = 0.0
                else:
                    lat1, lng1 = coords[i]
                    lat2, lng2 = coords[j]
                    # Approximate distance in meters using Haversine formula
                    dist[i, j] = _haversine_distance(lat1, lng1, lat2, lng2)
    
    return dist

def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth (in meters).
    """
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    return c * r
