import sys
import spacy
import nltk
from nltk import word_tokenize
import operator
import collections
import re
from nltk.corpus import wordnet as wn

class Word:
    def __init__(self, name):
        self.word_name = name
        self.pos = ""
        self.lemma = ""
        self.tag = ""
        self.dep = ""

class SentenceDetails:
    def __init__(self):
        self.sentence = []
        self.count = ""
        self.ners = []
        self.score = 0

# question_map = {"how tall": ['QUANTITY'], "who" : ['PERSON','ORGANIZATION'],"when" : ['DATE', 'TIME'],
#                 "where":['LOC', 'GPE'], "how much" : ['ORDINAL','PERCENT','MONEY'], "whose":['PERSON'],
#                 "how big": ['ORDINAL', 'QUANTITY'], "how many" : ['ORDINAL', "QUANTITY", "CARDINAL"],
#                 "how long" : ["QUANTITY", "DATE"], "how old" : ["DATE"], "how often" : ["DATE"],
#                 "how far" : ["TIME", "QUANTITY"]}

question_map = {"how tall": ['QUANTITY'], "who" : ['PERSON','ORG'],"when" : ['DATE', 'TIME'],
                "where":['LOC', 'GPE'], "how much" : ['PERCENT','MONEY'], "whose":['PERSON'],
                "how big": ['QUANTITY'], "how many" : ['ORDINAL', "QUANTITY", "CARDINAL"],
                "how long" : ["QUANTITY", "DATE", "TIME"], "how old" : ["DATE"], "how often" : ["DATE"],
                "how far" : ["TIME", "QUANTITY"], "how high": ['QUANTITY'], "how large": ['QUANTITY'], "how deep": ['QUANTITY']}                
nlp = spacy.load('en_core_web_sm')
# question_map = {}

def input_file_contents(filename):
    input_file = open(filename, "r")
    # input_file = open("all_input_file.txt", "r")
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
                word_obj.tage = word.tag_
                word_obj.dep = word.dep_
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
    wh_words = ["what", "who", "why", "when", "where", "which", "whose", "how"]
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
        # if word.text in wh_words or word            
        if word.text != '?' and ((word.is_stop == False) or (word.text in wh_words)):
            # or (word.is_stop == True and word.pos_ == "VERB"):
            word_obj = Word(word.text)
            # Add pos tagging
            word_obj.pos = word.pos_
            # Add lemmatization
            word_obj.lemma = word.lemma_

            question_arr.append(word_obj)
    return subject, direct_object, indirect_object, rootverb, question_arr, expected_answer_type



# def matchOrSimilarity(array, word):
#     for wordobject in array:
#         if wordobject == word.lemma:
#             # print("Match")
#             return True


def matchOrSimilarity(array, word, tf_dict):
    prob = 0
    # print(word.word_name, word.pos)
    # Check if word in question lemmas array
    for wordobject in array:
        if wordobject == word.lemma:
            # print("Match")
            if word.word_name != "." and word.word_name != "," and word.word_name != "-" and word.word_name != "\"" and word.word_name != "'s" and word.word_name != "'nt" and word.word_name != "...":
                count = sum(tf_dict.values())
                maximum_val = max(tf_dict.values())
                count_word = tf_dict[word.word_name]
                prob += 1- (count_word/maximum_val)
            # Check if verb
            if word.pos == "VERB":
                # print(word.word_name)
                prob+= 3
    return prob            

        # Word similarity
        # word1 = nlp(wordobject)
        # word2 = nlp(word.lemma)
        #  Similarity measure
        # if word1.similarity(word2) > 0.5 and wordobject.lemma == 'run':
        #     print("Similar: ", word1.similarity(word2))
        #     print(word1.text)
        #     print(word2.text)

