from email.mime import text
import io
import os
import re
import nltk
import fitz
import re
import pandas as pd
import docx2txt
from datetime import datetime
from dateutil import relativedelta
from . import constants as cs
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from typing import List, Dict


def extract_text_from_pdf(pdf_path):
    
    if not isinstance(pdf_path, io.BytesIO):
        with open(pdf_path, 'rb') as fh:
            try:
                for page in PDFPage.get_pages(
                        fh,
                        caching=True,
                        check_extractable=True
                ):
                    resource_manager = PDFResourceManager()
                    fake_file_handle = io.StringIO()
                    converter = TextConverter(
                        resource_manager,
                        fake_file_handle,
                        codec='utf-8',
                        laparams=LAParams()
                    )
                    page_interpreter = PDFPageInterpreter(
                        resource_manager,
                        converter
                    )
                    page_interpreter.process_page(page)

                    text = fake_file_handle.getvalue()
                    yield text

                    converter.close()
                    fake_file_handle.close()
            except PDFSyntaxError:
                return
    else:
        try:
            for page in PDFPage.get_pages(
                    pdf_path,
                    caching=True,
                    check_extractable=True
            ):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(
                    resource_manager,
                    fake_file_handle,
                    codec='utf-8',
                    laparams=LAParams()
                )
                page_interpreter = PDFPageInterpreter(
                    resource_manager,
                    converter
                )
                page_interpreter.process_page(page)

                text = fake_file_handle.getvalue()
                yield text

                converter.close()
                fake_file_handle.close()
        except PDFSyntaxError:
            return


def get_number_of_pages(file_name):
    try:
        if isinstance(file_name, io.BytesIO):
            count = 0
            for page in PDFPage.get_pages(
                        file_name,
                        caching=True,
                        check_extractable=True
            ):
                count += 1
            return count
        else:
            if file_name.endswith('.pdf'):
                count = 0
                with open(file_name, 'rb') as fh:
                    for page in PDFPage.get_pages(
                            fh,
                            caching=True,
                            check_extractable=True
                    ):
                        count += 1
                return count
            else:
                return None
    except PDFSyntaxError:
        return None


def extract_text_from_docx(doc_path):
    try:
        temp = docx2txt.process(doc_path)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        return ' '.join(text)
    except KeyError:
        return ' '


def extract_text_from_doc(doc_path):
    try:
        try:
            import textract
        except ImportError:
            return ' '
        text = textract.process(doc_path).decode('utf-8')
        return text
    except KeyError:
        return ' '


def extract_text(file_path, extension):
    text = ''
    if extension == '.pdf':
        for page in extract_text_from_pdf(file_path):
            text += ' ' + page
    elif extension == '.docx':
        text = extract_text_from_docx(file_path)
    elif extension == '.doc':
        text = extract_text_from_doc(file_path)
    return text


def extract_entity_sections_grad(text):   
    text_split = [i.strip() for i in text.split('\n')]
    entities = {}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) & set(cs.RESUME_SECTIONS_GRAD)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in cs.RESUME_SECTIONS_GRAD:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
            entities[key].append(phrase)

    # entity_key = False
    # for entity in entities.keys():
    #     sub_entities = {}
    #     for entry in entities[entity]:
    #         if u'\u2022' not in entry:
    #             sub_entities[entry] = []
    #             entity_key = entry
    #         elif entity_key:
    #             sub_entities[entity_key].append(entry)
    #     entities[entity] = sub_entities

    # make entities that are not found None
    # for entity in cs.RESUME_SECTIONS:
    #     if entity not in entities.keys():
    #         entities[entity] = None

    # print(entities)
    return entities


def extract_entities_wih_custom_model(custom_nlp_text):
    
    entities = {}
    for ent in custom_nlp_text.ents:
        if ent.label_ not in entities.keys():
            entities[ent.label_] = [ent.text]
        else:
            entities[ent.label_].append(ent.text)
    for key in entities.keys():
        entities[key] = list(set(entities[key]))
    return entities


def get_total_experience(experience_list):
   
    exp_ = []
    for line in experience_list:
        experience = re.search(
            r'(?P<fmonth>\w+.\d+)\s*(\D|to)\s*(?P<smonth>\w+.\d+|present)',
            line,
            re.I
        )
        if experience:
            exp_.append(experience.groups())
    total_exp = sum(
        [get_number_of_months_from_dates(i[0], i[2]) for i in exp_]
    )
    total_experience_in_months = total_exp
    return total_experience_in_months


