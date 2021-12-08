from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
import json
import os

PATH = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(PATH)

def get_listLinks(tag,max_page):
    #navigates to book lists by as tag (ie fantasy, nonfiction)
    #download names of book lists for specified number of pages
    tag_lists = []
    for page in range(1,max_page+1):
        driver.execute_script('el = document.elementFromPoint(0, 100); el.click();')
        driver.get(f'https://www.goodreads.com/list/tag/{tag}?page={page}')
        driver.execute_script('el = document.elementFromPoint(0, 100); el.click();')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME,'listTitle'))
            )
        driver.execute_script('el = document.elementFromPoint(0, 100); el.click();')
        listTitles = driver.find_elements(By.CLASS_NAME,'listTitle')
        listTitles = [element.get_attribute('href').split('/')[-1] for element in listTitles]
        listTitles = [element for element in listTitles if re.search(tag,element.lower())]
        tag_lists = tag_lists + listTitles
    listdf = pd.DataFrame(tag_lists,columns =['listTitle'])
    listdf.to_csv('data/'+tag+'_lists.tsv',sep='\t',index=False)
#get_listLinks('fantasy',5)


def books_on_page(pageLink):
    #extracts title, author, link and rating info for all 100 books on a list page
    driver.get(pageLink)
    allBooks = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'all_votes'))
        )
    driver.execute_script('el = document.elementFromPoint(0, 100); el.click();')
    bookTitles = allBooks.find_elements(By.XPATH,"//a[contains(@class,'bookTitle')]")
    titles = [title.text for title in bookTitles]
    authorNames = allBooks.find_elements(By.XPATH,"//a[contains(@class,'authorName')]")
    authors = [author.text for author in authorNames]
    links = [title.get_attribute('href') for title in bookTitles]
    ratings = allBooks.find_elements(By.XPATH,"//span[contains(@class,'greyText smallText uitext')]")
    ratings = [rating.text for rating in ratings]
    ave_ratings = [re.findall(r'([0-9.]+) avg rating',v)[0] for v in ratings]
    no_ratings = [re.findall(r'([0-9(?,)]+) rating',v)[0] for v in ratings]
    df = pd.DataFrame(list(zip(titles, authors, ave_ratings, no_ratings,links)),
                   columns =['title', 'author', 'ave_rating','no_rating','link'])
    return(df)

def get_books_on_list(listTitle):
    #interates through pages of a book list scraping book info and outputs df
    listStartPage = f'https://www.goodreads.com/list/show/{listTitle}'
    driver.get(listStartPage)
    driver.execute_script('el = document.elementFromPoint(0, 100); el.click();')
    pagination =  driver.find_element(By.CLASS_NAME,'pagination')
    paginationLinks = pagination.find_elements(By.TAG_NAME,'a')
    maxPageNum = int(paginationLinks[-2].text)
    listPageLinks = [listStartPage + '?page=' + str(v) for v in range(1,maxPageNum+1)]
    book_dfs = [books_on_page(pageLink) for pageLink in listPageLinks]
    book_dfs_merged = pd.concat(book_dfs)
    book_dfs_merged.to_csv(f'data/lists/{listTitle}.tsv',sep='\t',index=False)

#get_books_on_list('88.Best_Fantasy_Books_of_the_21st_Century')

def download_books_lists_for_tag(tag,maxPageNum):
    #gets book lists and s
    get_listLinks(tag,maxPageNum)
    listdf = pd.read_csv(f'data/{tag}_lists.tsv',sep='\t')
    todo_lists = set(listdf['listTitle'])
    print(len(todo_lists))
    dn_lists = set([f.split('.tsv')[0] for f in os.listdir('data/lists')])
    todo_lists = todo_lists - dn_lists
    print(len(todo_lists))
    for listTitle in todo_lists:
        print(listTitle)
        try:
            get_books_on_list(listTitle)
            print("SUCCESS")
        except:
            print("ERROR")
            continue

#download_books_lists_for_tag('fantasy',6)
download_books_lists_for_tag('nonfiction',3)
driver.quit()
