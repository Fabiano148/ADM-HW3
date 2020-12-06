#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import re
import os
import urllib.request
from urllib.request import urlopen
import csv
from langdetect import detect
import json
import pandas as pd
from collections import Counter
import nltk
from nltk.corpus import stopwords  
from nltk.tokenize import word_tokenize 
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
nltk.download('punkt')
nltk.download('stopwords')


# # Creation of the txt file that collects the list of the urls
# ## First, I open a txt file where I'm going to write the list of the books' url.
# ## With a for loop I check the first 300 pages (I stopped on page 12 due to lack of time) and, through BeautifulSoup, I extract every bookTitle, adding them to a list ("list_ads").
# ## With a for loop on "list_ads", I add the string 'https://www.goodreads.com/' to every book, obtaining the relative url. I added every url to a list ("list_of_url").
# ## With a for loop on the "list_of_url", I get every url and I save the relative html page in the directory of the relative page (for example, the html of the books in the first page are saved in the directory "page_1" with the name "article_<num_article>"). I create the relative directory if not exists.

# In[ ]:


# I open a txt file where I'm going to write the list of the books' url
txt_url = open("List_of_url.txt", "w")
# With a for loop I check the first 300 pages and, through BeautifulSoup, I extract every bookTitle, adding them to a list ("list_ads")
for num_page in range(1,301): #range(301)
    list_of_url = []
    best_books_ever = 'https://www.goodreads.com/list/show/1.Best_Books_Ever?page='+str(num_page)
    page = urlopen(best_books_ever)
    soup = BeautifulSoup(page, 'html.parser')
    list_ads = soup.findAll('a' ,class_='bookTitle')
# With a for loop on "list_ads", I add the string 'https://www.goodreads.com/' to every book, obtaining the relative url. I added every url to a list ("list_of_url").
    for i in list_ads:
        list_of_url.append('https://www.goodreads.com/'+str(i.get('href')))
#With a for loop on the "list_of_url", I get every url and I save the relative html page in the directory of the relative page (for example, the html of the books in the first page are saved in the directory "page_1" with the name "article_<num_article>"). I create the relative directory if not exists.
    for line in range(len(list_of_url)):
        txt_url.write(list_of_url[line]+'\n')
        html = urlopen(list_of_url[line]).read().decode('utf-8')
        directory = "page_"+str(num_page)
        if not os.path.exists(directory):
            os.makedirs(directory)
        urllib.request.urlretrieve(list_of_url[line], directory+"/article_"+str((num_page-1)*100 + line)+".html")
txt_url.close()


# # Creation of a tsv file for every html page
# ## With a for loop on the pages (directory: "page_1", "page_2", etc) and a for loop on the html inside every page/directory ("article_0.html, "article_1.html" and so on in "page_1" directory etc) I parse every html page through BeautifulSoup
# ## For every html I verify that the Plot is in english, through "detect". If it is in english, I consider that book, otherwise I discard it.
# ## I open a tsv file for every html in every page/directory and I write the header of the tsv file
# ## I find every information in html page through BeautifulSoup, and I add this information to the relative tsv file.

# In[3]:


# With a for loop on the pages (directory: "page_1", "page_2", etc) and a for loop on the html inside every page/directory ("article_0, "article_1" and so on in "page_1" directory etc) I parse every html page through BeautifulSoup
for page in range(1,12): #for page in (1:301):
    for html in range(0,100):
        try:
            soup = BeautifulSoup(open("page_"+str(page)+"/article_"+str((page-1)*100 + html)+".html",encoding="utf8"), "html.parser")
            # For every html I verify that the Plot is in english, through "detect". If it is in english, I consider that book, otherwise I discard it.
            plot_verified = soup.find('div', id='descriptionContainer')
            if plot_verified is not None:
                Plot_verified = plot_verified.text.strip()
            if detect(Plot_verified) == 'en':   
                #I open a tsv file for every html in every page/directory and I write the header of the tsv file
                with open('page_'+str(page)+'/article'+str((page-1)*100 + html)+'.tsv','wt', encoding="utf8" ) as out_file:
                    tsv_writer = csv.writer(out_file, delimiter='\t')
                    tsv_writer.writerow(['bookTitle', 'bookSeries','bookAuthors','ratingValue','ratingCount','reviewCount','Plot','NumberofPages','Publishing_Date','Characters','Setting','Url'])
                    # I find every information in html page through BeautifulSoup, and I add this information to the relative tsv file.
                    title = soup.find('h1')
                    if title is not None:
                        bookTitle = title.text.strip()
                    else:
                        bookTitle = ''
                    series = soup.find('h2', id='bookSeries')
                    if series is not None:
                        bookSeries = series.text.strip()
                    else:
                        bookSeries=''
                    author = soup.find('div', id='bookAuthors')
                    if author is not None:
                        bookAuthors = author.text.strip()
                    else:
                        bookAuthors=''
                    ratings = soup.find("span", {"itemprop": "ratingValue"})
                    if ratings is not None:
                        ratingValue = ratings.text.strip()
                    else:
                        ratingValue=''
                    giv_ratings = soup.find("meta", {"itemprop": "ratingCount"})
                    if giv_ratings is not None:
                        ratingCount = giv_ratings.text.strip()
                    else:
                        ratingCount=''
                    num_reviews = soup.find("meta", {"itemprop": "reviewCount"})
                    if num_reviews is not None:
                        reviewCount = num_reviews.text.strip()
                    else:
                        reviewCount=''
                    plot = soup.find('div', id='descriptionContainer')
                    if plot is not None:
                        Plot = plot.text.strip()
                    else:
                        Plot=''
                    num_pages = soup.find("span", {"itemprop": "numberOfPages"})
                    if num_pages is not None:
                        NumberofPages = num_pages.text.strip()
                    else:
                        NumberofPages=''
                    published = soup.findAll('div', class_='row')
                    try:
                        pub = published[1]
                        if pub is not None:
                            Publishing_Date = pub.text.strip()
                        else:
                            Publishing_Date=''
                    except:
                        Publishing_Date=''
                    characters = soup.findAll('div', class_='infoBoxRowItem')
                    try:
                        char = characters[4]
                        if char is not None:
                            Characters = char.text.strip()
                        else:
                            Characters=''
                    except:
                        Characters=''
                    setting = soup.findAll('div', class_='infoBoxRowItem')
                    try:
                        sett = setting[5]
                        if sett is not None:
                            Setting = sett.text.strip()
                        else:
                            Setting=''
                    except:
                        Setting=''
                    URL = soup.findAll('link')
                    try:
                        Url = URL[0].get('href')
                    except:
                        Url = ''
                    tsv_writer.writerow([bookTitle, bookSeries,bookAuthors,ratingValue,ratingCount,reviewCount,Plot,NumberofPages,Publishing_Date,Characters,Setting,Url])
            else:
                continue
        except:
            continue


