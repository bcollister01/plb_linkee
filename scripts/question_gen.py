import pandas as pd
from ecommercetools import seo
import spacy
import textacy
import re
import nltk

from clean_text import CleanUpText
from keyword_find import find_text, answer_keyword_compare, linkee_keywords
from knowledge_graph import KnowledgeGraph
nlp = spacy.load("en_core_web_sm")
Clean_text = CleanUpText()
Knowledge_graph = KnowledgeGraph()


def fill_in_blank_q_generate(final_input, input_text, facts=1):
    # Might break if only 1 fact possible and not 2 - needs fixed
    """
    Generate a fill in the blank style question using 1 or 2
    facts about the input.

    Parameters
    ----------

    final_input (string): original input (final answer) for card
    input (string): answer/keyword which we want to generate question for
    facts (integer 1/2): allows to keep 1 or 2 facts for each answer

    Returns
    -------
    question ("string"): the fill in the blank question
    num_statements (integer): the number of statements found corresponding to the
                            input
    """
    final_input = Clean_text.tidy_input(final_input)

    if (facts < 1) or (facts > 2):
        return ("Invalid entry. Please specify if you want 1 or 2 facts.")
    page_name = input_text

    # Get Wikipedia page and text
    # using knowledge graph method
    text, key_url = find_text(page_name, keep_words=100000, cleanup=False, multi_links=False)
    # print(page_name)
    # text = (wikipedia.page(page_name,auto_suggest=False)).content
    text = re.sub(r'==.*?==+', '', text)
    # text = text.replace('\n', '')
    text = text.replace('\n', ' ')
    text = re.sub("\s\s+", " ", text)

    # Get category of input to better search for entity
    category = Knowledge_graph.classify_input(Knowledge_graph.get_knowledge_graph_df(input_text))
    # If person, just look for surname when trying to find facts
    if category == "Person":
        page_entity = input_text.split()[-1]
    else:
        page_entity = input_text
    # Above is fine

    doc = nlp(text)
    # Set up empty array to hold facts
    uniqueStatements = []
    # cue: Verb lemma with which ``entity`` is associated (e.g. "be", "have", "say").
    # Potentially use pronouns for the entity as well and combine results
    for cue in ["be", "have", "say", "do", "win", "write", "talk", "talk about", "born", "receive", "make", "continue",
                "find"]:
        statements = textacy.extract.semistructured_statements(doclike=doc, entity=page_entity, cue=cue)
        for statement in statements:
            entity, verb, fact = statement
            factlist = [str(word) for word in fact]
            fact = Clean_text.cleanup_fact(str(fact))

            # Removing statements where target word/phrase appears in fact
            # if re.search(page_name, fact):
            #   continue

            # if len(answer_keyword_compare(factlist, page_name)) != \
            #    len(factlist):
            #    print(f'removed: {factlist} due to page_name {page_name} ')
            # if fact has answer word in it ignore
            #  continue
            if len(answer_keyword_compare(factlist, final_input)) != len(factlist):
                # if fact has final answer in it ignore
                print(f'removed: {factlist} due to final_input {final_input} ')
                continue
            # Remove statements that are too long - more than 35 words long
            if len(fact.split()) > 35:
                continue
            elif len(fact.split()) < 5:
                continue
            # statement = f"{page_name} {verb} {fact}"
            statement = f"{verb} {fact}"
            # More cleanup on fact
            statement = re.sub(r"[\[\]\•\▽\❖\†]+", '', statement)
            statement = statement.replace(', ', ' ')
            statement = statement.replace(' , ', ', ')
            statement = statement.replace(' ( ', ' (')
            statement = statement.replace(' )', ')')
            statement = statement.replace(" 's", "'s")
            statement = statement.replace(" - ", "-")
            statement = statement.replace("\'s", "'s")
            statement = statement.replace(page_name, '______')
            statement = f"{page_name} {statement}"

            uniqueStatements.append(statement)
    num_statements = len(uniqueStatements)

    # If it can't find any facts, should we try splitting up the input in
    # a different manner - at moment, just telling us this is happening
    if len(uniqueStatements) == 0:
        return ("No facts found for input.", num_statements)

    # Ensure code doesn't break if 2 facts are asked for but not available
    if len(uniqueStatements) == 1 and facts == 2:
        print('Only one fact available for answer.')
        facts = 1

    # Good tags for finding facts are numbers, proper nouns,
    # foreign words and comparative/superlative adjectives/adverbs
    good_tags = ['CD', 'FW', 'JJR', 'JJS', 'NNP', 'NNPS', 'RBR', 'RBRS']
    tag_count = []
    for i in range(len(uniqueStatements)):
        tag_tuples = nltk.pos_tag(uniqueStatements[i].split())
        tags = [x[1] for x in tag_tuples]
        # Adding a small weight for statement length to prioritise longer facts
        # which should have more info
        tag_count.append(sum(x in good_tags for x in tags) + 0.3 * len(tags))

    # Returning a sorted DataFrame of all the questions to be able to view
    df = pd.DataFrame(list(zip(uniqueStatements, tag_count)),
                      columns=['Statement', 'Count'])
    df = df.sort_values(by='Count', ascending=False)
    #     return(df)

    # Get sorted array of indexes containing facts in ascending order of good tags
    # In case of a tie, this arrays puts the lower numbered index first
    sorted_count = sorted(range(len(tag_count)), key=lambda k: tag_count[k])

    # Use 2 facts with most good tags in them

    fact1 = uniqueStatements[sorted_count[-1]]
    if facts == 2:
        fact2 = uniqueStatements[sorted_count[-2]]

    # Calculate how many letters are in the answer we are blanking
    page_name_words = page_name
    words = page_name_words.split()
    letters_per_word = [len(w) for w in words]

    fact1 = fact1.replace(page_name, '______ ' + str(letters_per_word))
    if category == "Person" and facts == 2:
        fact2 = fact2.replace(page_name, 'This person')
    elif category != "Person" and facts == 2:
        fact2 = fact2.replace(page_name, 'It')

    if facts == 1:
        question = str('Fill in the blank: ') + fact1 + str('.')
    elif facts == 2:
        question = str('Fill in the blank: ') + fact1 + str('. ') + fact2 + str('.')

    return (question, num_statements)


def generate_card(final_input):
    """Takes input and generates 4 question answer pairs"""
    keywords = linkee_keywords(final_input)
    answers = []  # Empty list to add answers we have questions for
    questions = []
    for answer in keywords:
        try:
            question, num_statements = fill_in_blank_q_generate(final_input, answer, facts=2)
        # except PageError:
        except:
            print(answer + ' does not have a Wikipedia page')
            continue

        if question == 'No facts found for input.':
            # print(answer + ' does not have facts')
            continue
        else:
            # print(answer + ' does have facts')
            answers.append(answer)
            questions.append(question)

    for i in range(len(answers)):
        questions = [re.sub(answers[i], f"[keyword {i + 1}]", qus) for qus in questions]
    # print(answers, "; ", questions)
    return (answers, questions)