def checkNer_for_who(sent_nerlist, sentence_record, original_question_string):
    match_count = 0
    question_ners = nlp(original_question_string).ents
    question_ner_list = []

    for each in question_ners:
        question_ner_list.append(each.label_)

    # if len(question_ner_list) == 1 and "PERSON" in question_ner_list:
    #     if
    if 'PERSON' not in question_ner_list:
        if 'PERSON' in sent_nerlist or 'FAC' in sent_nerlist:
            match_count += 6
        if 'name' in sentence_record.sentence[0]:
            match_count += 4
    elif 'ORG' not in question_ner_list:
        if 'ORG' in sent_nerlist:
            match_count += 6
        if 'name' in sentence_record.sentence[0]:
            match_count += 4

    #check if NAME or ORG is present in sentence
    for val in sent_nerlist:
        if 'PERSON' == val or 'ORG' == val:
            match_count += 4
            break
    return match_count


def checkNer(question, nerlist, expected_answer_type):
    matches = []
#    check if ner list and expected_answer_type have anything in common
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

def whenqs(overlapCount, matches, sentence_details_array, question_lem_arr):
    score = 0
    if matches!=0:
        score +=6
        score += overlapCount*3
    time_words = ['first', 'last', 'since', 'ago']
    if 'the last' in question_lem_arr:
        for word in time_words:
            if word in sentence_details_array[0].sentence[1]:
                score+=20
                break
    start_words = ['start', 'begin', 'since', 'year']
    if 'start' in question_lem_arr or 'begin' in question_lem_arr:
        for word in start_words:
            if word in sentence_details_array[0].sentence[1]:
                score+=20
                break
    return score

def whyqs(sentence_details_array, question_lem_arr, tf_dict, original_question_string):
    root = ""
    question_pos = nlp(original_question_string)
    for each in question_pos:
        if each.dep_ == "ROOT":
            root = each.lemma_
    if root == "":
        for each in question_pos:
            if each.pos_ == "VERB" and each.lemma_ != "be":
                root = each.lemma_        
                break
    # print("Root:", root)
    for index in range(0,len(sentence_details_array)):
        record = sentence_details_array
        record[index].count = 0
        for word in record[index].sentence[1]:
            # if matchOrSimilarity(question_lem_arr, word):
            #     record[index].count += 1
            
            prob = matchOrSimilarity(question_lem_arr, word, tf_dict)
            record[index].count += prob
            # if word.lemma == root:
            #     record[index].count += 2
            record[index].score = record[index].count*3

    answer = None
    max_score = 0    
    for index in range(0,len(sentence_details_array)):
        record = sentence_details_array
        if index+1 !=len(sentence_details_array) and record[index+1].score > 0:
            record[index].score +=3
        if index-1 >= 0 and record[index-1].score > 0:    
            record[index].score+=6
        if 'want' in record[index].sentence[0]:
            record[index].score+=6
        if 'so' in record[index].sentence[0] or 'because' in record[index].sentence[0]:
            record[index].score+=6
        if record[index].score > max_score:
            answer = record[index].sentence[0]
            max_score = record[index].score    
    print("Answer:::::---------------------------------", answer)    
    if 'because' in answer:
        index = answer.index('because')
        return remove_IntersectionFromQuestionAndAnswer(original_question_string, answer[index-1:])
        # return answer[index:] 
    if 'so' in answer:
        index = answer.index('so')
        return remove_IntersectionFromQuestionAndAnswer(original_question_string, answer[index-1:])
        # return answer[index:]
    if 'want' in answer:
        index = answer.index('want')
        return remove_IntersectionFromQuestionAndAnswer(original_question_string, answer[index-1:])
        # return answer[index:]
    if root in answer:
        index = answer.index(root)
        return remove_IntersectionFromQuestionAndAnswer(original_question_string, answer[index-1:])

    answer = remove_IntersectionFromQuestionAndAnswer(original_question_string, answer)
    return answer

