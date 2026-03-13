from pathlib import Path
import json
import re
from urllib.parse import quote

import pandas as pd
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD, OWL


# =========================
# Configuration (adjust at the beginning)
# =========================
BASE_DIR = Path(__file__).resolve().parent

MOVIE_DETAILS_CSV = BASE_DIR / "data" / "movie_details.csv"
MOVIE_CREW_CSV = BASE_DIR / "data" / "movie_crew.csv"
PERSONS_CSV = BASE_DIR / "data" / "persons.csv"

ONTOLOGY_TTL = BASE_DIR / "data" / "ontology.ttl"
OUTPUT_TTL = BASE_DIR / "data" / "film_crew.ttl"


SCHEMA = Namespace("https://schema.org/")
EX = Namespace("http://example.org/")
TMDB = Namespace("https://www.themoviedb.org/")
IMDB = Namespace("https://www.imdb.com/")


MOVIE_DETAILS_DF = None
MOVIE_CREW_DF = None
PERSONS_DF = None


def load_data() -> None:
    global  MOVIE_DETAILS_DF, MOVIE_CREW_DF, PERSONS_DF

    MOVIE_DETAILS_DF = pd.read_csv(MOVIE_DETAILS_CSV, sep=",", on_bad_lines="skip", engine="python")
    MOVIE_CREW_DF = pd.read_csv(MOVIE_CREW_CSV, sep=",", on_bad_lines="skip", engine="python")
    PERSONS_DF = pd.read_csv(PERSONS_CSV, sep=",", on_bad_lines="skip", engine="python")


def init_graph() -> Graph:
    graph = Graph()
    graph.parse(ONTOLOGY_TTL, format="turtle")

    graph.bind("schema", SCHEMA)
    graph.bind("ex", EX)
    graph.bind("tmdb", TMDB)
    graph.bind("imdb", IMDB)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("xsd", XSD)
    return graph


def uri_safe(value: str) -> str:
    if value is None:
        return ""
    safe_value = str(value).strip()
    safe_value = re.sub(r"\s+", "-", safe_value)
    safe_value = safe_value.lower()
    return quote(safe_value, safe="")


def countryToURI(country):
    return URIRef(EX + "place/" + uri_safe(country))


def personToURI(person_id):
    return URIRef(TMDB + "person/" + uri_safe(person_id))


def movieToURI(movie_id):
    return URIRef(TMDB + "movie/" + uri_safe(movie_id))


def imdbPersonToURI(imdb_id):
    return URIRef(IMDB + "name/" + str(imdb_id) + "/")


def imdbMovieToURI(imdb_id):
    return URIRef(IMDB + "title/" + str(imdb_id) + "/")


def genreToURI(genre):
    return URIRef(TMDB + "genre/" + uri_safe(str(genre["id"]) + "-" + str(genre["name"])))


def participationToURI(movie_id, person_id):
    return URIRef(EX + "participation/" + uri_safe(str(movie_id)) + "/" + uri_safe(str(person_id)))


def aggregateRatingToURI(movie_id):
    return URIRef(EX + "aggregateRating/" + uri_safe(str(movie_id)))


def roleToURI(role):
    return URIRef(EX + "role/" + uri_safe(str(role)))


def getGender(gender_id):
    if gender_id == 1:
        return "f"
    if gender_id == 2:
        return "m"
    if gender_id == 0:
        return "u"
    return "b"


def getCountry(birthplace):
    if pd.isna(birthplace) or str(birthplace).strip() == "":
        return None
    return birthplace.split(",")[-1].strip()


def getAllGenres(genres_json):
    if isinstance(genres_json, pd.Series):
        genres_json = genres_json.dropna()
        if genres_json.empty:
            return []
        genres_json = genres_json.iloc[0]

    if pd.isna(genres_json) or str(genres_json).strip() == "":
        return []

    try:
        parsed = json.loads(genres_json)
    except (TypeError, json.JSONDecodeError):
        return []

    return [{"id": g["id"], "name": g["name"]} for g in parsed if "id" in g and "name" in g]


def getAllRoles(participations_rows):
    roles = set()
    participations_cast = participations_rows[participations_rows["cast_or_crew"] == "cast"]
    if not participations_cast.empty:
        roles.update(["Actor"])

    participations_crew = participations_rows[participations_rows["cast_or_crew"] == "crew"]
    for job in participations_crew["job"]:
        if pd.notna(job) and str(job).strip() != "":
            roles.add(job)

    return list(roles)


