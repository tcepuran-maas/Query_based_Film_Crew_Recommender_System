from rdflib import Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, RDFS, XSD


g = Graph()

SCHEMA = Namespace("https://schema.org/")
EX = Namespace("http://example.org/")

g.bind("schema", SCHEMA)
g.bind("ex", EX)
g.bind("owl", OWL)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)


# ontology
g.add((EX.MovieCrewOntology, RDF.type, OWL.Ontology))
g.add((EX.MovieCrewOntology, RDFS.label, Literal("Movie Crew Ontology")))
g.add((EX.MovieCrewOntology, RDFS.comment, Literal("Ontology for movies with their cast and crew members")))


# classes
g.add((EX.Genre, RDF.type, OWL.Class))
g.add((EX.Genre, RDFS.label, Literal("Genre")))
g.add((EX.Genre, RDFS.comment, Literal("A genre of movies which can be found on TMDb")))

g.add((EX.Participation, RDF.type, OWL.Class))
g.add((EX.Participation, RDFS.label, Literal("Participation")))
g.add((EX.Participation, RDFS.comment, Literal("A participation of a person in a movie including all the roles they had in that movie. Has no usable URL yet because there is no URL on the web, only for the movie and person.")))

g.add((SCHEMA.Place, RDF.type, OWL.Class))
g.add((SCHEMA.Place, RDFS.label, Literal("Place")))
g.add((SCHEMA.Place, RDFS.comment, Literal("A place somewhere on Earth. Has no usable URL yet because there is no URL on TMDb.")))

g.add((SCHEMA.Country, RDF.type, OWL.Class))
g.add((SCHEMA.Country, RDFS.label, Literal("Country")))
g.add((SCHEMA.Country, RDFS.comment, Literal("A country which is a specific type of place. Has no usable URL yet because there is no URL on TMDb.")))
g.add((SCHEMA.Country, RDFS.subClassOf, SCHEMA.Place))

g.add((SCHEMA.Role, RDF.type, OWL.Class))
g.add((SCHEMA.Role, RDFS.label, Literal("Role in Movie")))
g.add((SCHEMA.Role, RDFS.comment, Literal("A role that a person can have in a movie, e.g. director, actor, producer, etc. Has no usable URL yet because there is no URL on the web, only written on the page of the movie or person.")))

g.add((SCHEMA.AggregateRating, RDF.type, OWL.Class))
g.add((SCHEMA.AggregateRating, RDFS.label, Literal("aggregate rating")))
g.add((SCHEMA.AggregateRating, RDFS.comment, Literal("An aggregate rating of a movie, e.g. the average rating and the number of ratings on TMDb. Has no usable URL yet because there is no URL on the web, only written on the page of the movie.")))

g.add((SCHEMA.Person, RDF.type, OWL.Class))
g.add((SCHEMA.Person, RDFS.label, Literal("Person")))
g.add((SCHEMA.Person, RDFS.comment, Literal("A person involved in the movie industry as cast or crew")))

g.add((SCHEMA.Movie, RDF.type, OWL.Class))
g.add((SCHEMA.Movie, RDFS.label, Literal("Movie")))
g.add((SCHEMA.Movie, RDFS.comment, Literal("A movie which can be found on TMDb")))


# object properties
g.add((EX.hasParticipant, RDF.type, OWL.ObjectProperty))
g.add((EX.hasParticipant, RDFS.label, Literal("has participant")))
g.add((EX.hasParticipant, RDFS.comment, Literal("link to the person participating in a movie")))
g.add((EX.hasParticipant, RDFS.domain, EX.Participation))
g.add((EX.hasParticipant, RDFS.range, SCHEMA.Person))

g.add((EX.hasRole, RDF.type, OWL.ObjectProperty))
g.add((EX.hasRole, RDFS.label, Literal("has role")))
g.add((EX.hasRole, RDFS.comment, Literal("link to the role of a person in a movie, e.g. director, actor, producer, etc.")))
g.add((EX.hasRole, RDFS.domain, EX.Participation))
g.add((EX.hasRole, RDFS.range, SCHEMA.Role))

