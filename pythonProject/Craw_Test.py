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

# categoryUrl = 'https://ungthubachmai.vn/y-hoc-hat-nhan.html' #done 
# cartid = 41

# categoryUrl = 'https://ungthubachmai.vn/gen-tri-lieu.html' # 9page done
# cartid = 64

# categoryUrl = 'https://ungthubachmai.vn/ca-lam-sang.html' # 34page done
# cartid = 128

# categoryUrl = 'https://ungthubachmai.vn/dao-tao--nghien-cuu.html' # 17page error page12
# cartid = 76

categoryUrl = 'https://ungthubachmai.vn/ung-thu.html' # 117page
cartid = 43

# categoryUrl = 'https://ungthubachmai.vn/tu-van-benh-nhan.html' # 4page done
# cartid = 81

saveImagesPath = 'D:/Elcom/Test'


def getFullTextOnArtical(url):
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


# def download_image_2(image_url, save_path):
#     try:
#         if ('http' in image_url) == False:
#             image_url = 'https://ungthubachmai.vn' + fullImageUrl
#         # Gửi yêu cầu HTTP GET để tải ảnh
#         response = requests.get(image_url)
#         response.raise_for_status()  # Kiểm tra xem yêu cầu có thành công không
# 
#         # Lấy tên file từ URL
#         image_name = os.path.basename(image_url)
# 
#         # Tạo đường dẫn lưu ảnh
#         save_full_path = os.path.join(save_path, image_name)
# 
#         # Lưu ảnh vào đường dẫn đã chỉ định
#         with open(save_full_path, 'wb') as file:
#             file.write(response.content)
# 
#         print(f"Ảnh đã được tải về và lưu tại: {save_full_path}")
#     except requests.exceptions.RequestException as e:
#         print(f"Lỗi khi tải ảnh: {e}")


def download_image(url, base_save_path):
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


def saveArticalToDb(artical):
    cartid = artical['cartid']
    title = artical['title']
    introtext = artical['introtext']
    fulltext = artical['fulltext']
    picture = artical['picture']

    server = 'AleeVan\\SQLEXPRESS'
    database = 'Test_Python'
    username = 'sa'
    password = 'Alee123.'

    # conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    conn = pyodbc.connect(
        Trusted_Connection='Yes',
        Driver='{SQL Server}',
        Server='AleeVan\\SQLEXPRESS',
        Database='Test_Python'
    )
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO [jos_k2_items] (cartid,  title, introtext, fulltext, picture) VALUES (?, ?, ?, ?, ?)",
        cartid, title, introtext, fulltext, picture
    )

    conn.commit()
    cursor.close()
    conn.close()


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
        if i == 92:
            articleTags = driver.find_elements(By.CLASS_NAME, 'item-box')
            for articleTag in articleTags:
                title = articleTag.find_element(By.CLASS_NAME, 'n-title').find_element(By.TAG_NAME, 'a').get_attribute(
                    'title')
                print(f'Handling - Page {i} -  {title}')
                introtext = articleTag.find_element(By.CLASS_NAME, 'n-desc').text
                pictureUrl = articleTag.find_element(By.TAG_NAME, 'img').get_attribute('src')
                path_index = pictureUrl.find("/", len("https://"))
                picture = pictureUrl[path_index:]
    
                articleUrl = articleTag.find_element(By.CLASS_NAME, 'n-title').find_element(By.TAG_NAME, 'a').get_attribute('href')
                fulltext = getFullTextOnArtical(articleUrl)
                fulltext = str(fulltext)
    
                download_image(pictureUrl, saveImagesPath)
    
                article = {'cartid': cartid,'title': title, 'introtext': introtext, 'fulltext': fulltext, 'picture': picture}
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