# # Removing stopwords, punctuation and stemming.
# # Creation of a json "vocabulary" that maps each word in the html pages to an integer "term_id".
# # Creation of a json "inverted_index", where for every "term_id" I write all the "document_i" in which the relative word is present.
# ## I create the two vocabularies "vocabulary" and "index_vocabulary"
# ## I use a for loop on the pages (directory: "page_1", "page_2", etc) and a for loop on the tsv file inside every page/directory ("article0.tsv", "article1.tsv" and so on in "page_1" directory etc)
# ## I apply the stemming to the words in the Plot.
# ## I tokenize the word in the "Plot" and I consider every english stopwords. With a for loop on the words extract with tokenizer, I check if the word isn't a stopword. If so, I add this word to the list "filtered_sentence".
# ## I create a "list_without_punct" with the words of the "Plot" without punctuation.
# ## With a for loop, I check if the words in "filtered_sentence" are also in "list_without_punct" (to discard punctuation). If so I add the word to filtered_sentence_without_punct.
# ## I verify if a word is already present in the "vocabulary". If not, I add this word to the "vocabulary", associating it to a sequential integer (key). I also add that document to the "inverted_index" for that sequential integer (key).
# ## If that document is not yet present in the "inverted_index" for that sequential integer (key), I add it.
# ## I write the two dictionaries "vocabulary" and "inverted_index" on the relative json file.

# In[4]:


# I create the two vocabularies "vocabulary" and "index_vocabulary"
vocabulary = {}
index_vocabulary = 1
inverted_index = {}
tokenizer = RegexpTokenizer(r'\w+')
porter = PorterStemmer()
# I use a for loop on the pages (directory: "page_1", "page_2", etc) and a for loop on the html inside every page/directory ("article_0, "article_1" and so on in "page_1" directory etc)
for page in range(1,12): #for page in (1:301):
    for file in range(0,100):
        try:
            # For every tsv file, I get the "Plot"
            tsv_read = pd.read_csv('page_'+str(page)+'/article'+str((page-1)*100 + file)+'.tsv', sep='\t')
            PLOT = tsv_read['Plot'][0]
            # I apply the stemming to the words in the Plot.
            frase = porter.stem(PLOT)
            frase_1 = frase
            # I tokenize the word in the "Plot" and I consider every english stopwords. With a for loop on the words extract with tokenizer, I check if the word isn't a stopword. If so, I add this word to the list "filtered_sentence".
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(frase_1)
            filtered_sentence = [] 
            for w in word_tokens:
                if w not in stop_words:  
                    filtered_sentence.append(w)
            filtered_sentence_without_punct = [] 
            # I create a "list_without_punct" with the words of the "Plot" without punctuation.
            list_without_punct = tokenizer.tokenize(frase)
            # With a for loop, I check if the words in "filtered_sentence" are also in "list_without_punct" (to discard punctuation). If so I add the word to filtered_sentence_without_punct.
            for t in filtered_sentence:
                if t in list_without_punct:
                    filtered_sentence_without_punct.append(t)
                    # I verify if a word is already present in the "vocabulary". If not, I add this word to the "vocabulary", associating it to a sequential integer (key). I also add that document to the "inverted_index" for that sequential integer (key).
                    if t not in vocabulary.values():
                        vocabulary[index_vocabulary] = t
                        # Here I verify if the key is not present in the "inverted_index" to decide where insert the tab 
                        if index_vocabulary not in inverted_index.keys():
                            inverted_index[index_vocabulary] ='article'+str((page-1)*100 + file)
                        else:
                            inverted_index[index_vocabulary] =',article'+str((page-1)*100 + file)
                        index_vocabulary += 1
                    # If that document is not yet present in the "inverted_index" for that sequential integer (key), I add it.
                    elif ('article'+str((page-1)*100 + file) or ',article'+str((page-1)*100 + file))  not in inverted_index[list(vocabulary.keys())[list(vocabulary.values()).index(t)]]:
                        inverted_index[list(vocabulary.keys())[list(vocabulary.values()).index(t)]] += ',article'+str((page-1)*100 + file)
        except:
            continue
