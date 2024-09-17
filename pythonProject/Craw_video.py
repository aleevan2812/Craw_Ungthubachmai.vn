import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import pyodbc
from urllib.parse import urlparse
from datetime import datetime

categoryUrl = 'https://ungthubachmai.vn/video-clip.html' #8 pages 
catid = 131

def saveArticalToDb(artical):
    try:
        catid = artical['catid']
        title = artical['title']
        video = artical['video']

        # server = 'AleeVan\\SQLEXPRESS'
        # database = 'Test_Python'
        # username = 'sa'
        # password = 'Alee123.'

        conn = pyodbc.connect(
            Trusted_Connection='Yes',
            Driver='{SQL Server}',
            Server='AleeVan\\SQLEXPRESS',
            Database='Ungthuba_Demo'
        )
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO [dbo].[jos_k2_items] (catid,  title,introtext, fulltext, video, trash, is_review) VALUES (?, ?, ?, ?, ?, ?, ?)",
            catid, title,title, title, video, 0, 1
        )

        conn.commit()
        cursor.close()
        conn.close()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lưu database: {e}")
def main():
    # Thiết lập trình duyệt (ở đây sử dụng Chrome)
    driver = webdriver.Chrome()

    # Tải trang web
    driver.get(categoryUrl)

    # Đợi một thời gian để trang web tải hoàn toàn
    time.sleep(5)

    # Lấy nội dung HTML sau khi trang đã tải
    # content = driver.page_source
    articles = []
    # response = requests.get(content)

    # Sử dụng BeautifulSoup để phân tích cú pháp HTML
    # soup = BeautifulSoup(content, 'html.parser')
    i = 0
    while True:
        i = i + 1

        articleTags = driver.find_elements(By.CLASS_NAME, 'gall-item')
        for articleTag in articleTags:
            title = articleTag.find_element(By.CLASS_NAME, 'gall-title').get_attribute('data-title')
            print(f'Handling - Page {i} -  {title}')
            
            video = articleTag.find_element(By.CLASS_NAME, 'gall-title').get_attribute('data-href')
            
            article = {'catid': catid,'title': title, 'video': video}
            saveArticalToDb(article)
            articles.append(article)
            print(f"Finished - Page {i} - {title}")


        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f'//a[@href="javascript:__doPostBack(\'ctl00$cphMain$ctl00$pager\',\'{i}\')"]'))
            # Thay bằng XPath của nút "a"
        )
        next_button.click()

        # Đợi trang tải lại dữ liệu
        time.sleep(2)  # Điều chỉnh thời gian chờ nếu cần
    print(articles)

main()

# main_for_CaLamSang()

