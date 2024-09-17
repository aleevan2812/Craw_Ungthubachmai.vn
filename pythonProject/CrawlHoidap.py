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


categoryUrl = 'https://ungthubachmai.vn/hoi-dap-chuyen-gia.html' # 1 page 
catid = 133
saveImagesPath = 'D:/Elcom/Test'


def getFullTextOnArtical(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.content
            # Sử dụng BeautifulSoup để phân tích cú pháp HTML
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.prettify()

            fullText = soup.find('div', class_='faq-desc')
                    
            return fullText
        return ''
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy fulltext: {e}")
        return ''

def download_image(url, base_save_path):
    try:
        # Phân tích URL
        if 'data' in url:
            print(f"Ảnh base64 - Url: {url}")
            return
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.lstrip('/').split('/')

        # Đường dẫn lưu ảnh (không bao gồm tên file)
        save_path = os.path.join(base_save_path, *path_parts[:-1])

        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Tên file
        file_name = path_parts[-1]

        # Đường dẫn đầy đủ để lưu file
        full_path = os.path.join(save_path, file_name)

        # Tải file từ URL
        response = requests.get(url)
        if response.status_code == 200:
            with open(full_path, 'wb') as file:
                file.write(response.content)
            print(f"Ảnh đã được tải về và lưu tại: {full_path}")
        else:
            print(f"Không thể tải ảnh. Mã trạng thái HTTP: {response.status_code} - Url: {url}")
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tải ảnh: {e}")


def saveArticalToDb(artical):
    try:
        title = artical['title']
        introtext = artical['introtext']
        fullname = ''
        address = ''
        email = ''
        phonenumber = ''
        question = artical['title']
        answer = artical['answer']

        conn = pyodbc.connect(
            Trusted_Connection='Yes',
            Driver='{SQL Server}',
            Server='AleeVan\\SQLEXPRESS',
            Database='Test_Python'
        )
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO [jos_k2_qa] (title,  introtext, fullname, address, email, phonenumber, question, answer) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            title,  introtext, fullname, address, email, phonenumber, question, answer
        )

        conn.commit()
        cursor.close()
        conn.close()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lưu database: {e}")

def convertTextToDate(date_string):
    # Tách phần ngày từ chuỗi
    date_part = date_string.split(": ")[1]

    # Chuyển đổi thành đối tượng datetime
    date_object = datetime.strptime(date_part, "%d/%m/%Y")

    # Chuyển đổi thành định dạng YYYY-MM-DD
    formatted_date = date_object.strftime("%Y-%m-%d")
    return formatted_date

def main():
    # Thiết lập trình duyệt (ở đây sử dụng Chrome)
    driver = webdriver.Chrome()

    # Tải trang web
    driver.get(categoryUrl)

    # Đợi một thời gian để trang web tải hoàn toàn
    time.sleep(5)
    

    articleTags = driver.find_elements(By.CLASS_NAME, 'faq-item')
    i = 0
    for articleTag in articleTags:
        i = i+1
        title = articleTag.find_element(By.TAG_NAME, 'h3').text
        print(f'Handling - Page {i} -  {title}')
        introtext = articleTag.find_element(By.CLASS_NAME, 'faq-desc').text

        articleUrl = articleTag.find_element(By.CLASS_NAME, 'faq-title').find_element(By.TAG_NAME, 'a').get_attribute('href')
        answer = ''
        if (articleUrl is None) == False:
            answer = getFullTextOnArtical(articleUrl)
            answer = str(answer)

        article = {'title': title, 'introtext': introtext, 'answer': answer}
        saveArticalToDb(article)
        print(f"Finished - Page {i} - {title}")
    print("THE END")

main()


# CREATE TABLE jos_k2_qa (
#     id INT IDENTITY(1,1) PRIMARY KEY,
# title NVARCHAR(255),
# introtext NVARCHAR(MAX),
# fullname NVARCHAR(255),
# address NVARCHAR(255),
# email NVARCHAR(255),
# phonenumber NVARCHAR(255),
# question NVARCHAR(MAX),
# answer NVARCHAR(MAX)
# );