def remove_IntersectionFromQuestionAndAnswer(question, answer):
    # s = list(set(answer.split()).difference(set(question.split())))
    # result = (" ".join(x for x in s))
    # return result
    result = ""
    question_list = question.split(' ')
    answer = answer.split(' ')
    for ans_word in answer:
        if ans_word.find('(') != -1:
            ans_word = ans_word.replace('(', '')
        if ans_word.find(')') != -1:
            ans_word = ans_word.replace(')', '')
        if ans_word.find(']') != -1:
            ans_word = ans_word.replace(']', '')
        if ans_word.find('[') != -1:
            ans_word = ans_word.replace('[', '')

        regex_match_word = '\s*'+ ans_word.lower() + '\s*'
        #if ans_word in question_list:
        # print(regex_match_word)
        if re.search(regex_match_word, (' '.join(question_list)).lower()):
          #  question_list.remove(ans_word)
            for i in range(len(question_list)):
                if ans_word.lower() in question_list[i].lower():
                    question_list.remove(question_list[i])
                    break
        else:
            result = result + ' '+ ans_word
    return result
   

def whatqs(sentence_details_array, question_lem_arr, original_question_string, tf_dict):
    question_ners = nlp(original_question_string).ents
    question_pos = nlp(original_question_string)
    question_ner_list = []
    root = ""
    for each in question_pos:
        if each.dep_ == "ROOT" and each.lemma_ != "be":
            root = each.text
    if root == "":
        for each in question_pos:
            if each.pos_ == "VERB" and each.lemma_ != "be":
                root = each.lemma_        
                break

    for each in question_ners:
        question_ner_list.append(each.label_)
    # print("*************************************")        
    # print(original_question_string)
    answer = None
    max_score = 0
    for index in range(0,len(sentence_details_array)):
        record = sentence_details_array
        record[index].count = 0
        record[index].score = 0
        for word in record[index].sentence[1]:
            # if matchOrSimilarity(question_lem_arr, word):
            #     record[index].count += 1
            #     record[index].score +=3
            
            prob = matchOrSimilarity(question_lem_arr, word, tf_dict)
            record[index].score += prob
            # for each_word in record[index].sentence[0]:
            if word.lemma == root:
                print(record[index].sentence[0])
                record[index].score +=30

            # if record[index].count > 0.8:
            #     print ( "Match rul1 : + 3")
            #     record[index].score +=3                    
            if ('DATE' in question_ner_list) and ('today' in record[index].sentence[0] or 'yesterday' in record[0].sentence[0] or 'tomorrow' in record[0].sentence[0] or 'last night' in record[0].sentence[0]) :
                record[index].score +=6
            if ('kind' in question_lem_arr) and ('call' in record[index].sentence[0] or 'from' in record[0].sentence[0]):
                record[index].score +=20
            if ('name' in question_lem_arr) and ('name' in record[index].sentence[0] or 'call' in record[0].sentence[0] or 'known' in record[0].sentence[0]):    
                record[index].score +=20
        if record[index].score > max_score:
            answer = record[index].sentence[0]
            max_score = record[index].score   
    answer = remove_IntersectionFromQuestionAndAnswer(original_question_string, answer)
    return answer
    
        # print(record[index].sentence[0])
        # print(record[index].score)
def get_index_of_who(question_arr):
    for i in range(len(question_arr)):
        if question_arr[i].lemma == "who":
            return i

