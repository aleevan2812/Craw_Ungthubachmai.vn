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

# categoryUrl = 'https://ungthubachmai.vn/y-hoc-hat-nhan.html' #8 pages done 
# catid = 41

# categoryUrl = 'https://ungthubachmai.vn/gen-tri-lieu.html' # 9page done
# catid = 64

# categoryUrl = 'https://ungthubachmai.vn/ca-lam-sang.html' # 34page done
# catid = 128


categoryUrl = 'https://ungthubachmai.vn/dao-tao--nghien-cuu.html' # 17page error page12
catid = 76
# 
# categoryUrl = 'https://ungthubachmai.vn/ung-thu.html' # 112page done
# catid = 43
# 
# categoryUrl = 'https://ungthubachmai.vn/tu-van-benh-nhan.html' # 4page  done
# catid = 81

# categoryUrl = 'https://ungthubachmai.vn/tai-lieu-y-hoc-hat-nhan.html' # 1page  done
# catid = 132

# categoryUrl = 'https://ungthubachmai.vn/tin-tuc---su-kien.html' #103 pages done
# catid = 24

# categoryUrl = 'https://ungthubachmai.vn/kien-thuc-y-khoa.html' #13 pages done
# catid = 123

# categoryUrl = 'https://ungthubachmai.vn/xa-tri.html' #1 page  done
# catid = 47
# 
# categoryUrl = 'https://ungthubachmai.vn/dieu-tri-dich.html' # 3 pages 
# catid = 49
# # 
# categoryUrl = 'https://ungthubachmai.vn/dinh-duong-chung.html' # 4 pages 
# catid = 114
# # 
# categoryUrl = 'https://ungthubachmai.vn/tam-tinh-benh-nhan--thay-thuoc.html' #2 pages 
# catid = 127
# # 
# categoryUrl = 'https://ungthubachmai.vn/kien-thuc-co-ban.html' #9 pages 
# catid = 25
# 
# categoryUrl = 'https://ungthubachmai.vn/huong-dan-kham-chua-benh.html' # 1 page 
# catid = 100001
saveImagesPath = 'D:/Elcom/Test'


def getFullTextOnArtical(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.content
            # Sử dụng BeautifulSoup để phân tích cú pháp HTML
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.prettify()
    
            fullText = soup.find('div', class_='n-desc')
    
            imageTags = fullText.find_all('img')
            for imageTag in imageTags:
                # imageUrl = imageTag.get('src')
                imageUrl = imageTag['src']
                if ('http' in imageUrl) == False:
                    download_image('https://ungthubachmai.vn' + imageUrl, saveImagesPath)
                    download_image('https://ungthubachmai.com.vn' + imageUrl, saveImagesPath)
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
        catid = artical['catid']
        title = artical['title']
        introtext = artical['introtext']
        fulltext = artical['fulltext']
        picture = artical['picture']
        created = artical['created']
        alias = artical['alias']
    
        if(title == 'Nghiên cứu giá trị của PET/CT trong chẩn đoán bệnh ung thư đại trực tràng'):
            # Chả hiểu sao bài viết này k lưu được vào database, chắc fulltext dài quá hehe
            return
                
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
            "INSERT INTO [jos_k2_items] (catid,  title, introtext, fulltext, picture, created, alias, is_review) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            catid, title, introtext, fulltext, picture, created, alias, 1
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

    # Lấy nội dung HTML sau khi trang đã tải
    # content = driver.page_source
    articles = []
    # response = requests.get(content)

    # Sử dụng BeautifulSoup để phân tích cú pháp HTML
    # soup = BeautifulSoup(content, 'html.parser')
    i = 0
    while True:
        i = i + 1

        articleTags = driver.find_elements(By.CLASS_NAME, 'item-box')
        for articleTag in articleTags:
            title = articleTag.find_element(By.CLASS_NAME, 'n-title').find_element(By.TAG_NAME, 'a').get_attribute(
                'title')
            print(f'Handling - Page {i} -  {title}')
            introtext = articleTag.find_element(By.CLASS_NAME, 'n-desc').text
            
            pictureUrl = articleTag.find_element(By.TAG_NAME, 'img').get_attribute('src')
            picture = pictureUrl.split('/')[-1]
            
            articleUrl = articleTag.find_element(By.CLASS_NAME, 'n-title').find_element(By.TAG_NAME, 'a').get_attribute('href')
            
            createdText = articleTag.find_element(By.CLASS_NAME, 'n-title').find_element(By.CLASS_NAME, 'date').text
            created = convertTextToDate(createdText)
            
            alias = articleTag.find_element(By.TAG_NAME, 'img').get_attribute('alt')
            
            fullText = ''
            if (articleUrl is None) == False:                        
                fulltext = getFullTextOnArtical(articleUrl)
                fulltext = str(fulltext)

            download_image(pictureUrl, saveImagesPath)
            
            article = {'catid': catid,'title': title, 'introtext': introtext, 'fulltext': fulltext, 'picture': picture, 'created': created, 'alias': alias}
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


def main_for_CaLamSang():
    categoryUrl = 'https://ungthubachmai.vn/ca-lam-sang.html' # 34page done
    catid = 128
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
    i = 33
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, f'//a[@href="javascript:__doPostBack(\'ctl00$cphMain$ctl00$pager\',\'{i}\')"]'))
        # Thay bằng XPath của nút "a"
    )
    next_button.click()

    # Đợi trang tải lại dữ liệu
    time.sleep(2)  # Điều chỉnh thời gian chờ nếu cần
    
    while True:
        
        
        articleTags = driver.find_elements(By.CLASS_NAME, 'item-box')
        for articleTag in articleTags:
            title = articleTag.find_element(By.CLASS_NAME, 'n-title').find_element(By.TAG_NAME, 'a').get_attribute(
                'title')
            print(f'Handling - Page {i+1} -  {title}')
            introtext = articleTag.find_element(By.CLASS_NAME, 'n-desc').text

            pictureUrl = articleTag.find_element(By.TAG_NAME, 'img').get_attribute('src')
            picture = pictureUrl.split('/')[-1]

            articleUrl = articleTag.find_element(By.CLASS_NAME, 'n-title').find_element(By.TAG_NAME, 'a').get_attribute('href')

            createdText = articleTag.find_element(By.CLASS_NAME, 'n-title').find_element(By.CLASS_NAME, 'date').text
            created = convertTextToDate(createdText)

            alias = articleTag.find_element(By.TAG_NAME, 'img').get_attribute('alt')

            fullText = ''
            if (articleUrl is None) == False:
                fulltext = getFullTextOnArtical(articleUrl)
                fulltext = str(fulltext)

            download_image(pictureUrl, saveImagesPath)

            article = {'catid': catid,'title': title, 'introtext': introtext, 'fulltext': fulltext, 'picture': picture, 'created': created, 'alias': alias}
            saveArticalToDb(article)
            articles.append(article)
            print(f"Finished - Page {i+1} - {title}")

        i = i -1
        pri_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f'//a[@href="javascript:__doPostBack(\'ctl00$cphMain$ctl00$pager\',\'{i}\')"]'))
            # Thay bằng XPath của nút "a"
        )
        pri_button.click()

        # Đợi trang tải lại dữ liệu
        time.sleep(2)  # Điều chỉnh thời gian chờ nếu cần
    print(articles)

# main_for_CaLamSang()

