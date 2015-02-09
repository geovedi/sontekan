
import fileinput
import codecs
from unidecode import unidecode
from bs4 import BeautifulSoup

if __name__ == '__main__':
    with codecs.open('output.txt', 'w', 'utf-8') as out:
        title = None
        for line in fileinput.input():
            line = line.decode('utf-8')
            soup = BeautifulSoup(line)
            if line.startswith('<doc'):
                try:
                    title = soup.find_all('doc')[0].attrs['title']
                except:
                    pass
            for link in soup.find_all('a'):
                link_attrs, link_text = None, None
                try:
                    link_attrs = link.attrs['href']
                    link_text = link.contents[0]
                except:
                    pass
                if title and link_attrs and link_text:
                    out.write(u'{0} | {1} | {2}\n'.format(title, link_attrs, link_text))
