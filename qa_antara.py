import sys
import spacy
import nltk
from nltk import word_tokenize


class Word:
    def __init__(self, name):
        self.word_name = name
        self.pos = ""
        self.lemma = ""

class SentenceDetails:
    def __init__(self):
        self.sentence = []
        self.count = ""
        self.ners = []


nlp = spacy.load('en_core_web_sm')


def input_file_contents():
    #    file = open(sys.argv[1], "r")
    input_file = open("input_file.txt", "r")
    file_contents = input_file.read()
    file_contents = file_contents.split('\n')
    #    print(file_contents)
    return file_contents

def populate_dictionary(sentence_text, each_sentence_array, ner_for_sentence):
    details = SentenceDetails()
    details.sentence = [sentence_text, each_sentence_array]
    details.ners = ner_for_sentence
    details.count = 0
    return details


def get_story_data(story_data):
    story = story_data.split('\n\n')
    story = story[2:]
    story = ' '.join(story)
    story = story.replace('\n', ' ')
    story = story.replace('.\"', ". \"")

    # use spacy to get sentence segmentation
    sentence_details = {}
    story_array = []
    result_array = []
    tokenized_sent_text = nltk.sent_tokenize(story)
    for each_sentence in tokenized_sent_text:
        #dictionary = {}
        sentence = nlp(each_sentence)
        each_sentence_array = []
        ner_for_sentence = sentence.ents

        # Print each sentence of the paragraph
        print(sentence.text)
        for word in sentence:
            word_obj = Word(word.text)
            # Add pos tagging
            word_obj.pos = word.pos_
            # Add lemmatization
            word_obj.lemma = word.lemma_
            each_sentence_array.append(word_obj)

        #dictionary[sentence.text] = each_sentence_array
        sentence_details = populate_dictionary(sentence.text, each_sentence_array, ner_for_sentence)
        result_array.append(sentence_details)
        story_array.append(each_sentence_array)

    return story_array, result_array


def extractpos(question):
    question_arr = []
    question_sentence = nlp(question)
    for word in question_sentence:
        if word.text != '?' and (word.is_stop == False):
            # or (word.is_stop == True and word.pos_ == "VERB"):
            word_obj = Word(word.text)
            # Add pos tagging
            word_obj.pos = word.pos_
            # Add lemmatization
            word_obj.lemma = word.lemma_
            question_arr.append(word_obj)
    return question_arr


def matchOrSimilarity(array, word):
    for wordobject in array:
        if wordobject.lemma == word.lemma:
            print("Match")
            return True
            break
        word1 = nlp(wordobject.lemma)
        word2 = nlp(word.lemma)
        if word1.similarity(word2) > 0.5 and wordobject.lemma == 'run':
            print("Similar: ", word1.similarity(word2))
            print(word1.text)
            print(word2.text)


def overlap(question, sentence_details_array):
    question_lem_arr = []
    for word in question:
        if word.pos != "PUNCT":
            question_lem_arr.append(word)
    #result_arr = []
    # for sentence, taglist in sentence_dict.items():
    #     d = {}
    #     d["sentence"] = [sentence, taglist]
    #     d["count"] = 0
    #     result_arr.append(d)
        # for k, v in d.items():
        #     print(k,v)
    print(question)
    for record in sentence_details_array:
        #for key, value in record.items():
            #if key != "count":
                print(record.sentence[0])
                for word in record.sentence[1]:
                    # if word.lemma in question_lem_arr:
                    if matchOrSimilarity(question_lem_arr, word):
                        record.count += 1
                        print("Matched word", word.lemma)
    return sentence_details_array


def find_answer(question, sentence_details_array):
    print("***********************************")
    print(question)
    question = question.split(":")
    question = question[1].strip()
    question_arr = extractpos(question)
    count_sentence = overlap(question_arr, sentence_details_array)
    # for record in count_sentence:
    #     print(record["sentence"][0])
    #     print(record["count"])
    print("***********************************")
    # for token in question_arr:
    #     print(token.word_name, token.lemma, token.pos)
    #     print(" ")
    header = "Answer: "
    answer = ""
    return "\n" + header + answer


def process_question(question_data, output_stream, sentence_details_array):
    newline = "\n"
    question_id = "QuestionID"
    question = "Question:"
    question_data = question_data.split(newline)
    for each in question_data:
        if question_id in each:
            output_stream.write(each)
        if question in each:
            answer = find_answer(each, sentence_details_array)
            output_stream.write(answer)
            output_stream.write(newline + newline)


def fetch_file_data_and_process(input_file_data, output_stream):
    directory_path = input_file_data[0]
    for i in range(1, len(input_file_data)):
        # process each set of story and questions at once.
        filename_path = directory_path + input_file_data[i]

        # ------ STORY ------
        # get story from each file
        filename_path_story = filename_path + ".story"
        story_data = open(filename_path_story, "r").read()
        story, sentence_details_array = get_story_data(story_data)

        # ------ QUESTIONS ------
        filename_path_questions = filename_path + ".questions"
        question_data = open(filename_path_questions, "r").read()
        process_question(question_data, output_stream, sentence_details_array)

        # ------ ANSWERS ------
        filename_path_answers = filename_path + ".answers"
        answers_data = open(filename_path_answers, "r").read()


def main():
    input_file_data = input_file_contents()
    output_stream = open("output.txt", "w")
    fetch_file_data_and_process(input_file_data, output_stream)
    output_stream.close()


if __name__ == "__main__": main()
