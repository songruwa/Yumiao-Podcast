import csv
import os
import re
from lxml import etree
import requests
import time

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
}

categories_to_scrap = ["评书", "人文", "国学", "头条", "投资理财", "健康", "影视", "商业管理", "科技"]


def extract_links(html):
    tree = etree.HTML(html)
    a_elements = tree.xpath('//div[@class="wrapper first q_X"]/a')
    links = [(a.get('href'), a.text) for a in a_elements if a.text in categories_to_scrap] # Only select the required categories
    return links

url = 'https://www.ximalaya.com/channel/'
response = requests.get(url, headers=header)
html = response.text
start_urls = extract_links(html)

def getAllpage(url, category):
    print(f"\n>>>>> Scraping Category: {category} <<<<<\n")  # To indicate which category is being scraped
    r = requests.get(url, headers=header)
    html = r.text
    result = re.findall(r'<li class="page-item y_J".*?><a class="page-link y_J".*?><span>(.*?)</span>', html, re.S)
    result=int(result[-1])
    url_list = []
    for i in range(1,result+1):
        if i==1:
            url_list.append(url)
        else:
            second_url=url+'p{}/'.format(i)
            url_list.append(second_url)

    for i in range(1,result):
        if i == 2:
            break

        print(">>>开始爬取第{}页".format(i))
        url=url_list[i-1]
        r=requests.get(url,headers=header)
        response=etree.HTML(r.text)
        time.sleep(0.1)
        allFM=response.xpath('//*[@id="award"]/main/div[1]/div[3]/div[2]/ul/li')

        # Open a new file for this category to record the sequence of files
        sequence_file = open(os.path.join('/Users/wsr/Desktop/Yumiao/JunxuanGuo/', category, 'sequence.txt'), 'w')
        audio_count = 1  # Initialize a counter to keep track of the number of audios scraped


        # 之后换成[25: larger number]
        for i in allFM[:25]:
            item={}
            item['title']=i.xpath(" div / a / span/text()")[0]
            item['author'] = i.xpath(" div/a[2]/text()")[0]
            item['playback'] = i.xpath("div/div/a/p/span/text()")[0]
            item['href'] = "https://www.ximalaya.com"+i.xpath("div/div/a/@href")[0]

            GetFM_Music(item['href'], change_title(item['title']), item['author'], category, sequence_file, audio_count)  # Pass category, sequence_file, and audio_count to the function
            print(item)

            audio_count += 1
        # Close the sequence file when done with this category
        sequence_file.close()

def GetFM_Music(href, title, author, category, sequence_file, audio_count):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
    }

    r = requests.get(href, headers=header)
    if r.status_code != 200:
        print(f"Failed to fetch the page: {href}")
        return

    response = etree.HTML(r.text)

    sound_nodes = response.xpath('//li[@class="b_t"]/div[@class="text b_t"]/a/@to')
    if sound_nodes:
        sound_id = sound_nodes[0].replace('https://www.ximalaya.com/sound/', '')
        print("Sound id: " + sound_id)
    else:
        print('No sound id found in the given href')
        return

    src = 'https://www.ximalaya.com/revision/play/v1/audio?id=' + sound_id + '&ptype=1'
    print("Source url is "+str(src))
    r=requests.get(src,headers=header)
    pattern1 = r'"src":"([^"]+)"'
    match = re.search(pattern1, r.text)
    if match:
        src_value = match.group(1)
        print('音频文件地址',src_value)

        foldername = '/Users/wsr/Desktop/Yumiao/JunxuanGuo/' + category
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        
        # Write the title of the audio file to the sequence file, along with its sequence number
        sequence_file.write(f'{audio_count}. {title}- {author} - {category}\n')

        # Build the file path and check if the file already exists
        filepath = os.path.join(foldername, f'{title}- {author} - {category}.m4a')
        if os.path.exists(filepath):
            print(f"The file {filepath} already exists. Skipping download.")
            return

        response = requests.get(url=src_value, headers=header).content
        with open(filepath, mode='wb') as file:
            file.write(response)


    else:
        print('没有vip，无法下载')


def change_title(title):
    pattern = re.compile(r"[\/\\\:\*\?\"\<\>\|]")  
    new_title = re.sub(pattern, "_", title)
    return new_title

if __name__ == '__main__':
    for start_url, category in start_urls:
        getAllpage("https://www.ximalaya.com" + start_url, category)



