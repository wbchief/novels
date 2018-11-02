import json
import os
import re
import shutil
from zipfile import ZipFile


class SaveEpub:

    def __init__(self, title='bai', author=None):
        '''

        :param title: 书名
        :param author: 作者
        '''

        self.title = title
        self.author = author
        self.path = '/home/chief/python/novels/tmp'
        self.ebook_address = '/home/chief/python/novels/ebooks/'
        self.htmllist = list(filter(lambda x: '.html' in x, os.listdir(self.ebook_address)))
        self.htmllist.sort(key=lambda x: int(re.match('\d+', x).group()))



    def create_mimetype(self):
        '''
        创建mimetype文件
        :return:
        '''


        if not os.path.exists(self.path):
            os.mkdir(self.path)
        with open('{}/mimetype'.format(self.path), 'w') as f:
            f.write('application/epub+zip')



    def create_meta_type(self):
        '''
        它的功能是告诉阅读器电子书根文件路径以及打开方式，
        如果你修改了content.opf的名字或者把它放在其他位置，应该写明完整的路径。
        :return:
        '''

        if not os.path.exists('{}/META-INF'.format(self.path)):
            os.mkdir('{}/META-INF'.format(self.path))

        with open('{}/META-INF/container.xml'.format(self.path), 'w') as f:
            f.write('''<container version="1.0"><rootfiles><rootfile full-path="OPS/fb.opf"
                    media-type="application/oebps-package+xml"/></rootfiles></container>
                    ''')


    def create_OPS(self):
        '''
        创建ops文件
        :return:
        '''

        if not os.path.exists('{}/OPS'.format(self.path)):
            os.mkdir('{}/OPS'.format(self.path))

        if os.path.isfile('cover.jpg'):  # 如果有cover.jpg, 用来制作封面
            shutil.copyfile('cover.jpg', '{}/OPS/cover.jpg'.format(self.path))
            print('Cover.jpg found!')

        opfcontent = '''<?xml version="1.0" encoding="UTF-8" ?>
        <package version="2.0" unique-identifier="PrimaryID" xmlns="http://www.idpf.org/2007/opf">
        <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        %(metadata)s
        <meta name="cover" content="cover"/>
        </metadata>
        <manifest>
        %(manifest)s
        <item id="ncx" href="content.ncx" media-type="application/x-dtbncx+xml"/>
        <item id="cover" href="cover.jpg" media-type="image/jpeg"/>
        </manifest>
        <spine toc="ncx">
        %(ncx)s
        </spine>
        </package>
        '''

        dc = '<dc:%(name)s>%(value)s</dc:%(name)s>'
        item = "<item id='%(id)s' href='%(url)s' media-type='application/xhtml+xml'/>"
        itemref = "<itemref idref='%(id)s'/>"

        metadata = '\n'.join([
            dc % {'name': 'title', 'value': self.title},
            dc % {'name': 'creator', 'value': self.author},
        ])

        manifest = []
        ncx = []

        for htmlitem in self.htmllist:
            content = open(self.ebook_address + htmlitem, 'r').read()
            tmpfile = open('{}/OPS/{}'.format(self.path, htmlitem), 'w')
            tmpfile.write(content)
            tmpfile.close()
            manifest.append(item % {'id': htmlitem, 'url': htmlitem})
            ncx.append(itemref % {'id': htmlitem})

        manifest = '\n'.join(manifest)
        ncx = '\n'.join(ncx)

        tmpfile = open('{}/OPS/content.opf'.format(self.path), 'w')
        tmpfile.write(opfcontent % {'metadata': metadata, 'manifest': manifest, 'ncx': ncx, })
        tmpfile.close()

        ncx = '''<?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
        <ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
        <head>
          <meta name="dtb:uid" content=" "/>
          <meta name="dtb:depth" content="-1"/>
          <meta name="dtb:totalPageCount" content="0"/>
          <meta name="dtb:maxPageNumber" content="0"/>
        </head>
         <docTitle><text>%(title)s</text></docTitle>
         <docAuthor><text>%(creator)s</text></docAuthor>
        <navMap>
        %(navpoints)s
        </navMap>
        </ncx>
        '''

        navpoint = '''<navPoint id='%s' class='level1' playOrder='%d'>
        <navLabel> <text>%s</text> </navLabel>
        <content src='%s'/></navPoint>'''

        navpoints = []

        chapter = {}  # 存放读取的数据
        with open("chapter.json", 'r', encoding='utf-8') as json_file:
            chapter = json.load(json_file)
        #print(chapter)
        for i, htmlitem in enumerate(self.htmllist):
            navpoints.append(navpoint % (htmlitem, i + 1, chapter.get(str(i+1)), htmlitem))
        os.remove('chapter.json')
        tmpfile = open('{}/OPS/content.ncx'.format(self.path), 'w')
        tmpfile.write(ncx % {
            'title': self.title,
            'creator': self.author,
            'navpoints': '\n'.join(navpoints)})
        tmpfile.close()


    def save(self):

        epubfile = ZipFile('../{}.epub'.format(self.title), 'w')
        os.chdir(self.path)
        for d, ds, fs in os.walk('.'):
            for f in fs:
                epubfile.write(os.path.join(d, f))
        epubfile.close()
        print('OK')
        shutil.rmtree(self.ebook_address)
        shutil.rmtree(self.path)


    def main(self):
        '''

        :return:
        '''
        self.create_mimetype()
        self.create_meta_type()
        self.create_OPS()
        self.save()



if __name__ == '__main__':
    epub = SaveEpub()
    epub.main()