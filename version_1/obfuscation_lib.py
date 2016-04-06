from nltk.corpus import wordnet
from awesome_print import ap
import sys
import random
import nltk
import glob
import codecs
import csv
import json
from nltk.corpus import stopwords
from nltk.stem.porter import *
from mstranslator import Translator
from yandex_translate import YandexTranslate
import requests.packages.urllib3
import random
import os
requests.packages.urllib3.disable_warnings()

def translate_1(text, source_language_code, target_language_code):
	translator = YandexTranslate("trnsl.1.1.20160221T144519Z.fb49de2271d61b51.299460f2121de3773b72d98b5c3e7118e7b0139c")
	response = translator.translate(text, "{0}-{1}".format(source_language_code,target_language_code))
	translation = response["text"][0]
	return translation

def translate_2(text, source_language_code, target_language_code):
	client_id = "irlab-pan-author-obfuscation-16"
	client_secret = "TWGKKcKQ/VoASe1EksnZBNNVA8mlThBsPQ/5z7Wqkkk="
	translator = Translator(client_id, client_secret)
	translation = translator.translate( text, lang_from=source_language_code, lang_to=target_language_code)
	return translation


def randomized_translation(text):
	language_code = random.choice([ ["vietnamese","vi"],
							["hungarian","hu"],
							["haitian","ht"],
							["chinese","zh"],
							["maltese","mt"],
							["norwegian","no"]
						 ])
	if ( random.random() > 0.5):
		translation_to = translate_1(text, "en", language_code[1])
		translation_fro = translate_2(translation_to, language_code[1] , "en")
		return(translation_fro)
	else:
		translation_to = translate_2(text, "en", language_code[1])
		translation_fro = translate_1(translation_to, language_code[1] , "en")
		return(translation_fro)


def obfuscate(line):

	if( is_american):
		line = turn_british(line)
	else:
		line = turn_american(line)
	line = randomized_translation(line)
	line = get_paraphrases(line)
	return line


def read_dictionaries(path_of_file):
	british_american_dic ={}
	american_british_dic = {}
	file_object = csv.reader(open(path_of_file, 'r'), delimiter = ';')
	for row in file_object:
		british_american_dic[row[0]] = row[1]
		american_british_dic[row[1]] = row[0]
	
	return (british_american_dic, american_british_dic)

def assign_american_or_brit(voc, path_of_file):
	british_american_dic = read_dictionaries(path_of_file)[0]
	b_count = 0
	a_count = 0
	bo_count = 0
	cannot_decide = 0	
	count = 0	
	for i in british_american_dic:
		if i in voc and british_american_dic[i] not in voc:
			b_count = b_count + 1
			count = count + voc[i]		
		elif i not in voc and british_american_dic[i] in voc:
			a_count = a_count + 1
			count = count + voc[british_american_dic[i]]
		elif i not in voc and british_american_dic[i] not in voc:
			cannot_decide =  cannot_decide + 1
		else:
			bo_count = bo_count + 1
	if b_count > a_count:
		return False
	elif a_count > b_count:
		return True
	else:
		if random.randint(1,2) == 1:
			return True
		else:
			return False


def avg_length_and_vocab(corpus):
	vocab = {}
	list_of_files = glob.glob(  os.path.join(corpus, "*.txt")  )

	w = 0
	l = 0
	for i in list_of_files:
		content = codecs.open(i, "r", "utf-8").read().strip()
		lines = tokenizer.tokenize(content)
		l = l + len(lines)
		for x in lines:
			p = nltk.word_tokenize(x)
			w = w + len(p)
			for each in p:
				if each.strip().lower() not in vocab:
					vocab[each.strip().lower()]= 1
				else:	
					vocab[each.strip().lower()] = vocab[each.strip().lower()] + 1
	return (vocab,w/float(l))


def turn_british(sentence):
	tokenized_words = nltk.word_tokenize(sentence)
	for word in tokenized_words:
		if(american_to_british.get(word, False)):
			sentence = sentence.replace(word, american_to_british[word])
	return(sentence)


