# -*- coding: utf-8 -*-
import expanddouban
from bs4 import BeautifulSoup
import time
import csv
from collections import Counter


"""
return a string corresponding to the URL of douban movie lists given category and location.
"""
def getMovieUrl(category, location):
    url = 'https://movie.douban.com/tag/#/?sort=S&range=9,10&tags=电影,{},{}'.format(category, location)
    return url


"""
return a list of Movie objects with the given category and location. 
"""
class Movie():
    def __init__(self, movie_name, movie_rate, movie_location, movie_category, info_link, cover_link):
        self.name = movie_name
        self.rate = movie_rate
        self.location = movie_location
        self.category = movie_category
        self.link = info_link
        self.cover = cover_link
       
    #for test
    #def make_readable(self):
        #return self.name, self.rate, self.location, self.category, self.link, self.cover
        
def getMovies(category, location):
    url = getMovieUrl(category, location)
    html = expanddouban.getHtml(url, loadmore=True, waittime=3) # get HTML by the given url
    soup = BeautifulSoup(html, "html.parser")
    target_content = soup.find(id="content").find(class_="list-wp").find_all("a", recursive=False)
    
    movie_list = []
    for c in target_content:
        t = c.find(class_="title").string
        #check if rate is None, replace with '0'
        r = '0'
        if c.find(class_="rate").string != None:
            r = c.find(class_="rate").string        
        h = c.get("href")
        i = c.find("img").get("src")
        movie = Movie(t, r, location, category, h, i)
        movie_list.append(movie)            
    return movie_list


"""
output movie data of all categories and locations to "moives.csv"
"""
def writeCsv(category, location):
    movie_list = getMovies(category, location)
    with open('movies.csv', 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter='|', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        for movie in movie_list:
            #replace comma with hyphen in movie title and set object to list
            writer.writerow([movie.name.replace(',','-') +","+ movie.rate +","+ movie.location +","+ movie.category +","+ movie.link +","+ movie.cover])


#get the category tags of genre and location
category_list=[] 
location_list=[]

def writeByCategory():
    html = expanddouban.getHtml("https://movie.douban.com/tag/#/?sort=S&range=9,10&tags=电影", loadmore=False)
    soup = BeautifulSoup(html, 'html.parser')
    target_content = soup.find(id='content').find(class_='tags').find(class_='category').next_sibling

    for c in target_content:
        category = c.find(class_='tag').string
        if category != '全部类型':
            category_list.append(category)   
    for c in target_content.next_sibling:
        location = c.find(class_='tag').string
        if location != '全部地区':
            location_list.append(location)
            
    #output to csv by category tags
    for category in category_list:
        for location in location_list:
            writeCsv(category, location)


writeByCategory()


"""
output calculated results to "output.txt"
"""
with open('movies.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    movie_list = list(reader)
    

with open('output.txt', 'w', newline='', encoding='utf-8-sig') as f:
    for category in category_list:
        singleCategoryList=[]
        for item in movie_list:
            if item[3] == category:
                singleCategoryList.append(item)

        locationCount = Counter()
        for item in singleCategoryList:
            locationCount[item[2]] += 1
        locationCount = dict(locationCount)
        categoryTotal = sum(locationCount.values()) #either way: categoryTotal = len(singleCategoryList)
 
        for k, v in locationCount.items():
            locationCount[k] = round((v/categoryTotal*100),2)
            locationPercent = sorted(locationCount.items(),key = lambda x:x[1],reverse = True)
            
        text = "{}类，数量排名前三的地区及占比为：{}，{}%；{}，{}%；{}，{}%。\n".format(category, locationPercent[0][0], locationPercent[0][1], locationPercent[1][0], locationPercent[1][1], locationPercent[2][0], locationPercent[2][1])
        
        f.write(text)