def addBirthPlace(birthplace, graph):
    birthplace_uri = countryToURI(birthplace)
    graph.add((birthplace_uri, RDF.type, SCHEMA.Country))
    graph.add((birthplace_uri, RDFS.label, Literal(birthplace)))
    graph.add((birthplace_uri, SCHEMA.name, Literal(birthplace, datatype=XSD.string)))


def addRole(role, graph):
    role_uri = roleToURI(role)
    graph.add((role_uri, RDF.type, SCHEMA.Role))
    graph.add((role_uri, RDFS.label, Literal(role)))
    graph.add((role_uri, SCHEMA.roleName, Literal(role, datatype=XSD.string)))


def addPerson(person_id, graph, birthplaces):
    person_uri = personToURI(person_id)
    graph.add((person_uri, RDF.type, SCHEMA.Person))

    person = PERSONS_DF[PERSONS_DF["person_id"] == person_id]
    if person.empty:
        return False

    name = person["name"].values[0]
    person_identifier = person["person_id"].values[0]
    gender = getGender(person["gender"].values[0])

    birthday_raw = person["birthday"].values[0]
    deathday_raw = person["deathday"].values[0]
    imdb_id = person["imdb_id"].values[0] if "imdb_id" in person.columns else None
    birth_date = pd.to_datetime(birthday_raw, errors="coerce") if birthday_raw is not None else None
    death_date = pd.to_datetime(deathday_raw, errors="coerce") if deathday_raw is not None else None

    graph.add((person_uri, RDFS.label, Literal(name)))
    graph.add((person_uri, SCHEMA.identifier, Literal(person_identifier, datatype=XSD.integer)))
    graph.add((person_uri, SCHEMA.name, Literal(name, datatype=XSD.string)))
    graph.add((person_uri, SCHEMA.gender, Literal(gender, datatype=XSD.string)))
    if pd.notna(imdb_id) and str(imdb_id).strip() != "":
        graph.add((person_uri, OWL.sameAs, imdbPersonToURI(imdb_id)))

    if pd.notna(birth_date):
        graph.add((person_uri, SCHEMA.birthDate, Literal(birth_date, datatype=XSD.date)))
    if pd.notna(death_date):
        graph.add((person_uri, SCHEMA.deathDate, Literal(death_date, datatype=XSD.date)))

    birthplace = getCountry(person["place_of_birth"].values[0])
    if birthplace:
        if birthplace not in birthplaces:
            birthplaces.add(birthplace)
            addBirthPlace(birthplace, graph)

        birthplace_uri = countryToURI(birthplace)
        graph.add((person_uri, SCHEMA.birthPlace, birthplace_uri))

    return True


def addAverageRating(movie_id, graph):
    rating_uri = aggregateRatingToURI(movie_id)
    movie = MOVIE_DETAILS_DF[MOVIE_DETAILS_DF["id"] == movie_id]
    title = movie["title"].values[0] if not movie.empty else movie_id
    rating_value = movie["vote_average"].values[0]
    rating_count = movie["vote_count"].values[0]

    graph.add((rating_uri, RDF.type, SCHEMA.AggregateRating))
    graph.add((rating_uri, RDFS.label, Literal(f"average rating of the movie: {title}")))
    graph.add((rating_uri, SCHEMA.ratingValue, Literal(rating_value, datatype=XSD.float)))
    graph.add((rating_uri, SCHEMA.ratingCount, Literal(rating_count, datatype=XSD.integer)))


def addGenre(genre, graph):
    genre_uri = genreToURI(genre)
    graph.add((genre_uri, RDF.type, EX.Genre))
    graph.add((genre_uri, RDFS.label, Literal(genre["name"])))
    graph.add((genre_uri, SCHEMA.name, Literal(genre["name"], datatype=XSD.string)))
    graph.add((genre_uri, SCHEMA.identifier, Literal(genre["id"], datatype=XSD.integer)))


