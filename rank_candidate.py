import pandas as pd
import spacy
from multiprocessing import Pool
from pyresparser.utils import extract_skills

def get_candidate_score(job_skill_count, job_skills, candidate_skills):
    common = job_skills & candidate_skills
    return len(common) / job_skill_count * 100

def sort_candidates(job_desc, candidates_df):
    nlp = spacy.load("en_core_web_sm")
    job_skills = {s.lower() for s in extract_skills(nlp(job_desc), nlp(job_desc).noun_chunks)}
    job_skill_count = len(job_skills)

    candidate_skills = [
        {s.strip().lower() for s in skills.split(",")}
        for skills in candidates_df["Skills"]
    ]
    data = [(job_skill_count, job_skills, skills) for skills in candidate_skills]

    with Pool() as pool:
        candidates_df["Score"] = pool.starmap(get_candidate_score, data)

    return candidates_df.sort_values(by="Score", ascending=False)

# Example usage
df = pd.read_csv("resumes.csv", usecols=["Email", "Skills"])
with open("sample_job_description.txt") as f:
    jd = f.read()

ranked_df = sort_candidates(jd, df)
ranked_df.to_csv("ranked.csv", index=False)
