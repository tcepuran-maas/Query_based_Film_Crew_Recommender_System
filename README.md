# Query based Film Crew Recommender System

This project builds a knowledge-graph-based recommendation workflow for film cast and crew collaborations using TMDb data. It creates an ontology, transforms movie/person/crew records into RDF triples, and supports SPARQL-driven analysis to identify strong collaboration patterns for specific creative roles. The goal is to enable query-based recommendations (e.g., actor–composer combinations) from structured film-industry metadata.


# Data Access:

To use these Scripts you need to have data from TMDb.
You can get the data by using following API-Endpoints when having an API-Key

| API-Endpoint         | URL                                                     |
| -------------------- | ------------------------------------------------------- |
| **Movie Discovery:** | `https://api.themoviedb.org/3/discover/movie`           |
| **Movie Details:**   | `https://api.themoviedb.org/3/movie/{movie_id}`         |
| **Movie Credits:**   | `https://api.themoviedb.org/3/movie/{movie_id}/credits` |
| **Persons:**         | `https://api.themoviedb.org/3/person/{person_id}`       |


The following fields are nessesery for using the Build_Graph.py Script.






| Table/API-Endpoint | Field             | Description                                 |
| ------------------ | ----------------- | ------------------------------------------- |
| Movie Details      | id                | Unique identifier for the movie             |
| Movie Details      | title             | Movie title                                 |
| Movie Details      | vote_average      | Average rating                              |
| Movie Details      | vote_count        | Number of votes                             |
| Movie Details      | release_date      | Release date of the movie                   |
| Movie Details      | runtime           | Duration in minutes                         |
| Movie Details      | original_language | Language code (e.g., "en")                  |
| Movie Details      | popularity        | Popularity score                            |
| Movie Details      | imdb_id           | IMDb identifier                             |
| Movie Details      | genres            | List of genres (e.g., ["Action", "Comedy"]) |
| Movie Credits      | movie_id          | Reference to Movie in Movie Details         |
| Movie Credits      | person_id         | Reference to unique person ID in Persons    |
| Movie Credits      | cast_or_crew      | Either "cast" or "crew"                     |
| Movie Credits      | job               | Crew job title (e.g., "Director", "Writer") |
| Movie Credits      | character         | Character name (if cast member)             |
| Movie Credits      | cast_id           | Cast position in the movies credits         |
| Movie Credits      | imdb_id           | IMDb identifier                             |
| Persons            | person_id         | Unique identifier for the person            |
| Persons            | name              | Full name                                   |
| Persons            | gender            | Gender of the person                        |
| Persons            | birthday          | Date of birth                               |
| Persons            | deathday          | Date of death (if applicable)               |
| Persons            | place_of_birth    | Birthplace                                  |
| Persons            | imdb_id           | IMDb identifier of the person               |

Cast and crew members have different attributes but were grouped together. A new attribute, `cast_or_crew`, was therefore added. The fields `cast_or_crew`, `character`, and `cast_id` are only relevant for cast members. The `job` field, on the other hand, is only relevant for crew members.


# Intended Pipeline
![Pipeline](pipeline.png)



# Ontology 

In the following all the Properties are described in a table: 

| Property               | Type             | Domain                 | Range                  |
| ---------------------- | ---------------- | ---------------------- | ---------------------- |
| ex:hasParticipant      | ObjectProperty   | ex:Participation       | schema:Person          |
| ex:hasRole             | ObjectProperty   | ex:Participation       | schema:Role            |
| ex:inMovie             | ObjectProperty   | ex:Participation       | schema:Movie           |
| schema:birthPlace      | ObjectProperty   | schema:Person          | schema:Place           |
| schema:aggregateRating | ObjectProperty   | schema:Movie           | schema:AggregateRating |
| schema:genre           | ObjectProperty   | schema:Movie           | ex:Genre               |
| ex:castOrder           | DatatypeProperty | ex:Participation       | xsd:integer            |
| ex:playedCharacter     | DatatypeProperty | ex:Participation       | xsd:string             |
| schema:birthDate       | DatatypeProperty | schema:Person          | xsd:date               |
| schema:deathDate       | DatatypeProperty | schema:Person          | xsd:date               |
| schema:gender          | DatatypeProperty | schema:Person          | xsd:string             |
| schema:datePublished   | DatatypeProperty | schema:Movie           | xsd:date               |
| schema:duration        | DatatypeProperty | schema:Movie           | xsd:integer            |
| schema:inLanguage      | DatatypeProperty | schema:Movie           | xsd:string             |
| ex:popularity          | DatatypeProperty | schema:Movie           | xsd:float              |
| schema:ratingCount     | DatatypeProperty | schema:AggregateRating | xsd:integer            |
| schema:ratingValue     | DatatypeProperty | schema:AggregateRating | xsd:float              |
| schema:roleName        | DatatypeProperty | schema:Role            | xsd:string             |

# Use the Pipeline

need for `movie_crew.csv`, `movie_details.csv`, `persons.csv` to use pipeline and all `person_id`s and `movie_id`s  in `movie_crew` need to have a corresponding entry in the other files. 

An example of the pipeline is used in the `Pipeline_Ridley_Scott_Example.ipynb` so feel free to use this one to write your own queries.
You just need to modify the Query Prefiltering Parameters and the SPARQL Query itself.
