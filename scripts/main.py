# Linkee Main script
import pandas as pd
from question_gen import generate_card
from os.path import exists
practice_list = ['Tom Hanks', 'Harry Potter', 'California', 'Willem Dafoe', 'Allstate', 'Las Vegas', 'Emerdale']
additional_list = ['iphone', 'Arsenal', 'Belfast', 'Easter', 'Christmas', 'Cadbury', 'Green Goblin']
# make this a command line entry instead and to load from existing df, make a copy and add to
def add_card(input_list):

    # a list of names that want to generate card for
    #Check with some saved db is aleady there
    # easiest is prob read df, check if exists and then add if doesn't
    # df = pd.DataFrame(columns=('Final Answer', 'Answers', 'Questions'))

    file_exists = exists("Linkee_records.csv")
    if file_exists:
        df = pd.read_csv("Linkee_records.csv")
    else:
        df = pd.DataFrame(columns=('Final Answer', 'Answers', 'Questions'))

    for final_answer in input_list:
        #should check if already in table before searching for it.
        l = len(df)
        answers, questions = generate_card(final_answer)
        df.loc[l] = [final_answer, answers, questions]
    df.to_csv("Linkee_records.csv", index=False)
    print("file saved")

    # print(answers, questions)
    # Add to df
    return  # no output

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # answers, questions = generate_card("Tom Hanks")
    # print(answers, questions)
    add_card(additional_list)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
