from flask import Blueprint
from flask import flash
from flask import render_template
from flask import url_for
from sqlalchemy import and_
from sqlalchemy import or_
from werkzeug.utils import redirect

from novel import create_app, db
from novel.main.form import SearchForm
from novel.models import Novels, Chapter, Content
from novel.novelSpider.ebookSpider import EBook

main = Blueprint('main', __name__)

@main.route('/', methods=['POST', 'GET'])
@main.route('/index', methods=['POST', 'GET'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        name = form.name.data
        print('搜索成功')
        flash('搜索成功')
        return redirect(url_for('main.result', search=name))

    return render_template('index.html', form=form)


def gave(chapters):
    '''
    分组
    :return:
    '''

    count = 4
    i = 0
    number = len(chapters)
    degree = int(number/count)
    #print(number)
    temp = []
    while i < degree*count:
        temp.append(chapters[i:i+count])
        i += count
    temp.append(chapters[i:])
    #print(len(temp))
    return temp




@main.route('/result/<search>')
def result(search):
    books = Novels.query.filter(or_(Novels.search_name==search, Novels.book_name==search)).all()
    print(books)
    if books:
        datas = []
        for book in books:
            temp = {'book_name': book.book_name, 'book_url': book.book_url,
                    'author': book.author, 'font': book.fonts,
                    'time': book.last_update, 'statu': book.status}
            chapter = Chapter.query.filter_by(book_id=book.id, chapter_number=0).first()
            if chapter:
                temp['new_chapter'] = chapter.chapter_name
                temp['new_chapter_url'] = chapter.chapter_url
                temp['book_id'] = chapter.book_id
            datas.append(temp)
        return render_template('results.html', datas=datas, search=search)


    spider = EBook()
    temp_datas = spider.get_book_result(search)
    datas = []
    for data in temp_datas:
        print(data)
        novels = Novels(book_name=data['book_name'],
                        author=data['author'],
                        last_update=data['time'],
                        book_url=data['book_url'],
                        fonts=data['font'],
                        status=data['statu'],
                        search_name=search,
                        flag=0
                        )
        db.session.add(novels)
        db.session.commit()

        book = Novels.query.filter_by(search_name=search, book_name=data['book_name']).first()
        print(book)
        chapter = Chapter(chapter_name=data.get('new_chapter'),
                          chapter_url=data.get('new_chapter_url'),
                          chapter_number=0,
                          book_id=book.id)
        db.session.add(chapter)
        db.session.commit()
        data['book_id'] = book.id
        datas.append(data)
    return render_template('results.html', datas=datas, search=search)

@main.route('/book/<int:book_id>')
def book(book_id):
    '''

    :param name:
    :return:
    '''
    book = Novels.query.filter_by(id=book_id).first()
    print(book)
    print(book.flag)
    if not book.flag:
        ebook = EBook()
        datas, about_book, image = ebook.get_chapters_url(book.book_url)
        for data in datas:
            chapter = Chapter(chapter_name=data.get('chapter_name'),
                              chapter_url=data.get('chapter_url'),
                              chapter_number=data.get('chapter_number'),
                              book_id=book.id)
            db.session.add(chapter)
            db.session.commit()
        Novels.query.filter_by(id=book.id).update({'about_book': about_book, 'flag': 1, 'image': image})
        db.session.commit()
        chapters = Chapter.query.filter(and_(Chapter.book_id==book.id, Chapter.chapter_number>0)).all()
        chapters = gave(chapters)
        return render_template('book.html', book=book, chapters=chapters)

    print('sql')
    chapters = Chapter.query.filter(and_(Chapter.book_id == book.id, Chapter.chapter_number > 0)).all()
    chapters = gave(chapters)
    return render_template('book.html', book=book, chapters=chapters)


@main.route('/content/<int:book_id>/<int:chapter_number>')
def content(book_id, chapter_number):
    '''

    :param chapter_id :有book_id 和chapter_number组成
    :return:
    '''
    print(book_id)
    print(chapter_number)
    # 查询章节
    chapter = Chapter.query.filter_by(book_id=book_id, chapter_number=chapter_number).first()
    # 查询内容
    content = Content.query.filter_by(chapter_id=chapter.id).first()
    # 查询上一章，下一章
    count = Chapter.query.filter(and_(Chapter.chapter_number>0,
                                                 Chapter.book_id==book_id)).count()
    if content:
        return render_template('content.html', content=content, chapter=chapter, count=count)

    url = chapter.chapter_url
    spider = EBook()
    chapter_content = spider.get_chapter_content(url)
    content = Content(content=chapter_content,
                      chapter_id=chapter.id)
    db.session.add(content)
    db.session.commit()
    return render_template('content.html', content=content, chapter=chapter)




if __name__ == '__main__':
    app = create_app('testing')
    app.run(host='0.0.0.0', port='9999')
