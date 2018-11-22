This project requires the following:

**************************************************

This code is tested on lab1-12 machine of CADE lab.

**************************************************

Time estimate:
It will aproximately take 10 seconds to execute for each story 
On the development dataset it took less than a minute to execute on 70 stories

**************************************************

libraries/models:

1. Spacy - https://spacy.io/
2. spacy.load('en_core_web_sm')
3. NLTK - https://www.nltk.org/

Note: we set up a virtual environment on lab1-12 machine and 
activated using:
source env/bin/activate.csh 

**************************************************

Instructions to run:

source /home/u1209537/env/bin/activate.csh
bash run.sh <input_file>

**************************************************

Output file:
Output is generated in file: output.txt

**************************************************

Debugging output:

The output of the perl script on given development dataset generated during debugging is in: fscorecheck.txt

**************************************************

Contributions:
Antara Bahursettiwar (u1209537):
Processing questions files and printing the result into the output file
Tokenizing and POS tagging for questions
Processed question types: What, Why, When


Neha Kherde (u1205893):
Processing the stories from the story file
Story sentence splitting 
Tokenizing and POS tagging for sentences in stories
Processed question types: How, Who, Where

**************************************************