# I write the two dictionaries "vocabulary" and "inverted_index" on the relative json file.
with open('vocabulary.json', 'w') as fp:
    json.dump(vocabulary, fp)
with open('inverted_index.json', 'w') as fp:
    json.dump(inverted_index, fp)


# # Given a query in input, the search engine returns information about documents that contain all the words in the query
# ## Similarly to what was done previously for the words in the "Plot" of every book, I remove stopwords, punctuation and apply stemming from the query search.
# ## I check if the words in the search query are registred in the 'vocabulary' and I get the relative key(term_id). I add these id to a list ("list_of_term_id_input").
# ## From the term_id in "list_of_term_id_input", I extract the relative value (the article<i'> that contain that word) from the dict "inverted_index". I add this article<i'> to a list (of lists) "list_of_term_id_input_in_dict". That list contain the lists of article for every word.
# ## I split the item in the list (of lists) "list_of_term_id_input_in_dict", getting every article<i'> and then I get an unique flat list from the list of lists. Now, if an article is present more times, it means that more of the input words are present in that article.
# ## With Counter, I check the number of times an article<i'> appears in the flat list. If this number is equal to the number of the words entered in input, this means that all the input words are present in that article, so I have to exhibit it in output. To do this, I add this article to the list "list_of_article", then with a for cicle I extract all the articles from the various directories and I add them to a dataframe. I print that dataframe and also generate a tsv output.

# In[10]:


# Query and output
query = input("Enter your search: ")
# Similarly to what was done previously for the words in the "Plot" of every book, I remove stopwords, punctuation and apply stemming from the query search.
frase = porter.stem(query)
example_sent = frase
stop_words = set(stopwords.words('english'))
word_tokens = word_tokenize(example_sent)
filtered_sentence = [] 
for w in word_tokens:
    if w not in stop_words:  
        filtered_sentence.append(w)
filtered_sentence_without_punct = [] 
list_without_punct = tokenizer.tokenize(frase)
for t in filtered_sentence:
    if t in list_without_punct:
        filtered_sentence_without_punct.append(t)
#I check if the words in the search query are registred in the 'vocabulary' and I get the relative key(term_id). I add these id to a list ("list_of_term_id_input").
list_of_term_id_input = []
for inp in filtered_sentence_without_punct:
    if inp in vocabulary.values():
        key = list(vocabulary.keys())[list(vocabulary.values()).index(inp)]
        list_of_term_id_input.append(key)
# From the term_id in "list_of_term_id_input", I extract the relative value (the article<i'> that contain that word) from the dict "inverted_index". I add this article<i'> to a list (of lists) "list_of_term_id_input_in_dict". That list contain the lists of article for every word.
list_of_term_id_input_in_dict = []
for term in list_of_term_id_input:
    list_of_term_id_input_in_dict.append(inverted_index[term])
# I split the item in the list (of lists) "list_of_term_id_input_in_dict", getting every article<i'> and then I get an unique flat list from the list of lists. Now, if an article is present more times, it means that more of the input words are present in that article.
list_of_term_id_str = []
for cont in list_of_term_id_input_in_dict:
    list_of_term_id_str.append(cont.split(","))
# From the list of lists, I get an unique flat_list
flat_list = []
for sublist in list_of_term_id_str:
    for item in sublist:
        flat_list.append(item)
# With Counter, I check the number of times an article<i'> appears in the flat list. If this number is equal to the number of the words entered in input, this means that all the input words are present in that article, so I have to exhibit it in output. To do this, I add this article to the list "list_of_article", then with a for cicle I extract all the articles from the various directories and I add them to a dataframe. I print that dataframe and also generate a tsv output.       
conteggio = Counter(flat_list)
list_of_article = []
for c in conteggio:
    if conteggio[c] == len(filtered_sentence_without_punct):
        list_of_article.append(c)
#list_of_article
Output = pd.DataFrame(columns=['bookTitle','Plot','Url'])
for page in range(1,12): #for page in (1:301):
    try:
        for article in list_of_article:
            tsv_read = pd.read_csv('page_'+str(page)+'/'+str(article)+'.tsv', sep='\t')
            row = [tsv_read['bookTitle'][0], tsv_read['Plot'][0], tsv_read['Url'][0]]
            Output.loc[len(Output)] = row
    except:
        continue
print(Output)
Output.to_csv('Output.tsv', sep='\t')


# In[ ]:




