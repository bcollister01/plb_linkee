# Linkee Main script

from question_gen import generate_card
def add_card(input_list):
    # a list of names that want to generate card for
    #Check with some saved db is aleady there
    # easiest is prob read df, check if exists and then add if doesn't

    answers, questions = generate_card('Tom Hanks')
    print(answers, questions)
    # Add to df
    return  # no output

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    answers, questions = generate_card("Tom Hanks")
    print(answers, questions)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
