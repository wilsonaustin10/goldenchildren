#!/usr/bin/env python3
"""
Script to generate a JSON file with Oscar nominees data and save it locally.
This can be used as a reference for testing the BrowserUse functionality.
"""

import json
import os
from datetime import datetime

def generate_oscar_nominees_data():
    """Generate structured data for Oscar nominees."""
    
    # Data structure for Oscar nominees by year and category
    oscar_data = {
        "2021": {
            "best_supporting_actor": [
                {
                    "name": "Daniel Kaluuya",
                    "film": "Judas and the Black Messiah",
                    "won": True,
                    "imdb_profile": "https://www.imdb.com/name/nm2257207/"
                },
                {
                    "name": "Sacha Baron Cohen",
                    "film": "The Trial of the Chicago 7",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm0056187/"
                },
                {
                    "name": "Leslie Odom Jr.",
                    "film": "One Night in Miami",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm0644865/"
                },
                {
                    "name": "Paul Raci",
                    "film": "Sound of Metal",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm0705067/"
                },
                {
                    "name": "LaKeith Stanfield",
                    "film": "Judas and the Black Messiah",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm3147751/"
                }
            ],
            "best_supporting_actress": [
                {
                    "name": "Youn Yuh-jung",
                    "film": "Minari",
                    "won": True,
                    "imdb_profile": "https://www.imdb.com/name/nm0950926/"
                },
                {
                    "name": "Maria Bakalova",
                    "film": "Borat Subsequent Moviefilm",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm10079638/"
                },
                {
                    "name": "Glenn Close",
                    "film": "Hillbilly Elegy",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm0000335/"
                },
                {
                    "name": "Olivia Colman",
                    "film": "The Father",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm1469236/"
                },
                {
                    "name": "Amanda Seyfried",
                    "film": "Mank",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm1086543/"
                }
            ],
            "best_actor": [
                {
                    "name": "Anthony Hopkins",
                    "film": "The Father",
                    "won": True,
                    "imdb_profile": "https://www.imdb.com/name/nm0000164/"
                },
                {
                    "name": "Riz Ahmed",
                    "film": "Sound of Metal",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm1981893/"
                },
                {
                    "name": "Chadwick Boseman",
                    "film": "Ma Rainey's Black Bottom",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm1569276/"
                },
                {
                    "name": "Gary Oldman",
                    "film": "Mank",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm0000198/"
                },
                {
                    "name": "Steven Yeun",
                    "film": "Minari",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm3081796/"
                }
            ],
            "best_actress": [
                {
                    "name": "Frances McDormand",
                    "film": "Nomadland",
                    "won": True,
                    "imdb_profile": "https://www.imdb.com/name/nm0000531/"
                },
                {
                    "name": "Viola Davis",
                    "film": "Ma Rainey's Black Bottom",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm0205626/"
                },
                {
                    "name": "Andra Day",
                    "film": "The United States vs. Billie Holiday",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm4731677/"
                },
                {
                    "name": "Vanessa Kirby",
                    "film": "Pieces of a Woman",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm3948952/"
                },
                {
                    "name": "Carey Mulligan",
                    "film": "Promising Young Woman",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm1659547/"
                }
            ]
        },
        "2022": {
            "best_supporting_actor": [
                {
                    "name": "Troy Kotsur",
                    "film": "CODA",
                    "won": True,
                    "imdb_profile": "https://www.imdb.com/name/nm0468045/"
                },
                {
                    "name": "Ciarán Hinds",
                    "film": "Belfast",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm0001354/"
                },
                {
                    "name": "Jesse Plemons",
                    "film": "The Power of the Dog",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm0687146/"
                },
                {
                    "name": "J.K. Simmons",
                    "film": "Being the Ricardos",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm0799777/"
                },
                {
                    "name": "Kodi Smit-McPhee",
                    "film": "The Power of the Dog",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm2240346/"
                }
            ]
        },
        "2023": {
            "best_supporting_actor": [
                {
                    "name": "Ke Huy Quan",
                    "film": "Everything Everywhere All at Once",
                    "won": True,
                    "imdb_profile": "https://www.imdb.com/name/nm0702841/"
                },
                {
                    "name": "Brendan Gleeson",
                    "film": "The Banshees of Inisherin",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm0322407/"
                },
                {
                    "name": "Brian Tyree Henry",
                    "film": "Causeway",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm3109964/"
                },
                {
                    "name": "Judd Hirsch",
                    "film": "The Fabelmans",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm0002139/"
                },
                {
                    "name": "Barry Keoghan",
                    "film": "The Banshees of Inisherin",
                    "won": False,
                    "imdb_profile": "https://www.imdb.com/name/nm4422686/"
                }
            ]
        }
    }
    
    # Add metadata
    result = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "description": "Oscar nominees data for testing BrowserUse functionality",
            "version": "1.0"
        },
        "data": oscar_data
    }
    
    return result

def save_json_file(data, filename="oscar_nominees_data.json"):
    """Save data to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully saved data to {os.path.abspath(filename)}")
        return True
    except Exception as e:
        print(f"❌ Error saving JSON file: {str(e)}")
        return False

def main():
    """Main function to generate and save Oscar nominees data."""
    print("Generating Oscar nominees data...")
    data = generate_oscar_nominees_data()
    
    # Save the data to a JSON file
    save_json_file(data)
    
    # Print a sample of the data
    print("\nSample data (2021 Best Supporting Actor nominees):")
    for nominee in data["data"]["2021"]["best_supporting_actor"]:
        winner_status = "🏆 WINNER" if nominee["won"] else ""
        print(f"- {nominee['name']} ({nominee['film']}) {winner_status}")
        print(f"  IMDB: {nominee['imdb_profile']}")
    
    print("\nThis data can be used for testing the BrowserUse functionality.")
    print("You can use the prompt: 'Find IMDB profiles for the 2021 Oscar nominated actors for best supporting actor'")

if __name__ == "__main__":
    main() 