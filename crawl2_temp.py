import requests
from bs4 import BeautifulSoup

# Tải nội dung của trang web
url = 'https://ungthubachmai.vn/ca-lam-sang.html'
response = requests.get(url)

# Kiểm tra xem yêu cầu có thành công không
if response.status_code == 200:
    content = response.content
    # Sử dụng BeautifulSoup để phân tích cú pháp HTML
    soup = BeautifulSoup(content, 'html.parser')
    # print(soup.prettify())

    content = soup.prettify()
    tags = soup.find_all('div', class_ = 'n-title');
    print(tags)