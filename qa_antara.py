import sys
import spacy
import nltk
from nltk import word_tokenize
import operator

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

question_map = {"how tall": ['QUANTITY'], "who" : ['PERSON','ORGANIZATION'],"when" : ['DATE', 'TIME'],
                "where":['LOC', 'GPE'], "how much" : ['ORDINAL','PERCENT','MONEY'], "whose":['PERSON'],
                "how big": ['ORDINAL', 'QUANTITY']}
nlp = spacy.load('en_core_web_sm')
# question_map = {}

def input_file_contents():
    #    file = open(sys.argv[1], "r")
    input_file = open("input_file.txt", "r")
    file_contents = input_file.read()
    file_contents = file_contents.split('\n')
    #    print(file_contents)
    return file_contents

def get_questions_map(file_name):
    #    file = open(sys.argv[1], "r")
    input_file = open(file_name, "r")
    file_contents = input_file.read()
    file_contents = file_contents.split('\n')
    for index in range(len(file_contents)):
        line = file_contents[index].split(' ')
        if line[0] == "Type:":
            question_type = line[1]
            if len(line) > 2:
                types = line[3].split(',')
                expected_answer_type = file_contents[index + 1].split(',')
                for type in types:
                    question = question_type + ' ' + type
                    question_map[question] = expected_answer_type
            else:
                expected_answer_type = file_contents[index+1].split(',')
                question_map[question_type] = expected_answer_type


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
        # print(sentence.text)

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
    expected_answer_type = {}
    # fetch the kind of answer the question is expecting before dropping the stop words and maintain a dictionary of those
    # check if question map data is present in the question
    for question_key, expected_value in question_map.items():
        lower_case_question = question.lower()
        if question_key in lower_case_question:
            expected_answer_type[question_key] = expected_value

    subject = None
    indirect_object = None
    direct_object = None
    rootverb = None

    for word in question_sentence:
        if word.dep_ == "nsubj":
            subject = word.orth_
        #iobj for indirect object
        if word.dep_ == "iobj":
            indirect_object = word.orth_
        #dobj for direct object
        if word.dep_ == "dobj":
            direct_object = word.orth_
        if word.dep_ == "ROOT":
            rootverb = word.lemma_
        if word.text != '?' and (word.is_stop == False):
            # or (word.is_stop == True and word.pos_ == "VERB"):
            word_obj = Word(word.text)
            # Add pos tagging
            word_obj.pos = word.pos_
            # Add lemmatization
            word_obj.lemma = word.lemma_

            question_arr.append(word_obj)
    return subject, direct_object, indirect_object, rootverb, question_arr, expected_answer_type



def matchOrSimilarity(array, word):
    for wordobject in array:
        if wordobject == word.lemma:
            # print("Match")
            return True
            break
        # Word similarity
        # word1 = nlp(wordobject)
        # word2 = nlp(word.lemma)
        #  Similarity measure
        # if word1.similarity(word2) > 0.5 and wordobject.lemma == 'run':
        #     print("Similar: ", word1.similarity(word2))
        #     print(word1.text)
        #     print(word2.text)

def checkNer(question, nerlist, expected_answer_type):
    matches = []
    # print(nerlist)
    # print(question)

    # check if ner list and expected_answer_type have anything in common
    for question_key, expected_answer_list in expected_answer_type.items():
        for answer_type in expected_answer_list:
            for ner in nerlist:
                if ner == answer_type:
                    matches.append(ner)

    # for key, valueslist in question_map.items():
    #     # print("-------Key : ",key)
    #     if key in question:
    #         for value in valueslist:
    #             if value in nerlist:
    #                 matches.append(value)
    return matches if (len(matches) > 0) else 0

def assignScore(matches, overlapCount, verbMatchCnt):
    score = 0
    if matches!=0:
        score += len(matches)*6
    print("NER Match Score:", matches)
    print("Overlap Count: ", overlapCount)
    print("Verb Match Count: ", verbMatchCnt)
    score += overlapCount*3
    score += verbMatchCnt*6
    return score

def whereqs(overlapCount, matches, sentence_details_array):
    locationpreps = ["in", "at", "near", "inside"]
    score = 0
    score += overlapCount*3
    # print("Overlap score:", overlapCount)
    for word in sentence_details_array[0].sentence[1]:
        if word.lemma in locationpreps:
            # print(word.lemma)
            score+=6
    # print("Location prep count:", (score - (overlapCount*3))/6)        
    if matches!=0:
        score += 6                
    # print("NER Match: ", matches)
    return score


