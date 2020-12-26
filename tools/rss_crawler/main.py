from bs4 import BeautifulSoup

xml_doc = """
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">
<author>
<name>Blog lists</name>
</author>
<id>좋은 블로그</id>
<title>Korea Blogs</title>
<updated>2020-12-26T00:30:00+09:00</updated>
<entry>
<author>
<name>홍길동</name>
</author>
<id>https://readmoa.net/foo</id>
<link href="https://readmoa.net/foo"/>
<summary><!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd"> <html><body><p>테스트</p></body></html> </summary>
<title>테스트 제목</title>
<updated>2020-12-22T16:33:00+09:00</updated>
<dc:date>2020-12-22T16:33:00+09:00</dc:date>
</entry>
"""
# Requirement: pip install lxml
soup = BeautifulSoup(xml_doc, "lxml")

print(soup.prettify())
