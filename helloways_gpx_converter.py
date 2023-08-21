import requests
import re

HELLOWAYS_URL = "https://www.helloways.com"


def get_trackid_from_helloways(url: str) -> str:
    page = requests.get(url)
    page.raise_for_status()
    track_id = re.search(r"tracks/(.*?)/img-md", page.text)
    if track_id:
        return track_id.group(1)
    else:
        raise Exception("Track id not found")


def get_json_from_trackid(trackid: str) -> dict:
    url = f"{HELLOWAYS_URL}/api/tracks/{trackid}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def convert_to_gpx(json_file: dict) -> (str, str):
    path = json_file["path"]
    gpx = f"""<?xml version="1.0" encoding="UTF-8"?>
    <gpx version="1.1" creator="Helloways" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
        <trk>
            <name>{json_file["name"]}</name>
            <trkseg>"""
    for point in path["features"][0]["geometry"]["coordinates"]:
        gpx += f"""
                <trkpt lat="{point[1]}" lon="{point[0]}">
                    <ele>{int(point[2])}</ele>
                </trkpt>"""
    gpx += """
            </trkseg>
        </trk>
    </gpx>"""
    return (json_file["name"], gpx)


if __name__ == "__main__":
    try:
        track_url = input("Enter the URL of the Helloways hiking route you want to convert: ")
        track_id = get_trackid_from_helloways(track_url)
        json_file = get_json_from_trackid(track_id)
        name, gpx = convert_to_gpx(json_file)
        name = name.replace(" ", "_")
        with open(f"{name}.gpx", "w") as f:
            f.write(gpx)
        print(f"GPX file saved as {name}.gpx")
    except Exception as e:
        print(f"An error occurred: {e}")