def get_number_of_months_from_dates(date1, date2):
   
    if date2.lower() == 'present':
        date2 = datetime.now().strftime('%b %Y')
    try:
        if len(date1.split()[0]) > 3:
            date1 = date1.split()
            date1 = date1[0][:3] + ' ' + date1[1]
        if len(date2.split()[0]) > 3:
            date2 = date2.split()
            date2 = date2[0][:3] + ' ' + date2[1]
    except IndexError:
        return 0
    try:
        date1 = datetime.strptime(str(date1), '%b %Y')
        date2 = datetime.strptime(str(date2), '%b %Y')
        months_of_experience = relativedelta.relativedelta(date2, date1)
        months_of_experience = (months_of_experience.years
                                * 12 + months_of_experience.months)
    except ValueError:
        return 0
    return months_of_experience


def extract_entity_sections_professional(text):
    
    text_split = [i.strip() for i in text.split('\n')]
    entities = {}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) \
                    & set(cs.RESUME_SECTIONS_PROFESSIONAL)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in cs.RESUME_SECTIONS_PROFESSIONAL:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
            entities[key].append(phrase)
    return entities


def extract_email(text):
    email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None


def extract_name(nlp_text, matcher):
    pattern = [cs.NAME_PATTERN]

    matcher.add('NAME', pattern)

    matches = matcher(nlp_text)

    for _, start, end in matches:
        span = nlp_text[start:end]
        if 'name' not in span.text.lower():
            return span.text


def extract_mobile_number(text, custom_regex=None):
    # mob_num_regex = r'''(?:(?:\+?([1-9]|[0-9][0-9]|
    #     [0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|
    #     [2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|
    #     [0-9]1[02-9]|[2-9][02-8]1|
    #     [2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|
    #     [2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{7})
    #     (?:\s*(?:#|x\.?|ext\.?|
    #     extension)\s*(\d+))?'''
    if not custom_regex:
        mob_num_regex = r'''(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)
                        [-\.\s]*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'''
        phone = re.findall(re.compile(mob_num_regex), text)
    else:
        phone = re.findall(re.compile(custom_regex), text)
    if phone:
        number = ''.join(phone[0])
        return number


def extract_skills(nlp_text, noun_chunks, skills_file=None):
   
    tokens = [token.text for token in nlp_text if not token.is_stop]
    if not skills_file:
        data = pd.read_csv(
            os.path.join(os.path.dirname(__file__), 'skills.csv')
        )
    else:
        data = pd.read_csv(skills_file)
    skills = list(data.columns.values)
    skillset = []
    # check for one-grams
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    # check for bi-grams and tri-grams
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]


def cleanup(token, lower=True):
    if lower:
        token = token.lower()
    return token.strip()


def extract_education(education_section):
    parsed_education = []
    current_entry = {}

    all_text = " ".join(education_section)
    bullet_counts = {k: all_text.count(k) for k in cs.SPLIT_KEYWORDS}
    bullet_counts = {k: v for k, v in bullet_counts.items() if v > 0}

    if bullet_counts:
        main_bullet = max(bullet_counts, key=bullet_counts.get)
    else:
        main_bullet = '•' 

    for item in education_section:
        clean_item = item.lstrip(main_bullet).strip()

        if any(char.isdigit() for char in clean_item) and any(sep in clean_item for sep in ['-', '–']):
            current_entry["years"] = clean_item

        elif item.strip().startswith(main_bullet):
            if current_entry:
                parsed_education.append(current_entry)
                current_entry = {}
            current_entry["institution"] = clean_item

        else:
            if "degree" in current_entry:
                current_entry["degree"] += " " + clean_item
            else:
                current_entry["degree"] = clean_item

    if current_entry:
        parsed_education.append(current_entry)

    return parsed_education


# import re

# COMPANY_HINTS = [
#     "Inc", "Ltd", "LLC", "Corp", "Company", "Technologies", "Solutions",
#     "Systems", "Pvt", "Limited", "Group", "Labs", "Global"
# ]
# KNOWN_COMPANIES = [
#     "Google", "Microsoft", "Apple", "Amazon", "Meta", "Facebook", "Netflix",
#     "Tesla", "Adobe", "IBM", "Intel", "Oracle", "Samsung", "NVIDIA", "Uber",
#     "Airbnb", "Stripe", "Paypal", "Mastercard", "Visa", "Accenture",
#     "Deloitte", "Infosys", "Wipro", "TCS", "Capgemini", "LinkedIn"
# ]

# SPLIT_KEYWORDS = ['•', '*', '●']  # Only strong section markers

# def is_company_line(line):
#     """Decide if a line looks like a company/title/date line."""
#     # If known company name
#     if any(re.search(rf"\b{c}\b", line, re.IGNORECASE) for c in KNOWN_COMPANIES):
#         return True
#     # Common company suffixes
#     if any(hint in line for hint in COMPANY_HINTS):
#         return True
#     # Short line with a year (date marker)
#     if len(line.split()) <= 8 and re.search(r"\d{4}", line):
#         return True
#     return False

# def extract_experience(text):
#     if isinstance(text, list):
#         text = "\n".join(text)

#     # Clean up multiple newlines and bullet separators
#     text = re.sub(r'\n+', '\n', text)  # Normalize newlines
#     sections = re.split(r'[' + re.escape(''.join(SPLIT_KEYWORDS)) + r']', text)

#     experiences = []
#     current_exp = None

#     for raw_line in sections:
#         line = raw_line.strip()
#         if not line:
#             continue

#         if is_company_line(line):
#             # Save previous entry
#             if current_exp:
#                 experiences.append(current_exp)
#             # Start new experience
#             current_exp = {"company": line, "title": "", "details": ""}
#         else:
#             # This is details text
#             if current_exp:
#                 if not current_exp["details"]:
#                     current_exp["details"] = line
#                 else:
#                     current_exp["details"] += " " + line

#     # Append last experience
#     if current_exp:
#         experiences.append(current_exp)

#     return experiences



def extract_experience(text):
    if isinstance(text, list):
        text = "\n".join(text)

    SPLIT_KEYWORDS = ['•', '*', '●']

    sections = re.split(r'[' + re.escape(''.join(SPLIT_KEYWORDS)) + r']', text)
    experiences = []

    for section in sections:
        lines = [line.strip() for line in section.strip().split("\n") if line.strip()]
        if not lines:
            continue

        company = ""
        title = ""
        details_lines = []

        for i, line in enumerate(lines):
            if any(re.search(rf"\b{c}\b", line, re.IGNORECASE) for c in cs.KNOWN_COMPANIES) \
                or any(suffix in line for suffix in ["Inc", "Ltd", "LLC", "Corp", "Pvt", "Limited", "Group", "Technologies"]):
                company = line
                remaining_lines = lines[i+1:]
                break
        else:
            remaining_lines = lines

        for i, line in enumerate(remaining_lines):
            if any(keyword.lower() in line.lower() for keyword in cs.JOB_TITLE_KEYWORDS):
                title = line
                details_lines = remaining_lines[i+1:]
                break
        else:
            details_lines = remaining_lines

        details_array = [line for line in details_lines if line]

        experiences.append({
            "company": company,
            "title": title,
            "details": details_array
        })

    return experiences




# def extract_experience(resume_lines):
#     print(resume_lines)

#     if isinstance(resume_lines, str):
#         lines = resume_lines.splitlines()
#     else:
#         lines = resume_lines

#     experience = []
#     current_item = None

#     date_pattern = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{4}\b|\b\d{4}\b', re.IGNORECASE)

#     for line in lines:
#         clean_line = line.strip()

#         if not clean_line or date_pattern.fullmatch(clean_line):
#             continue

#         if clean_line.startswith("•") or re.match(r"^\d+\.", clean_line):
#             if current_item:
#                 experience.append(current_item)
#             title = clean_line.lstrip("•").strip()
#             current_item = {"title": title, "details": []}

#         elif clean_line.startswith("–") or clean_line.startswith("-"):
#             if current_item:
#                 current_item["details"].append(clean_line.lstrip("–-").strip())

#         else:
#             if current_item:
#                 if not current_item["details"]:
#                     current_item["details"].append(clean_line)
#                 else:
#                     current_item["details"][-1] += " " + clean_line

#     if current_item:
#         experience.append(current_item)

#     return experience


