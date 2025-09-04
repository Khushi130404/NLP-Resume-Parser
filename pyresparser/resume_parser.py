import os
import multiprocessing as mp
import io
from . import constants as cs
import spacy
import pprint
from spacy.matcher import Matcher
from . import utils


class ResumeParser(object):

    def __init__(
        self,
        resume,
        skills_file=None,
        custom_regex=None
    ):
        nlp = spacy.load('en_core_web_sm')
        custom_nlp = spacy.load("en_core_web_sm")
        self.__skills_file = skills_file
        self.__custom_regex = custom_regex
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'skills': None,
            'experience': None,
            'projects': None,
            "education": None,
            "leadership":None,
            'achievements':None
        }
        self.__resume = resume
        if not isinstance(self.__resume, io.BytesIO):
            ext = os.path.splitext(self.__resume)[1].split('.')[1]
        else:
            ext = self.__resume.name.split('.')[1]
        self.__text_raw = utils.extract_text(self.__resume, '.' + ext)
        self.__text = ' '.join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)
        self.__custom_nlp = custom_nlp(self.__text_raw)
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details


    def __get_basic_details(self):
        """
        Extract all basic details from the parsed resume text.
        Populates self.__details with structured data.
        """

        # Extract entities using custom NLP model
        cust_ent = utils.extract_entities_wih_custom_model(self.__custom_nlp)

        # Extract name (fallback to standard method if custom entity fails)
        name = utils.extract_name(self.__nlp, matcher=self.__matcher)

        # Extract email and mobile
        email = utils.extract_email(self.__text)
        mobile = utils.extract_mobile_number(self.__text, self.__custom_regex)

        # Extract skills
        skills = utils.extract_skills(
            self.__nlp,
            self.__noun_chunks,
            self.__skills_file
        )

        # Extract entity sections (education, projects, achievements, etc.)
        entities = utils.extract_entity_sections_grad(self.__text_raw)

        # Fill structured details using keyword-based matching
        self.__details['name'] = cust_ent.get('Name', [name])[0] if cust_ent.get('Name') else name
        self.__details['email'] = email
        self.__details['mobile_number'] = mobile
        self.__details['skills'] = skills

        self.__details['education'] = utils.safe_parse_by_keywords(
            entities, cs.EDUCATION_KEYWORDS, utils.extract_education
        )

        self.__details['projects'] = utils.extract_project_section(self.__text_raw)

        # print("**************************************************************************************")

        self.__details['leadership'] = utils.safe_parse_by_keywords(
            entities, cs.POSITIONS_KEYWORDS, utils.extract_responsibilities
        )

        print("--------------------------------------------------------------------------------")

        self.__details['achievements'] = utils.safe_parse_by_keywords(
            entities, cs.ACHIEVEMENTS_KEYWORDS, utils.extract_achievements
        )

        self.__details['experience'] = utils.safe_parse_by_keywords(
            entities, cs.EXPERIENCE_KEYWORDS, utils.extract_experience
        )

        # Links (convert links into username mapping)
        links = utils.extract_links_from_pdf(self.__resume)
        self.__details['links'] = utils.extract_usernames(links) if links else {}

        # Total pages
        self.__details['no_of_pages'] = utils.get_number_of_pages(self.__resume)

        return


def resume_result_wrapper(resume):
    parser = ResumeParser(resume)
    return parser.get_extracted_data()


if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())

    resumes = []
    data = []
    for root, directories, filenames in os.walk('resumes/'):
        for filename in filenames:
            file = os.path.join(root, filename)
            resumes.append(file)

    results = [
        pool.apply_async(
            resume_result_wrapper,
            args=(x,)
        ) for x in resumes
    ]

    results = [p.get() for p in results]

    # pprint.pprint(results)