def overlap(question, sentence_details_array, expected_answer_type, rootverb):
    question_lem_arr = []
    answer_list = ""
    for word in question:
        if word.pos != "PUNCT":
            question_lem_arr.append(word.lemma)
    #result_arr = []
    # for sentence, taglist in sentence_dict.items():
    #     d = {}
    #     d["sentence"] = [sentence, taglist]
    #     d["count"] = 0
    #     result_arr.append(d)
        # for k, v in d.items():
        #     print(k,v)
    # print(question)
    verbMatchCnt = 0
    where_ans = {}
    for record in sentence_details_array:
        record.count = 0
        for word in record.sentence[1]:
            if matchOrSimilarity(question_lem_arr, word):
                record.count += 1
                # print("Matched word", word.lemma)
            if word.lemma == rootverb:
                verbMatchCnt +=1
        nerlist = []
        for each in record.ners:
            nerlist.append(each.label_)
        matches = checkNer(question_lem_arr, nerlist, expected_answer_type)
        if "where" in question_lem_arr:
            # print("Ans: ",record.sentence[0])  
            score = whereqs(record.count, matches, sentence_details_array)
            if where_ans.get(score):
                where_ans[score].append(record.sentence[0])
            else:
                where_ans[score] = [record.sentence[0]]
            
        # print("Ans: ",record.sentence[0])
        # print(assignScore(matches, record.count, verbMatchCnt))
        # if (matches !=0 and record.count > 0) or (matches == 0 and record.count > 6):
        #     answer_list.append(record.sentence[0])            
    if "where" in question_lem_arr and where_ans.items != []:
        # print(sorted(where_ans.items(), reverse = True)[0][1])
        answer_list = "".join(sorted(where_ans.items(), reverse = True)[0][1][0])
        # print(sorted(where_ans.items(), reverse = True)[:2])
    return answer_list


def find_answer(qid, question, sentence_details_array, question_dict):
    # print(qid)
    # print(question)
    question = question.split(":")
    question = question[1].strip()
    # print(question)
    subject, dobject, idobject, rootverb, question_arr, expected_answer_type = extractpos(question)
    # print("Subject:", subject)
    # print("Direct Object:", dobject)
    # print("Indirect Object:", idobject)
    # print("Root:", rootverb)
    answer_list = overlap(question_arr, sentence_details_array, expected_answer_type, rootverb)
    if answer_list != "":
        question_dict[qid] = answer_list
    else:
        question_dict[qid] = "No answer found"
    # for record in answer_list:
    #     print(record["sentence"][0])
    #     print(record["count"])
    # print("***********************************")
    # for token in question_arr:
    #     print(token.word_name, token.lemma, token.pos)
    #     print(" ")
    header = "Answer: "
    answer = ""
    return "\n" + header + answer


def process_question(question_data, output_stream, sentence_details_array, question_dict):
    newline = "\n"
    question_id = "QuestionID"
    question = "Question:"
    question_data = question_data.split(newline)
    qid = None
    for each in question_data:
        if question_id in each:
            qid = each.split(": ")[1]
            output_stream.write(each)
        if question in each:
            answer = find_answer(qid, each, sentence_details_array, question_dict)
            output_stream.write(answer)
            output_stream.write(newline + newline)

def populate_answer_dict(answers_data, answer_dict):
    newline = "\n"
    question_id = "QuestionID"
    answer = "Answer:"
    answers_data = answers_data.split(newline)
    for entry in answers_data:
        if question_id in entry:
            qid = entry.split(": ")[1]
        if answer in entry:
            ans = entry.split(": ")[1]
            answer_dict[qid] = ans

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
        question_dict = {}
        filename_path_questions = filename_path + ".questions"
        question_data = open(filename_path_questions, "r").read()
        process_question(question_data, output_stream, sentence_details_array, question_dict)
    
        # ------ ANSWERS ------
        answer_dict = {}
        filename_path_answers = filename_path + ".answers"
        answers_data = open(filename_path_answers, "r").read()
        populate_answer_dict(answers_data, answer_dict)
        accuracy_count = 0
        for question, answer_list in question_dict.items():
            print("***********************************")
            print(question)
            print("Actual answer:", answer_dict.get(question))
            print("Answer Found:", answer_list)
            # for answer in answer_list:
            #     if answer_dict.get(question) in answer:
            #         accuracy_count +=1
            #     print("Ans:  ",answer)
        # print("**********************************************************************")
        # print("Accuracy:", accuracy_count)
        # print("**********************************************************************")
        
            
def main():
    input_file_data = input_file_contents()
    output_stream = open("output.txt", "w")
    # get_questions_map("question_types.txt")
    fetch_file_data_and_process(input_file_data, output_stream)
    output_stream.close()


if __name__ == "__main__": main()
