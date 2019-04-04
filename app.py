from dataclasses import dataclass
from itertools import product, islice

import googlemaps
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from settings import config
from patches import patch_gspread

patch_gspread()

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    config.google_credentials_file, scope
)

gc = gspread.authorize(credentials)
gmaps = googlemaps.Client(key=config.google_api_key)
book = gc.open("Thompson Mileage Sheet")


@dataclass
class Location:
    name: str
    address: str


def sheet_as_dicts(worksheet_name):
    iterator = book.worksheet(worksheet_name).get_all_values().__iter__()
    column_names = [q.lower().replace(" ", "_") for q in next(iterator)]
    for values in iterator:
        if values[0].strip():
            yield dict(zip(column_names, values))


def get_distance(origin, destination):
    return (
        gmaps.directions(origin, destination)[0]["legs"][0]["distance"]["value"]
        * 0.000621371
    )


def distances(pairs):
    for origin, destination in pairs:
        if not origin["address"] or not destination["address"]:
            yield (origin["name"], destination["name"], -1)
            continue
        try:
            miles = get_distance(origin["address"], destination["address"])
        except googlemaps.exceptions.ApiError:
            miles = -1
        yield (origin["name"], destination["name"], miles)


def parse_regions(regions):
    return [r.lower().strip() for r in (regions or "").split(",") if r.strip()]


def origins():
    for origin in sheet_as_dicts("Origins"):
        origin["regions"] = parse_regions(origin["regions"])
        yield origin


def destinations():
    for destination in sheet_as_dicts("Destinations"):
        destination["region"] = destination["region"].lower().strip()
        yield destination


def all_od_pairs():
    return (
        (origin, destination)
        for origin, destination in product(origins(), destinations())
        if destination["region"] in origin["regions"]
    )


def od_pairs():
    existing = set(
        (row["origin"], row["destination"]) for row in sheet_as_dicts("Distances")
    )

    def already_looked_up(pair):
        o, d = pair
        return (o["name"], d["name"]) in existing

    return (p for p in all_od_pairs() if not already_looked_up(p))


def chunked(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


if __name__ == "__main__":
    for chunk in chunked(distances(od_pairs()), 10):
        book.worksheet("Distances").append_rows(chunk)

    # print(list(od_pairs()))

    # existing = set(
    #     (row["origin"], row["destination"]) for row in sheet_as_dicts("Distances")
    # )
    # print(existing)