def addMovie(movie_id, graph, genres):
    movie_uri = movieToURI(movie_id)
    graph.add((movie_uri, RDF.type, SCHEMA.Movie))

    movie = MOVIE_DETAILS_DF[MOVIE_DETAILS_DF["id"] == movie_id]
    if movie.empty:
        return

    title = movie["title"].values[0]
    release_raw = movie["release_date"].values[0]
    release_date = pd.to_datetime(release_raw, errors="coerce") if release_raw is not None else None
    runtime = movie["runtime"].values[0]
    original_language = movie["original_language"].values[0]
    popularity = movie["popularity"].values[0]
    imdb_id = movie["imdb_id"].values[0] if "imdb_id" in movie.columns else None

    graph.add((movie_uri, RDFS.label, Literal(title)))
    graph.add((movie_uri, SCHEMA.identifier, Literal(movie_id, datatype=XSD.integer)))
    graph.add((movie_uri, SCHEMA.name, Literal(title, datatype=XSD.string)))
    if pd.notna(imdb_id) and str(imdb_id).strip() != "":
        graph.add((movie_uri, OWL.sameAs, imdbMovieToURI(imdb_id)))
    if pd.notna(release_date):
        graph.add((movie_uri, SCHEMA.datePublished, Literal(release_date, datatype=XSD.date)))
    graph.add((movie_uri, SCHEMA.duration, Literal(runtime, datatype=XSD.integer)))
    graph.add((movie_uri, SCHEMA.inLanguage, Literal(original_language, datatype=XSD.string)))
    graph.add((movie_uri, EX.popularity, Literal(popularity, datatype=XSD.float)))

    rating_uri = aggregateRatingToURI(movie_id)
    graph.add((movie_uri, SCHEMA.aggregateRating, rating_uri))
    addAverageRating(movie_id, graph)

    genres_of_movie = getAllGenres(movie["genres"].values[0])
    for genre in genres_of_movie:
        if genre["id"] not in genres:
            genres.add(genre["id"])
            addGenre(genre, graph)
        graph.add((movie_uri, SCHEMA.genre, genreToURI(genre)))


def addParticipation(movie_id, person_id, graph, movieSet, personSet, roleSet, genres, birthplaces, crew_df):
    participation_uri = participationToURI(movie_id, person_id)
    participations = crew_df[(crew_df["movie_id"] == movie_id) & (crew_df["person_id"] == person_id)]

    graph.add((participation_uri, RDF.type, EX.Participation))
    graph.add((participation_uri, RDFS.label, Literal(f"participation of person {person_id} in movie {movie_id}")))

    if movie_id not in movieSet:
        movieSet.add(movie_id)
        addMovie(movie_id, graph, genres)

    if person_id not in personSet:
        personSet.add(person_id)
        addPerson(person_id, graph, birthplaces)

    movie_uri = movieToURI(movie_id)
    person_uri = personToURI(person_id)

    graph.add((participation_uri, EX.inMovie, movie_uri))
    graph.add((participation_uri, EX.hasParticipant, person_uri))

    roles = getAllRoles(participations)
    for role in roles:
        if role not in roleSet:
            roleSet.add(role)
            addRole(role, graph)
        graph.add((participation_uri, EX.hasRole, roleToURI(role)))

    if (participations["cast_or_crew"] == "cast").any():
        cast_participations = participations[participations["cast_or_crew"] == "cast"]
        for character in cast_participations["character"]:
            if character:
                graph.add((participation_uri, EX.playedCharacter, Literal(character, datatype=XSD.string)))

        cast_order = cast_participations["cast_id"].min()
        graph.add((participation_uri, EX.castOrder, Literal(cast_order, datatype=XSD.integer)))


def generateGraph(save: bool = True, output_path: Path = OUTPUT_TTL, movie_crew_df: pd.DataFrame = None) -> Graph:
    load_data()
    graph = init_graph()
    crew_df = movie_crew_df if movie_crew_df is not None else MOVIE_CREW_DF

    movieSet = set()
    personSet = set()
    roleSet = set()
    genres = set()
    birthplaces = set()
    relevant_persons = set(PERSONS_DF["person_id"])

    for _, row in crew_df.iterrows():
        if row["person_id"] in relevant_persons:
            addParticipation(
                row["movie_id"],
                row["person_id"],
                graph,
                movieSet,
                personSet,
                roleSet,
                genres,
                birthplaces,
                crew_df,
            )

    if save:
        graph.serialize(destination=output_path, format="turtle")

    print(f"Size of the graph: {len(graph)} triples")
    print(f"Saved to: {output_path}")
    return graph


if __name__ == "__main__":
    generateGraph()