g.add((EX.inMovie, RDF.type, OWL.ObjectProperty))
g.add((EX.inMovie, RDFS.label, Literal("is in movie")))
g.add((EX.inMovie, RDFS.comment, Literal("link to the movie in which a person participates")))
g.add((EX.inMovie, RDFS.domain, EX.Participation))
g.add((EX.inMovie, RDFS.range, SCHEMA.Movie))

g.add((SCHEMA.aggregateRating, RDF.type, OWL.ObjectProperty))
g.add((SCHEMA.aggregateRating, RDFS.label, Literal("aggregate rating")))
g.add((SCHEMA.aggregateRating, RDFS.comment, Literal("link to the aggregate rating of a movie, including the average rating and the number of ratings on TMDb")))
g.add((SCHEMA.aggregateRating, RDFS.domain, SCHEMA.Movie))
g.add((SCHEMA.aggregateRating, RDFS.range, SCHEMA.AggregateRating))

g.add((SCHEMA.birthPlace, RDF.type, OWL.ObjectProperty))
g.add((SCHEMA.birthPlace, RDFS.label, Literal("birth place")))
g.add((SCHEMA.birthPlace, RDFS.comment, Literal("Link to the place where a person was born. Mostly just the country")))
g.add((SCHEMA.birthPlace, RDFS.domain, SCHEMA.Person))
g.add((SCHEMA.birthPlace, RDFS.range, SCHEMA.Place))

g.add((SCHEMA.genre, RDF.type, OWL.ObjectProperty))
g.add((SCHEMA.genre, RDFS.label, Literal("is genre")))
g.add((SCHEMA.genre, RDFS.comment, Literal("link to the genres of a movie, e.g. action, comedy, horror, etc.")))
g.add((SCHEMA.genre, RDFS.domain, SCHEMA.Movie))
g.add((SCHEMA.genre, RDFS.range, EX.Genre))


# datatype properties
g.add((EX.castOrder, RDF.type, OWL.DatatypeProperty))
g.add((EX.castOrder, RDFS.label, Literal("cast order")))
g.add((EX.castOrder, RDFS.comment, Literal("The order in which a cast member is listed in the credits of a movie. Only applies to actors. Gives information on the importance of the role (main role, supporting role, etc.)")))
g.add((EX.castOrder, RDFS.domain, EX.Participation))
g.add((EX.castOrder, RDFS.range, XSD.integer))

g.add((EX.playedCharacter, RDF.type, OWL.DatatypeProperty))
g.add((EX.playedCharacter, RDFS.label, Literal("played character")))
g.add((EX.playedCharacter, RDFS.comment, Literal("The character played by a person in a movie. Only applies to actors.")))
g.add((EX.playedCharacter, RDFS.domain, EX.Participation))
g.add((EX.playedCharacter, RDFS.range, XSD.string))

g.add((EX.popularity, RDF.type, OWL.DatatypeProperty))
g.add((EX.popularity, RDFS.label, Literal("popularity")))
g.add((EX.popularity, RDFS.comment, Literal("The popularity score of a movie on TMDb")))
g.add((EX.popularity, RDFS.domain, SCHEMA.Movie))
g.add((EX.popularity, RDFS.range, XSD.float))

g.add((SCHEMA.birthDate, RDF.type, OWL.DatatypeProperty))
g.add((SCHEMA.birthDate, RDFS.label, Literal("birth date")))
g.add((SCHEMA.birthDate, RDFS.comment, Literal("The birth date of a person")))
g.add((SCHEMA.birthDate, RDFS.domain, SCHEMA.Person))
g.add((SCHEMA.birthDate, RDFS.range, XSD.date))

g.add((SCHEMA.datePublished, RDF.type, OWL.DatatypeProperty))
g.add((SCHEMA.datePublished, RDFS.label, Literal("date published")))
g.add((SCHEMA.datePublished, RDFS.comment, Literal("The date when a movie was published")))
g.add((SCHEMA.datePublished, RDFS.domain, SCHEMA.Movie))
g.add((SCHEMA.datePublished, RDFS.range, XSD.date))

