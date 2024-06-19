#pip install spacy
#python -m spacy download en_core_web_sm

import spacy
nlp = spacy.load("en_core_web_sm")
text = "Pediatric Basic Life Support : 2010 American Heart Association Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care Marc D. Berg, Stephen M. Schexnayder, Leon Chameides, Mark Terry, Aaron Donoghue, Robert W. Hickey, Robert A. Berg, Robert M. Sutton and Mary Fran Hazinski"
doc = nlp(text)
for ent in doc.ents:
    if ent.label_ == "PERSON":
        print(ent.text, ent.start_char, ent.end_char)