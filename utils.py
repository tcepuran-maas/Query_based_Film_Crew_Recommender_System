from itertools import combinations
import pandas as pd


def _job_mask(df, job):
    """Boolean mask for a role.
    Actor -> cast_or_crew == 'cast'
    Otherwise -> job == <Role>
    """
    if job == "Actor":
        return df["cast_or_crew"] == "cast"
    return df["job"] == job


def _jobs_mask(df, jobs):
    """Boolean mask: matches any role from jobs."""
    mask = pd.Series(False, index=df.index)
    for job in jobs:
        mask = mask | _job_mask(df, job)
    return mask


def _rows_for_job(df, job, actor_cast_max=None):
    """Rows for a role; optionally limit Actor by cast_id."""
    rows = df[_job_mask(df, job)].copy()

    if job == "Actor" and actor_cast_max is not None and "cast_id" in rows.columns:
        rows = rows[rows["cast_id"].fillna(10**9) < actor_cast_max]

    return rows


def _limit_candidates(candidate_ids, anchor_rows, person_col, max_candidates):
    """Limits candidates to the most frequent persons in anchor movies."""
    if max_candidates is None or len(candidate_ids) <= max_candidates:
        return candidate_ids

    ranked_ids = (
        anchor_rows[anchor_rows[person_col].isin(candidate_ids)]
        .groupby(person_col)["movie_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(max_candidates)
        .index
        .tolist()
    )
    return ranked_ids


def queryPrefiltering(
    df,
    movies_df,
    req_person_names,
    req_job_titles,
    needed_jobs,
    genres=None,
    actor_cast_max=None,
    max_candidates_per_job=None,
):
    """
    Builds a small, query-oriented subgraph:
      1) Anchor movies (req_person + req_job)
      2) Candidates per needed_job from anchor movies
      3) Cross movies via pairwise intersections
      4) Minimal crew subset
    """

    # Step 1: Anchor movies
    anchor_film_ids = df[
        _jobs_mask(df, req_job_titles) & df["name"].isin(req_person_names)
    ]["movie_id"].unique().tolist()

    if genres:
        pattern = "|".join(genres)
        anchor_film_ids = movies_df[
            movies_df["id"].isin(anchor_film_ids)
            & movies_df["genres"].str.contains(pattern, na=False)
        ]["id"].tolist()

    print(f"Step 1 – Anchor movies: {len(anchor_film_ids)}")

    # Step 2: Candidates per role
    candidates_per_job = {}
    films_of_candidates_per_job = {}

    for job in needed_jobs:
        job_rows = _rows_for_job(df, job, actor_cast_max=actor_cast_max)
        anchor_job_rows = job_rows[job_rows["movie_id"].isin(anchor_film_ids)]

        cand_ids = anchor_job_rows["person_id"].dropna().unique().tolist()

        if isinstance(max_candidates_per_job, dict):
            limit = max_candidates_per_job.get(job)
        else:
            limit = max_candidates_per_job

        cand_ids = _limit_candidates(cand_ids, anchor_job_rows, "person_id", limit)
        candidates_per_job[job] = cand_ids

        films_of_candidates_per_job[job] = set(
            job_rows[job_rows["person_id"].isin(cand_ids)]["movie_id"]
            .dropna()
            .unique()
        )

        print(
            f"Step 2 – Candidates for '{job}': {len(cand_ids)} people, "
            f"{len(films_of_candidates_per_job[job])} movies total"
        )

    # Step 3: Cross-collaboration movies (pairwise intersections)
    cross_films = set()
    for job_a, job_b in combinations(list(needed_jobs), 2):
        pair_films = films_of_candidates_per_job[job_a] & films_of_candidates_per_job[job_b]
        print(f"Step 3 – Cross collaborations '{job_a}' ↔ '{job_b}': {len(pair_films)} movies")
        cross_films |= pair_films

    # Step 4: Minimal graph
    all_film_ids = set(anchor_film_ids) | cross_films

    anchor_crew = df[
        df["movie_id"].isin(anchor_film_ids)
        & _jobs_mask(df, req_job_titles)
        & df["name"].isin(req_person_names)
    ]

    candidate_parts = []
    for job in needed_jobs:
        job_rows = _rows_for_job(df, job, actor_cast_max=actor_cast_max)
        candidate_parts.append(
            job_rows[
                job_rows["movie_id"].isin(all_film_ids)
                & job_rows["person_id"].isin(candidates_per_job[job])
            ]
        )

    candidate_crew = (
        pd.concat(candidate_parts, ignore_index=False)
        if candidate_parts
        else pd.DataFrame(columns=df.columns)
    )

    result = pd.concat([anchor_crew, candidate_crew]).drop_duplicates()

    print(
        f"\nResult: {len(all_film_ids)} movies, {len(result)} crew entries "
        f"(before: {len(df)} entries)"
    )
    return result