g.add((SCHEMA.deathDate, RDF.type, OWL.DatatypeProperty))
g.add((SCHEMA.deathDate, RDFS.label, Literal("death date")))
g.add((SCHEMA.deathDate, RDFS.comment, Literal("The death date of a person")))
g.add((SCHEMA.deathDate, RDFS.domain, SCHEMA.Person))
g.add((SCHEMA.deathDate, RDFS.range, XSD.date))

g.add((SCHEMA.duration, RDF.type, OWL.DatatypeProperty))
g.add((SCHEMA.duration, RDFS.label, Literal("duration")))
g.add((SCHEMA.duration, RDFS.comment, Literal("The duration of a movie in minutes")))
g.add((SCHEMA.duration, RDFS.domain, SCHEMA.Movie))
g.add((SCHEMA.duration, RDFS.range, XSD.integer))

g.add((SCHEMA.gender, RDF.type, OWL.DatatypeProperty))
g.add((SCHEMA.gender, RDFS.label, Literal("gender")))
g.add((SCHEMA.gender, RDFS.comment, Literal("The gender of a person written as a single letter ('u' for unknown, 'm' for male, 'f' for female, 'b' for non-binary)")))
g.add((SCHEMA.gender, RDFS.domain, SCHEMA.Person))
g.add((SCHEMA.gender, RDFS.range, XSD.string))

g.add((SCHEMA.identifier, RDF.type, OWL.DatatypeProperty))
g.add((SCHEMA.identifier, RDFS.label, Literal("identifier")))
g.add((SCHEMA.identifier, RDFS.comment, Literal("A unique identifier for a person, movie, genre, role, place, country, or aggregate rating")))

g.add((SCHEMA.inLanguage, RDF.type, OWL.DatatypeProperty))
g.add((SCHEMA.inLanguage, RDFS.label, Literal("in language")))
g.add((SCHEMA.inLanguage, RDFS.comment, Literal("The original language of a movie")))
g.add((SCHEMA.inLanguage, RDFS.domain, SCHEMA.Movie))
g.add((SCHEMA.inLanguage, RDFS.range, XSD.string))

g.add((SCHEMA.name, RDF.type, OWL.DatatypeProperty))
g.add((SCHEMA.name, RDFS.label, Literal("name")))
g.add((SCHEMA.name, RDFS.comment, Literal("The name of a person, movie, genre, role, place, country, or aggregate rating")))

g.add((SCHEMA.ratingCount, RDF.type, OWL.DatatypeProperty))
g.add((SCHEMA.ratingCount, RDFS.label, Literal("rating count")))
g.add((SCHEMA.ratingCount, RDFS.comment, Literal("The number of ratings a movie has received in the AggregateRating class")))
g.add((SCHEMA.ratingCount, RDFS.domain, SCHEMA.AggregateRating))
g.add((SCHEMA.ratingCount, RDFS.range, XSD.integer))

g.add((SCHEMA.ratingValue, RDF.type, OWL.DatatypeProperty))
g.add((SCHEMA.ratingValue, RDFS.label, Literal("rating value")))
g.add((SCHEMA.ratingValue, RDFS.comment, Literal("The average rating value of a movie in the AggregateRating class")))
g.add((SCHEMA.ratingValue, RDFS.domain, SCHEMA.AggregateRating))
g.add((SCHEMA.ratingValue, RDFS.range, XSD.float))

g.add((SCHEMA.roleName, RDF.type, OWL.DatatypeProperty))
g.add((SCHEMA.roleName, RDFS.label, Literal("role name")))
g.add((SCHEMA.roleName, RDFS.comment, Literal("The name of a role that a person can have in a movie, e.g. director, actor, producer, etc.")))
g.add((SCHEMA.roleName, RDFS.domain, SCHEMA.Role))
g.add((SCHEMA.roleName, RDFS.range, XSD.string))


schema_file = "data/ontology.ttl"
g.serialize(destination=schema_file, format="turtle")

print(f"Ontology written to {schema_file}")
print(f"Validated {len(g)} triples")
