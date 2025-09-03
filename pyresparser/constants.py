from nltk.corpus import stopwords

# ---------------------- Basic Patterns ---------------------- #
NAME_PATTERN = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

NOT_ALPHA_NUMERIC = r'[^a-zA-Z\d]'
NUMBER = r'\d+'

MONTHS_SHORT = r'''(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)
                   |(aug)|(sep)|(oct)|(nov)|(dec)'''
MONTHS_LONG = r'''(january)|(february)|(march)|(april)|(may)|(june)|(july)|
                   (august)|(september)|(october)|(november)|(december)'''
MONTH = r'(' + MONTHS_SHORT + r'|' + MONTHS_LONG + r')'
YEAR = r'(((20|19)(\d{2})))'

STOPWORDS = set(stopwords.words('english'))


EDUCATION_KEYWORDS = [
    'education','diploma', 'degree',
    'courses', 'certifications'
]


PROJECTS_KEYWORDS = [
    "projects", "academic projects", "key projects", "capstone", 
    "personal projects", "major projects", "minor projects"
]


ACHIEVEMENTS_KEYWORDS = [
    "achievements", "awards", "honors", "honours", "recognition", 
    "certificates", "certifications", "scholarships", "accomplishments"
]

POSITIONS_KEYWORDS = [
    "positions", "position", "responsibility", "coordinator", "leadership", 
    "roles", "positions of responsibility", "por", "head", "president", 
    "secretary", "team lead", "organizer","training"
]

EXPERIENCE_KEYWORDS = [
    "experience","job","company","work"
]

USERNAME_KEYWORDS = [
    "github", "leetcode", "linkedin", "gfg", "geeksforgeeks", 
    "kaggle", "stackoverflow", "codeforces", "codechef", 
    "hackerrank", "medium", "twitter", "x.com", "instagram", 
    "facebook", "dev.to", "gitlab", "reddit", "behance", 
    "dribbble", "angel.co"
]

# ---------------------- Resume Section Keywords ---------------------- #
RESUME_SECTIONS_PROFESSIONAL = [
    'experience', 'education', 'interests', 'professional experience',
    'publications', 'skills', 'certifications', 'objective',
    'career objective', 'summary', 'leadership', 'projects'
]

RESUME_SECTIONS_GRAD = [
    # Achievements / Awards
    'accomplishments', 'achievements', 'awards', 'honors', 'honours',
    'recognition', 'certificates', 'certifications', 'scholarships',

    # Experience
    'experience', 'work experience', 'professional experience',
    'employment history', 'career history', 'internships', 'internship',

    # Education
    'education', 'academic background', 'academic qualifications',
    'qualifications', 'courses', 'studies',

    # Skills
    'skills', 'technical skills', 'key skills', 'soft skills',

    # Projects
    'projects', 'research projects', 'personal projects', 'academic projects',

    # Leadership & Responsibility
    'leadership', 'positions', 'responsibility', 'roles',
    'positions of responsibility', 'por', 'committee', 'head', 'organizer',

    # Summary & Objective
    'objective', 'career objective', 'summary', 'profile', 'professional summary',

    # Publications
    'publications', 'papers', 'research',

    # Interests
    'interests', 'hobbies', 'activities', 'extracurricular activities'
]
