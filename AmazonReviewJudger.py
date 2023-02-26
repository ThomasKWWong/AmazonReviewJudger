#%%
from bs4 import BeautifulSoup
import requests
import lxml
import re
import pandas as pd
import customtkinter
#https://github.com/TomSchimansky/CustomTkinter
from tkinter import *
import matplotlib.pyplot as plt
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import lxml
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36", "Accept-Encoding":"gzip, deflate, br", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
URL = "https://www.amazon.com//Indoor-Basketballs-Friendly-Official-Regulation/product-reviews/B09BSGBDM8/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"


#%%
#first scrape
page_to_scrape = requests.get(URL, headers =  HEADERS)
soup = BeautifulSoup(page_to_scrape.content, "html.parser")
soupPretty = BeautifulSoup(soup.prettify(), "html.parser")
print(soupPretty)

#%%
nltk.download([
    "stopwords",
    "vader_lexicon", 
    "punkt", 
    "state_union", 
    'wordnet', 
    'omw-1.4'])
#%%
#title stuff
title = soupPretty.find(id='productTitle')
if title != None:
    title = title.get_text()
    print(title)
else:
    print("no title")


# %%
#get all reviews
reviews = soupPretty.find_all("span", {"class": "a-size-base review-text review-text-content"})
for review in reviews:
    review = (review.text) #gets review text
    print(review)
# %%
#star rating
ratings = soupPretty.find_all("i", {"data-hook":"review-star-rating"})
for rating in ratings:
    str = rating.span.string #gets string "#.0 out of 5 stars"
    #print(rating)
    print(int(str.split('.0')[0]))

# %%
#opens all reviews page of main product page
nextLink = soupPretty.find("a", {"data-hook": "see-all-reviews-link-foot"})
nextLink = "https://www.amazon.com/" + nextLink['href']
#print(nextLink)
print(nextLink)

#%%
#get link to next page
nextLink = soupPretty.find("li", {"class": "a-last"})
if(nextLink["class"] != ['a-disabled', 'a-last']):
    nextLink = "https://www.amazon.com/" + nextLink.a['href']
    print(nextLink)
else:
    print("last page")


#%%
#while loop that accesses all reviews, creates arrays
#for reviews and comments

def thomas(link):

    #initialize variables used to get   soup
    URL = link
    HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36", "Accept-Encoding":"gzip, deflate, br", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    #arrays that will be turned into pandas df
    allReviews = []
    allRatings = []
    #soup cooking
    page_to_scrape = requests.get(URL, headers =  HEADERS)
    soup = BeautifulSoup(page_to_scrape.content, "html.parser")
    soupPretty = BeautifulSoup(soup.prettify(), "html.parser")
    #get the link for ALL reviews page on main product page
    nextLink = soupPretty.find("a", {"data-hook": "see-all-reviews-link-foot"})
    URL = "https://www.amazon.com/" + nextLink['href']
    #new soup cooking
    page_to_scrape = requests.get(URL, headers =  HEADERS)
    soup = BeautifulSoup(page_to_scrape.content, "html.parser")
    soupPretty = BeautifulSoup(soup.prettify(), "html.parser")
    #the loop, runs until out of review pages
    while (nextLink["class"] != ['a-disabled', 'a-last']):
        #get reviews of current page
        reviews = soupPretty.find_all("span", {"class": "a-size-base review-text review-text-content"})
        for review in reviews:
            review = review.text #gets review text
            allReviews.append(review) #append to all reviews list
        #gets ratings of current page
        ratings = soupPretty.find_all("i", {"data-hook":["review-star-rating", "cmps-review-star-rating"]})
        for rating in ratings:
            str = rating.span.string #gets string "#.0 out of 5 stars"
            allRatings.append(int(str.split('.0')[0])) #appends rating number
    
        #gets url of next page
        nextLink = soupPretty.find("li", {"class": "a-last"})
        if(nextLink["class"] != ['a-disabled', 'a-last']):
            URL = "https://www.amazon.com/" + nextLink.a['href']
            #cooking soup for new page
            page_to_scrape = requests.get(URL, headers =  HEADERS)
            soup = BeautifulSoup(page_to_scrape.content, "html.parser")
            soupPretty = BeautifulSoup(soup.prettify(), "html.parser")
            nextLink = soupPretty.find("li", {"class": "a-last"})
            #print(nextLink["class"])

    #run last page
    for review in soupPretty.find_all('span', {"class": "a-size-base review-text review-text-content"}):
        review = review.text #gets review text
        allReviews.append(review) #append to all reviews list
        #gets ratings of current page
        ratings = soupPretty.find_all("i", {"data-hook":["review-star-rating", "cmps-review-star-rating"]})
    for rating in ratings:
        str = rating.span.string #gets string "#.0 out of 5 stars"
        allRatings.append(int(str.split('.0')[0])) #appends rating number

    dataFrame = pd.DataFrame({'rating': allRatings, 'comment': allReviews})
    dataFrame.comment = dataFrame.comment.apply(lambda x: re.sub(r"\s+", " ", x)).apply(lambda x: re.sub(r" The media could not be loaded. ", " ", x)).apply(lambda x : x.strip())

    #
    reviews = dataFrame
    reviews
    # turn comments into lower case, then tokenize them
    reviews['comment'] = reviews['comment'].astype('str').str.lower()
    reviews['text_token'] = list(map(word_tokenize, reviews.comment))
    reviews
    # remove words from tokenized array  if punctuation, or if it is negligible (of, the, because, etc)
    stopwords = nltk.corpus.stopwords.words("english")
    reviews['text_token'] = reviews['text_token'].apply(lambda x: [w for w in x if w.isalpha()])
    reviews['text_token'] = reviews['text_token'].apply(lambda x: [w for w in x if w not in stopwords])
    reviews

    #create a single string of each comment which contain only the words that are useful
    # then turn it into a variable that contains all remaining words
    reviews['text_string'] = reviews['text_token'].apply(lambda x: ' '.join([item for item in x if len(item)>2]))
    all_words = ' '.join([word for word in reviews['text_string']])
    reviews[['text_token', 'text_string']]

    # create a frequency distribution of all words that we will observe
    tokenized_words = nltk.tokenize.word_tokenize(all_words)
    fdist = FreqDist(tokenized_words)
    #alter this code so that it can limit df to words that appear >= 5 in all reviews
    reviews['text_string_fdist'] = reviews['text_token'].apply(lambda x: ' '.join([item for item in x if fdist[item] >= 1 ]))

    reviews
    # Lemmatize words to group similar words together (walking -> walk)
    wordnet_lem = WordNetLemmatizer()

    reviews['text_string_lem'] = reviews['text_string_fdist'].apply(wordnet_lem.lemmatize)
    # sees if any words were dropped from lemmatizer
    (reviews['text_string_fdist']==reviews['text_string_lem']).value_counts()

    # create a polarity for each lemmatized word list
    reviews['polarity'] = reviews['text_string'].apply(lambda x: SentimentIntensityAnalyzer().polarity_scores(x))

    if 'neu' in reviews.columns:
        reviews = pd.concat(
        [reviews.drop(['polarity', 'neg', 'neu', 'pos', 'compound'], axis=1), 
         reviews['polarity'].apply(pd.Series)], axis=1)
    else:
        reviews = pd.concat(
        [reviews.drop(['polarity'], axis=1), 
         reviews['polarity'].apply(pd.Series)], axis=1)


    reviews.head(3)

    # normalize sentiment scores to compare with reviews
    min_sentiment = min(reviews.compound)
    max_sentiment = max(reviews.compound)

    reviews.compound = reviews.compound.apply(lambda x : 1 + (x-min_sentiment) * (4)/(max_sentiment - min_sentiment) )
    return reviews