def turn_american(sentence):
	tokenized_words = nltk.word_tokenize(sentence)
	for word in tokenized_words:
		if(british_to_american.get(word, False)):
			sentence = sentence.replace(word, british_to_american[word])
	return(sentence)



def get_postag(sample):
	tokenized_words = nltk.word_tokenize(sample)
	tagged_words = nltk.pos_tag(tokenized_words)
	return(tagged_words)


def get_synonyms(word):
	syns = wordnet.synsets(word)
	if len(syns) > 0:
		return([lemma.name() for lemma in syns[0].lemmas()])
	else:
		return("")

def get_paraphrases(sentence):
	paraphrases = []
	words_to_replace = []
	for word_tag in get_postag(sentence):
		if word_tag[1] in (noun_tags + adverb_tags + adjective_tags + verb_tags):
			words_to_replace.append(word_tag[0])
	words_to_replace = random.sample( words_to_replace , min(random.choice([3,4,5]), len(words_to_replace) ) )
	for word in words_to_replace:
			synonyms = get_synonyms(word)
			if((len(synonyms)>0) and (word not in english_stopwords) ):
				minimum_usage = vocabulary.get(synonyms[0],0)
				minimum_usage_synonym = synonyms[0]
				for synonym in synonyms:
					# ap(synonym)
					if( (minimum_usage > vocabulary.get(synonym,0)) and ( stemmer.stem(word) != stemmer.stem(synonym)) ):
						minimum_usage = vocabulary.get(synonym,0)
						minimum_usage_synonym = synonym
				minimum_usage_synonym = " ".join(minimum_usage_synonym.split("_"))
				synonym = random.choice(synonyms)
				sentence = sentence.replace(word, minimum_usage_synonym)
	paraphrases.append(sentence)
	return paraphrases[0]



def obfuscate_author(author_input_directory, output_file_path):

	global tokenizer
	global verb_tags
	global adjective_tags
	global noun_tags
	global adverb_tags
	global english_stopwords
	global stemmer	
	global is_american
	global american_to_british
	global british_to_american
	global british_american_dic
	global american_british_dic
	global vocabulary

	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	verb_tags = ["VB", "VBD", "VBG", "VBN", "VBP"]
	adjective_tags = ["JJ", "JJR", "JJS"]
	noun_tags = ["NN", "NNS"]
	adverb_tags = ["RB", "RBR", "RBS"]
	english_stopwords = stopwords.words('english')
	stemmer = PorterStemmer()

	obfuscation_document_content =  codecs.open(  os.path.join(author_input_directory, "original.txt") , "r", "utf-8").read().strip()
	lines = tokenizer.tokenize(obfuscation_document_content)

	position_tags = [(0,len(lines[0]))]
	for i in range(1,len(lines)):
		position_tags.append( ((position_tags[i-1][1] + 1) , (position_tags[i-1][1] + len(lines[i]) ) ) )


	lines = [line.replace("\r\n", " ").replace("\n", " ") for line in lines]
	obfuscated_lines = []

	vocabulary , average_document_length = (avg_length_and_vocab(author_input_directory))
	is_american = assign_american_or_brit(vocabulary, 'change.csv')
	british_to_american , american_to_british = read_dictionaries( 'change.csv')

	for line in lines:
		ap("About to obfuscate:")
		print(line)
		obfuscated_line = obfuscate(line)
		obfuscated_lines.append(obfuscated_line)
		ap("Obfuscated line is:")
		print(obfuscated_line)
		ap("--------------------------")

	output_dictionary = {}

	obfuscations = []

	for i in range(len(lines)):
		obfuscation = {}
		obfuscation["original"] = lines[i]
		obfuscation["original-start-charpos"] = position_tags[i][0]
		obfuscation["original-end-charpos"] = position_tags[i][1]
		obfuscation["obfuscation"] = obfuscated_lines[i]
		obfuscation["obfuscation-id"] = i+1
		obfuscations.append(obfuscation)	

	obfuscation_file = codecs.open(  output_file_path ,"w", "utf-8")
	obfuscation_file.write(json.dumps(obfuscations) )
	obfuscation_file.close()