def extract_achievements(resume_lines):
    
    print(resume_lines)

    if isinstance(resume_lines, str):
        lines = resume_lines.splitlines()
    else:
        lines = resume_lines

    achievements = []
    current_item = None

    date_pattern = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{4}\b|\b\d{4}\b', re.IGNORECASE)

    for line in lines:
        clean_line = line.strip()

        if not clean_line or date_pattern.fullmatch(clean_line):
            continue

        if clean_line.startswith("•") or re.match(r"^\d+\.", clean_line):
            if current_item:
                achievements.append(current_item)
            title = clean_line.lstrip("•").strip()
            current_item = {"title": title, "details": []}

        elif clean_line.startswith("–") or clean_line.startswith("-"):
            if current_item:
                current_item["details"].append(clean_line.lstrip("–-").strip())

        else:
            if current_item:
                if not current_item["details"]:
                    current_item["details"].append(clean_line)
                else:
                    current_item["details"][-1] += " " + clean_line

    if current_item:
        achievements.append(current_item)

    return achievements


def extract_responsibilities(resume_lines):
    print(resume_lines)

    if isinstance(resume_lines, str):
        lines = resume_lines.splitlines()
    else:
        lines = resume_lines

    responsibilities = []
    current_item = None

    date_pattern = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{4}\b|\b\d{4}\b', re.IGNORECASE)

    for line in lines:
        clean_line = line.strip()

        if not clean_line or date_pattern.fullmatch(clean_line):
            continue

        if clean_line.startswith("•") or re.match(r"^\d+\.", clean_line):
            if current_item:
                responsibilities.append(current_item)
            title = clean_line.lstrip("•").strip()
            current_item = {"title": title, "details": []}

        elif clean_line.startswith("–") or clean_line.startswith("-"):
            if current_item:
                current_item["details"].append(clean_line.lstrip("–-").strip())

        else:
            if current_item:
                if not current_item["details"]:
                    current_item["details"].append(clean_line)
                else:
                    current_item["details"][-1] += " " + clean_line

    if current_item:
        responsibilities.append(current_item)

    return responsibilities


def extract_links_from_pdf(path):
    doc = fitz.open(path)
    links = []
    seen_domains = set() 

    for page in doc:
        for link in page.get_links():
            if "uri" in link:
                url = link["uri"]

                domain = url.split("/")[2] if "//" in url else url

                if domain not in seen_domains:
                    links.append(url)
                    seen_domains.add(domain)

    return links


def extract_usernames(links):
    result = {}
    for link in links:
        if link.startswith("mailto:"):
            continue  
        for keyword in cs.USERNAME_KEYWORDS:
            if keyword in link:
                username = link.rstrip("/").split("/")[-1]
                platform = keyword.capitalize()
                result[platform] = username
                break
        else:
            result.setdefault("Other", []).append(link)
    return result

def extract_project_section(resume_text):
    if isinstance(resume_text, str):
        lines = resume_text.splitlines()
    else:
        lines = resume_text

    project_section = []
    in_project_section = False

    for line in lines:
        clean_line = line.strip()
        lower_line = clean_line.lower()

        if any(keyword in lower_line for keyword in cs.PROJECT_KEYWORDS):
            in_project_section = True
            continue

        if in_project_section and any(keyword in lower_line for keyword in cs.SECTION_KEYWORDS):
            break

        if in_project_section:
            if (clean_line 
                and not re.search(r'cgpa|percentile|rank|grade', lower_line)
                and not cs.DATE_PATTERN.fullmatch(clean_line)):
                project_section.append(clean_line)

    return project_section


def extract_projects(project_lines):
    projects = []
    current_project = None

    for line in project_lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        if clean_line.startswith("•"):
            if current_project:
                projects.append(current_project)
            current_project = {"project_name": clean_line.lstrip("•").strip(), "details": []}
        else:
            if current_project:
                current_project["details"].append(clean_line)

    if current_project:
        projects.append(current_project)

    return projects


def find_section_key_by_keywords(entities, keywords):
   
    for key in entities.keys():
        if any(k.lower() in key.lower() for k in keywords):
            return key
    return None

def safe_parse_by_keywords(entities, keywords, parser=None):
    
    key = find_section_key_by_keywords(entities, keywords)
    if key:
        data = entities.get(key, [])
        if parser and data:
            parsed = parser(data)
            return parsed if parsed else data
        return data if data else entities.get(key, "")
    return ""