#%%
#sentiment analysis and return of data
def danial(reviews):
    
    
    fig = plt.figure()
    p1 = plt.hist(reviews.compound, bins = 15, alpha=0.5, label='Sentiment', edgecolor='blue')
    p1 = plt.hist(reviews.rating, bins = 15, alpha=0.5, label='Rating', edgecolor='orange')
    p1 = plt.xticks([1, 2, 3, 4, 5])
    plt.legend(loc='upper left')
    plt.tight_layout()
    return fig, np.mean(reviews.rating), np.mean(reviews.compound)


#%%
#violin plot
def danialTwo(reviews2):
    #plt.clf()
    fig = plt.figure()
    
    p1 = plt.xticks([1, 2, 3, 4, 5])
    #plt.legend(loc='upper left')
    plt.tight_layout()
    p1 = plt.violinplot([reviews2[reviews2.rating == 1].compound,
                reviews2[reviews2.rating == 2].compound,
                reviews2[reviews2.rating == 3].compound,
                reviews2[reviews2.rating == 4].compound,
                reviews2[reviews2.rating == 5].compound], 
                showmeans=True)
    return fig

#%%
def wong(reviews):
    
    all_words = ' '.join([word for word in reviews['text_string']])
    fig = plt.figure()
    tokenized_words = nltk.tokenize.word_tokenize(all_words)
    fdist = FreqDist(tokenized_words)
    fdist.plot(30)
   
    
    return fig
# %%
#gui
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")


root = customtkinter.CTk()
root.geometry("720x480")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20,padx=60, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text = "Amazon Review Judger", font=('Roboto', 40))
label.pack(pady=12,padx=18)
label.place(rely=.25, relx=0.175)

entryLink = customtkinter.CTkEntry(master=frame, width = 500, 
placeholder_text="Enter Amazon Product Link URL", justify=CENTER)
entryLink.pack(pady=12, padx=30)
entryLink.place(rely=.4,relx=.1)

def getLink(): 
    URL = entryLink.get()
    panda = thomas(URL)
    p1, rating_mean, sentiment_mean = danial(panda)

    

    #bar plot
    child_w = Toplevel(root)
    child_w.geometry("720x720")
    child_w.title("plot")
    chart_type = FigureCanvasTkAgg(p1,child_w)
    chart_type.get_tk_widget().pack(pady=50)
    rMeanLab = customtkinter.CTkLabel(master=child_w, text = "Customer Mean: " + str(rating_mean), pady=10, text_color='black')
    rMeanLab.pack()
    sMeanLab = customtkinter.CTkLabel(master=child_w, text = "Sentiment Mean: " + str(sentiment_mean)
    , pady=5, text_color = 'black')
    sMeanLab.pack()

    #violin plot
    fig = danialTwo(panda)
    child_z = Toplevel(root)
    child_z.geometry("720x720")
    child_z.title("plot 2")
    chart_type = FigureCanvasTkAgg(fig,child_z)
    chart_type.get_tk_widget().pack(pady=50)

    #word plot
    fig = wong(panda)
    child_x = Toplevel(root)
    child_x.geometry("720x720")
    child_x.title("plot 3")
    chart_type = FigureCanvasTkAgg(fig,child_x)
    chart_type.get_tk_widget().pack(pady=50)




enterButton = customtkinter.CTkButton(master=frame,text="Confirm",command=getLink)
enterButton.pack(pady=12, padx=10)
enterButton.place(rely=.525, relx=.375)




root.mainloop()
# %%