def find_answer_from_sentence(answer_list, type, original_question_string):
    answer_substring = ""
    sent = nlp(answer_list)
    subject, dobject, idobject, rootverb, question_arr, expected_answer_type = extractpos(original_question_string)
    # print("Hey")
    # if type == "where":
    #     location_preps = ["in", "at", "near", "inside"]
    #     found_index = -1
    #     ner_list = nlp(answer_list).ents
    #     found_flag = False
    #     for location_prep in location_preps:
    #         sentence_array = answer_list.split(' ')
    #         if location_prep in sentence_array:
    #             found_index = answer_list.index(" " + location_prep + " ")
    #             found_flag = True
    #             break

    #     if found_flag:
    #         for each in ner_list:
    #             if (each.label_ == 'GPE' or each.label_ == 'LOC') and each.start_char >= found_index:
    #                 answer_substring = answer_substring + ' ' + each.text
    #     else:
    #         answer_substring = answer_list
    #     return answer_substring
    if type == "where":
        location_preps = ["in", "at", "near", "inside","from"]
        found_index = -1
        ner_list = sent.ents
        found_flag = False
        found_again = False
        min_index = 10000000
        for location_prep in location_preps:
            if (' ' + location_prep + ' ') in answer_list:
                found_index = answer_list.index(" " + location_prep + " ")
                if found_index < min_index:
                    min_index = found_index
                found_flag = True
        if found_flag:
            for each in ner_list:
                if (each.label_ == 'GPE' or each.label_ == 'LOC') and each.start_char >= min_index:
                    answer_substring = answer_substring + ' ' + each.text
                    found_again = True
            #answer_substring = answer_list[min_index+1:]
                # if (each.label_ == 'GPE' or each.label_ == 'LOC') and each.start_char >= found_index:
                #     answer_substring = answer_substring + ' ' + each.text
            if found_again == False:
                if min_index+50 < len(answer_list):
                    answer_substring = answer_list[min_index:min_index+50]
                else:
                    answer_substring = answer_list[min_index:]
                # answer_substring = answer_list
        else:
            answer_substring = answer_list
        return answer_substring

    elif type == "when":
        ner_list = nlp(answer_list).ents
        added_flag = False
        for each in ner_list:
            if (each.label_ == 'DATE' or each.label_ == 'TIME'):
                answer_substring = answer_substring + ' ' + each.text
                added_flag = True
                    # print("Substr:",answer_substring)
        if added_flag == True:
                # print("Returning: ", answer_substring)
            return answer_substring
        return answer_list

    elif type == "who":
        # ner_list = nlp(answer_list).ents
        # added_flag = False
        # for each in ner_list:
        #     if (each.label_ == 'PERSON' or each.label_ == 'ORG'):
        #         if each.text not in original_question_string:
        #             answer_substring = answer_substring + ' ' + each.text
        #             added_flag = True
        #             # print("Substr:",answer_substring)
        # if added_flag == True:
        #         # print("Returning: ", answer_substring)
        #     return answer_substring
        # return answer_list                
        ner_list = nlp(answer_list).ents
        added_flag = False
        result_string = ""
        who_index = get_index_of_who(question_arr)
        # check if there is verb after who other than [do, is, be] in the quesition
        if question_arr[who_index+1].pos == "VERB" and question_arr[who_index+1].lemma not in ["will", "do"]:
            #  check if that verb (lemma) is present in the answer
            for token in sent:
                if token.lemma_ == question_arr[who_index+1].lemma:
                    result = []
                    if sent[token.i+1].pos_ == "ADP":
                        # pick the words from ner_list that are after this index and break
                        for each in ner_list:
                            if answer_list.find(each.text) > answer_list.find(token.text):
                                result.append(each)
                    else:
                        # pick the words from ner_list that are before this index and break
                        for each in ner_list:
                            if answer_list.find(each.text) < answer_list.find(token.text):
                                result.append(each)
                    ner_list = result
                    if len(ner_list) == 0:
                        # Shrink the answer to before that verb/token
                        result_string = answer_list[:answer_list.find(token.text)]
                    break
        for each in ner_list:
            if each.label_ == 'PERSON' or each.label_ == 'ORG' or each.label_ == 'NORP' or each.label_ == 'GPE':
                if each.text not in original_question_string:
                    answer_substring = answer_substring + ' ' + each.text
                    added_flag = True
                    # print("Substr:",answer_substring)
        if added_flag == True:
                # print("Returning: ", answer_substring)
            return answer_substring
        if result_string != "":
            return result_string
        return answer_list
    # elif type == "how" :
    #     ner_list = nlp(answer_list).ents
    #     # handle case of how tall
    #     if "how tall" in original_question_string.lower():
    #         for ner in ner_list:
    #             if ner.label_ in question_map["how tall"]:
    #                 answer_substring = answer_substring + ' ' + ner.text

    #     elif "how many" in original_question_string.lower():
    #         for ner in ner_list:
    #             if ner.label_ in question_map["how many"]:
    #                 answer_substring = answer_substring + ' ' + ner.text
    #     else:
    #         answer_substring = answer_list
    #     return answer_substring    

    elif type == "how" :
        ner_list = nlp(answer_list).ents
        # handle case of how tall
        if "how tall" in original_question_string.lower():
            for ner in ner_list:
                if ner.label_ in question_map["how tall"]:
                    answer_substring = answer_substring + ' ' + ner.text

        elif "how far" in original_question_string.lower():
            for ner in ner_list:
                if ner.label_ in question_map["how far"]:
                    answer_substring = answer_substring + ' ' + ner.text

        elif "how deep" in original_question_string.lower():
            for ner in ner_list:
                if ner.label_ in question_map["how deep"]:
                    answer_substring = answer_substring + ' ' + ner.text

        elif "how large" in original_question_string.lower():
            for ner in ner_list:
                if ner.label_ in question_map["how large"]:
                    answer_substring = answer_substring + ' ' + ner.text

        elif "how often" in original_question_string.lower():
            for ner in ner_list:
                if ner.label_ in question_map["how often"]:
                    answer_substring = answer_substring + ' ' + ner.text

        elif "how big" in original_question_string.lower():
            for ner in ner_list:
                if ner.label_ in question_map["how big"]:
                    answer_substring = answer_substring + ' ' + ner.text

        elif "how old" in original_question_string.lower():
            for ner in ner_list:
                if ner.label_ in question_map["how old"]:
                    answer_substring = answer_substring + ' ' + ner.text

        elif "how many" in original_question_string.lower():
            for ner in ner_list:
                if ner.label_ in question_map["how many"]:
                    answer_substring = answer_substring + ' ' + ner.text

        elif "how much" in original_question_string.lower():
            for ner in ner_list:
                if ner.label_ in question_map["how much"]:
                    answer_substring = answer_substring + ' ' + ner.text

        elif "how long" in original_question_string.lower():
            for ner in ner_list:
                if ner.label_ in question_map["how long"]:
                    answer_substring = answer_substring + ' ' + ner.text
        else:
            answer_substring = answer_list
        return answer_substring    

# def sentence_similarity(question, probable_ans):
#     print("-------------------------------------------------")
#     print("Q:" , question)
#     print("PA:", probable_ans)
#     question = nlp(question)
#     answer = nlp(probable_ans)
#     score = question.similarity(answer)
#     print("Score:",score)

def overlap(question, sentence_details_array, expected_answer_type, rootverb, original_question_string, tf_dict):
    question_lem_arr = []
    answer_list = ""
    for word in question:
        if word.pos != "PUNCT":
            question_lem_arr.append(word.lemma)           
    who_ans = {}
    where_ans = {}
    when_ans = {}
    how_ans = {}
    
    if 'why' in question_lem_arr:
        return whyqs(sentence_details_array, question_lem_arr, tf_dict, original_question_string)
    elif 'what' in question_lem_arr:
        return whatqs(sentence_details_array, question_lem_arr, original_question_string, tf_dict)            
    for record in sentence_details_array:
        verbMatchCnt = 0
        record.count = 0
        for word in record.sentence[1]:
            # if matchOrSimilarity(question_lem_arr, word):
            #     record.count += 1
            
            prob = matchOrSimilarity(question_lem_arr, word, tf_dict)
            record.count += prob
            if word.lemma == rootverb:
                verbMatchCnt += 1
        nerlist = []
        for each in record.ners:
            nerlist.append(each.label_)

        if "how" in question_lem_arr:
            matches = checkNer(question_lem_arr, nerlist, expected_answer_type)
            if record.count > 0 and matches != 0:
                how_score = len(matches)+record.count+(verbMatchCnt*5)
                if how_ans.get(how_score):
                    how_ans[how_score].append(record.sentence[0])
                else:
                    how_ans[how_score] = [record.sentence[0]]
        if 'how' in question_lem_arr and record.count >= 1 and how_ans != {}:
            answer_list = "".join(sorted(how_ans.items(), reverse=True)[0][1][0])

        if "where" in question_lem_arr:
            matches = checkNer(question_lem_arr, nerlist, expected_answer_type)
            score = whereqs(record.count, matches, sentence_details_array)
            if where_ans.get(score):
                where_ans[score].append(record.sentence[0])
            else:
                where_ans[score] = [record.sentence[0]]

        if 'who' in question_lem_arr and record.count >= 1:
            #print("Ans: ",record.sentence[0])
            matches = checkNer_for_who(nerlist, record, original_question_string)
            verbMatchCnt = verbMatchCnt*5
            record_count = record.count * 3
            final_count = matches + record_count + verbMatchCnt

            if who_ans.get(final_count):
                who_ans[final_count].append(record.sentence[0])
            else:
                who_ans[final_count] = [record.sentence[0]]


        if 'who' in question_lem_arr and record.count >= 1 and who_ans.items != []:
            answer_list = "".join(sorted(who_ans.items(), reverse=True)[0][1][0])

        if "when" in question_lem_arr:
            matches = checkNer(question_lem_arr, nerlist, expected_answer_type)
            score = whenqs(record.count, matches, sentence_details_array, question_lem_arr)
            if when_ans.get(score):
                when_ans[score].append(record.sentence[0])
            else:
                when_ans[score] = [record.sentence[0]]



    if "when" in question_lem_arr and when_ans.items != []:
        answer_list = "".join(sorted(when_ans.items(), reverse = True)[0][1][0])
        answer_list = find_answer_from_sentence(answer_list, "when", original_question_string)
    elif "where" in question_lem_arr and where_ans.items != []:
        answer_list = "".join(sorted(where_ans.items(), reverse = True)[0][1][0])
        answer_list = find_answer_from_sentence(answer_list, "where", original_question_string)
    elif "who" in question_lem_arr and who_ans.items != []:
        answer_list = find_answer_from_sentence(answer_list, "who", original_question_string)
    elif "how" in question_lem_arr and who_ans.items != []:
        answer_list = find_answer_from_sentence(answer_list, "how", original_question_string)
    # elif "how" in question_lem_arr and how_ans != {}:
    #     answer_list = "".join(sorted(where_ans.items(), reverse=True)[0][1][0])



    return answer_list


def find_answer(qid, question, sentence_details_array, question_dict, tf_dict):
    # print(qid)
    # print(question)
    question = question.split(":")
    original_question = question[1]
    question = question[1].strip()
    # print(question)
    subject, dobject, idobject, rootverb, question_arr, expected_answer_type = extractpos(question)
    # print("Subject:", subject)
    # print("Direct Object:", dobject)
    # print("Indirect Object:", idobject)
    # print("Root:", rootverb)
    answer_list = overlap(question_arr, sentence_details_array, expected_answer_type, rootverb, original_question, tf_dict)
    answer = ""
    if answer_list != "":
        question_dict[qid] = [question, answer_list]
        answer = answer_list
    else:
        question_dict[qid] = [question, "No answer found"]

    # answer_list = overlap(question_arr, sentence_details_array, expected_answer_type, rootverb, )
    # question_dict[qid] = answer_list

    # for record in answer_list:s
    #     print(record["sentence"][0])
    #     print(record["count"])
    # print("***********************************")
    # for token in question_arr:
    #     print(token.word_name, token.lemma, token.pos)
    #     print(" ")
    header = "Answer: "
    return "\n" + header + answer


def process_question(question_data, output_stream, sentence_details_array, question_dict, tf_dict):
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
            # print(each)
            answer = find_answer(qid, each, sentence_details_array, question_dict, tf_dict)
            # print(answer)
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

def checkmatch(answer_found, answer):
    if answer_found!="No answer found":
        answers = answer.split('|')
        count = 0
        for ans in answers:
            match = 0
            for word in ans.split(" "):
                if word in answer:
                    match+=1
            if match > count:
                count = match
        num_words_answer_found = len(answer_found)
        num_words_actual_answer = len(answer) 
        p = count/num_words_actual_answer
        r = count/num_words_answer_found
        if (p+r) == 0:
            f_score = 0
        else:
            f_score = 2*(p)*(r)/(p+r)
        # print(f_score)
    return True 
    # match = 0
    # for ans in answers:
    #     if ans in answer_found:
    #         match+=1
    # if match!=0:
    #     return True
    # return False

def check_accuracy(question_dict, answer_dict, accuracy):
    for questionid, quest_ans in question_dict.items():
        # print("QID: ",questionid)
        # print("Question: ", quest_ans[0])
        answer = answer_dict.get(questionid)
        # print("Answer expected:", answer)
        answer_found = quest_ans[1]
        # print("Answer found: ", answer_found)
        if checkmatch(answer_found, answer):
            # print("Correct Answer!!!!")
            accuracy+=1
        return accuracy    

def gettf(story_data):
    story = story_data.split('\n\n')
    story = story[2:]
    story = ' '.join(story)
    story = story.replace('\n', ' ')
    story = story.replace('.\"', ". \"")
    story = story.split()
    c = collections.Counter(story)
    return c


def fetch_file_data_and_process(input_file_data, output_stream, answer_key):
    directory_path = input_file_data[0]
    accuracy =0
    total = 0
    for i in range(1, len(input_file_data)):
        # process each set of story and questions at once.
        filename_path = directory_path + input_file_data[i]

        # ------ STORY ------
        # get story from each file
        filename_path_story = filename_path + ".story"
        story_data = open(filename_path_story, "r").read()
        story, sentence_details_array = get_story_data(story_data)
        tf_dict = gettf(story_data)
        # print(tf_dict)
        # print(max(tf_dict.values()))

        # ------ QUESTIONS ------
        question_dict = {}
        filename_path_questions = filename_path + ".questions"
        question_data = open(filename_path_questions, "r").read()
        process_question(question_data, output_stream, sentence_details_array, question_dict, tf_dict)
    
        # ------ ANSWERS ------
        answer_dict = {}
        filename_path_answers = filename_path + ".answers"
        answers_data = open(filename_path_answers, "r").read()
        populate_answer_dict(answers_data, answer_dict)
        answer_key.write(answers_data)
        for questionid, quest_ans in question_dict.items():
            print("QID: ",questionid)
            print("Question: ", quest_ans[0])
            answer = answer_dict.get(questionid)
            print("Answer expected:", answer)
            answer_found = quest_ans[1]
            print("Answer found: ", answer_found)
            if checkmatch(answer_found, answer):
                # print("Correct Answer!!!!")
                accuracy+=1
        total+=len(question_dict.items())
        accuracy_count = 0

        # accuracy_count = check_accuracy(question_dict, answer_dict, accuracy_count)
        # print("***********************************")
        # print("Accuracy_count:", accuracy_count)
        # print("Total qs:", len(question_dict.items()))
        # print("Percentage accuracy: ", accuracy_count/len(question_dict.items()))
            # for answer in answer_list:
            #     if answer_dict.get(question) in answer:
            #         accuracy_count +=1
            #     print("Ans:  ",answer)
        # print("**********************************************************************")
        # print("Accuracy:", accuracy_count)
        # print("**********************************************************************")
    # print("***********************************")
    # print("Accuracy_count:", accuracy)
    # print("Total qs:", total)
    # print("Percentage accuracy: ", (accuracy/total)*100)
            
def main():
    filename = sys.argv[1]
    input_file_data = input_file_contents(filename)
    output_stream = open("output_test.txt", "w")
    answer_key = open("answerkey_test.txt", "w")
    # get_questions_map("question_types.txt")
    fetch_file_data_and_process(input_file_data, output_stream, answer_key)
    output_stream.close()


if __name__ == "__main__": main()
