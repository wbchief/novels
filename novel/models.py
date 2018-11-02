from novel import db


class Novels(db.Model):
    '''
    ebook表
    '''

    __tablename__ = 'novels'
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(64), index=True)#书名
    author = db.Column(db.String(64), index=True)#作者
    image = db.Column(db.String(64))# 书封面
    last_update = db.Column(db.String(64))# 最后更新时间
    about_book = db.Column(db.Text) #  简介
    book_url = db.Column(db.String(128)) #书链接
    search_name = db.Column(db.String(64))
    chapter = db.relationship('Chapter', backref='novel', lazy='dynamic')
    fonts = db.Column(db.String(24))
    status = db.Column(db.String(32))
    flag = db.Column(db.Integer)

    def __repr__(self):
        return '<Novel %r>' % self.book_name
    # def __init__(self, data):
    #     self.book_name = data['book_name']
    #     self.author = data['author']
    #     self.image = None
    #     self.last_update = data['last_since']
    #     self.new_chapter = data['new_chapter']
    #     self.about_book = data['about_book']
    #     self.book_url = data['book_url']
    #     self.search_name = data['search_name']


class Chapter(db.Model):
    '''
    章节表
    chapter_num=0,代表最新章节
    '''
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    chapter_name = db.Column(db.String(128))# 章节名
    chapter_url = db.Column(db.String(128))#章节url
    chapter_number = db.Column(db.Integer, index=True)
    # 外键
    book_id = db.Column(db.Integer, db.ForeignKey('novels.id'))
    chapter_content = db.relationship('Content', backref='chapter', lazy='dynamic')

    def __repr__(self):
        return '<chapter %r>' % self.chapter_name


class Content(db.Model):
    '''
    章节内容
    '''
    __tablename__ = 'contents'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))

