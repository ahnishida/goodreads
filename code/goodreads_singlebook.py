from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
import json


PATH = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(PATH)
#driver.get('https://www.goodreads.com/book/show/19351.The_Epic_of_Gilgamesh')
#clicks on screen to avoid popup
#driver.execute_script('el = document.elementFromPoint(0, 100); el.click();')



def get_bookSeries():
    try:
        bookSeries = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "bookSeries"))
            ).text
    except:
        bookSeries = ''
    return(bookSeries)

def get_bookAuthors():
    try:
        bookAuthors = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "bookAuthors"))
            )
        bookAuthors = bookAuthors.find_elements(
            By.XPATH, "//span[contains(@itemprop,'name')]")
        bookAuthors = (',').join([a.text for a in bookAuthors])
    except:
        bookAuthors = ''
    return(bookAuthors)

def get_bookMeta():
    try:
        bookMeta = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "bookMeta"))
            ).text.split(' ')
        bookMeta = [v.replace(',','') for v in bookMeta if v != '·' and v != '']
        bookMeta = [v for v in bookMeta if not v.isalpha()]
        return(bookMeta)
    except:
        return(['','',''])

def get_rating_distribution():
    try:
        rating_details_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Rating details"))
            )
        rating_details_link.click()
        rating_distribution = driver.find_element(
        By.XPATH, "//table[contains(@id,'rating_distribution')]")
        rating_distribution = rating_distribution.find_elements(By.TAG_NAME, "tr")
        star5, star4, star3, star2, star1 = (v.text.split(' ')[-1].strip('(').strip(')')
                                        for v in rating_distribution)
        return([star5, star4, star3, star2, star1])
    except:
        return(['','','','',''])

def get_numberOfPages():
    try:
        details = driver.find_element(By.ID, "details")
        numberOfPages = details.find_element(
            By.XPATH, "//span[contains(@itemprop,'numberOfPages')]").text

    except:
        numberOfPages = ''
    return(numberOfPages)

def get_originalPublicationYear():
    try:
        details = driver.find_element(By.ID, "details")
        publication_info = details.find_elements(By.CSS_SELECTOR,"*")[4].text
        years = re.findall('(-?[0-9]{3,4})',publication_info) #will capture BCE books
        originalPublicationYear = min(years)
    except:
        originalPublicationYear = ''
    return(originalPublicationYear)

def get_top10genres():
    try:
        top10genres = driver.find_elements(
            By.XPATH, "//a[contains(@class,'actionLinkLite bookPageGenreLink')]")
        top10genres = [v.text for v in top10genres]
    except:
        top10genres = ''
    return(top10genres)

def get_description():
    try:
        description = driver.find_element(By.ID, "description")
        description_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "...more"))
            )
        description_link.click()
        description = description.text
    except:
        description = ''
    return(description)


def bookDriver(bookid):
    print(bookid)
    driver.get('https://www.goodreads.com/book/show/' + str(bookid))
    #clicks on screen to avoid popup
    driver.execute_script('el = document.elementFromPoint(0, 100); el.click();')

    try:
        bookTitle = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "bookTitle"))
            ).text
    except:
    #return empty dataframe
        driver.quit()

    bookMeta = get_bookMeta()
    star5, star4, star3, star2, star1 = get_rating_distribution()
    bookData = {
    'bookid' : bookid,
    'bookSeries' : get_bookSeries(),
    'bookAuthors' : get_bookAuthors(),
    'ratingValue' : bookMeta[0],
    'ratingCount' : bookMeta[1],
    'reviewCount' : bookMeta[2],
    'ratingDistribution_star5' : star5,
    'ratingDistribution_star4' : star4,
    'ratingDistribution_star3' : star3,
    'ratingDistribution_star2' : star2,
    'ratingDistribution_star1' : star1,
    'numberOfPages' : get_numberOfPages(),
    'originalPublicationYear' : get_originalPublicationYear(),
    'get_top10genres' : get_top10genres(),
    'description' : get_description()
    }
    with open(f'records/{bookid}.{bookTitle}.json','w') as outfile:
        bookData = json.dump(bookData,outfile)

    return()


for id in range(1,10):
    try:
        bookDriver(id)
    except:
        continue
