import random
import spacy
from pathlib import Path
from spacy.training.example import Example
import json
import re

LABEL = "COL_NAME"

def trim_entity_spans(data: list) -> list:
    invalid_span_tokens = re.compile(r'\s')
    cleaned_data = []
    for text, annotations in data:
        entities = annotations['entities']
        valid_entities = []
        for start, end, label in entities:
            valid_start = start
            valid_end = end
            while valid_start < len(text) and invalid_span_tokens.match(text[valid_start]):
                valid_start += 1
            while valid_end > 1 and invalid_span_tokens.match(text[valid_end - 1]):
                valid_end -= 1
            valid_entities.append([valid_start, valid_end, label])
        cleaned_data.append((text, {'entities': valid_entities}))
    return cleaned_data

def convert_dataturks_to_spacy(filepath):
    training_data = []
    with open(filepath, 'r', encoding="utf8") as f:
        lines = f.readlines()
    for line in lines:
        data = json.loads(line)
        text = data['content']
        entities = []
        if data.get('annotation'):
            for annotation in data['annotation']:
                point = annotation['points'][0]
                labels = annotation['label']
                if not isinstance(labels, list):
                    labels = [labels]
                for label in labels:
                    entities.append((point['start'], point['end'] + 1, label))
        training_data.append((text, {"entities": entities}))
    return training_data

TRAIN_DATA = trim_entity_spans(convert_dataturks_to_spacy("traindata.json"))

def train_ner(model=None, output_dir="./resume_model", n_iter=30):
    if model:
        nlp = spacy.load(model)
        print(f"Loaded model '{model}'")
    else:
        nlp = spacy.blank("en")
        print("Created blank 'en' model")

    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    examples = []
    for text, annots in TRAIN_DATA:
        doc = nlp.make_doc(text)
        examples.append(Example.from_dict(doc, annots))

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.initialize()
        for i in range(n_iter):
            random.shuffle(examples)
            losses = {}
            for batch in spacy.util.minibatch(examples, size=8):
                nlp.update(batch, drop=0.2, losses=losses)
            print(f"Iteration {i+1} Losses: {losses}")

    test_text = "Marathwada Mitra Mandals College of Engineering"
    doc = nlp(test_text)
    print("Entities:", [(ent.text, ent.label_) for ent in doc.ents])

    output_dir = Path(output_dir)
    nlp.to_disk(output_dir)
    print(f"Model saved to {output_dir}")

if __name__ == "__main__":
    train_ner(model=None, output_dir="./resume_model", n_iter=30)
