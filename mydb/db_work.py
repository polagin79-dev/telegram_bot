import asyncio
import sqlite3
from datetime import datetime, date
#import fnmatch
import time
import os
import random
from PIL import Image
import math

from settings import Settings
from tools.save import save_error

prop_db = {}

flag_updatedb = False

#test_flag = False

def checkUpdateDB(db_path:str):
    #print('checkUpdateDB: start')
    #return True
    global flag_updatedb
    if os.path.exists(db_path):
        mtime_readable = datetime.fromtimestamp(os.path.getmtime(db_path))
        #print(type(mtime_readable))
        dt_now = datetime.now()
        diff = (dt_now.date() - mtime_readable.date()).days
        upd = diff > 30
        upd = upd and (dt_now.hour > 1) and (dt_now.hour < 3)
        upd = upd or flag_updatedb
        #print('checkUpdateDB: flag_updatedb=', flag_updatedb)
        flag_updatedb = False
        if upd:
            #print('checkUpdateDB: будем обновлять базу')
            return True
        else:
            #print('checkUpdateDB: обновление базы не требуется')
            return False
    else:
        return True

def NewNameDB(db_path:str):
    n=db_path.rfind(".")
    db_path_new = ".".join([db_path[0:n], "new", db_path[n+1:]])
    return db_path_new

def CreateChildTable(cursor):
    s = '''
CREATE TABLE IF NOT EXISTS picture (
id INTEGER PRIMARY KEY,
id_path INTEGER,
name_file TEXT NOT NULL,
id_telegram TEXT DEFAULT "NON",
id_telegram2 TEXT DEFAULT "NON",
id_telegram3 TEXT DEFAULT "NON",
id_telegram4 TEXT DEFAULT "NON",
bad_label TEXT DEFAULT NULL,
FOREIGN KEY (id_path)  REFERENCES path (id) ON DELETE CASCADE ON UPDATE CASCADE
)
'''
    cursor.execute(s)
    s = '''
CREATE TABLE IF NOT EXISTS video (
id INTEGER PRIMARY KEY,
id_path INTEGER,
name_file TEXT NOT NULL,
id_telegram TEXT DEFAULT "NON",
id_telegram2 TEXT DEFAULT "NON",
id_telegram3 TEXT DEFAULT "NON",
id_telegram4 TEXT DEFAULT "NON",
bad_label TEXT DEFAULT NULL,
FOREIGN KEY (id_path)  REFERENCES path (id) ON DELETE CASCADE ON UPDATE CASCADE
)
'''
    cursor.execute(s)

def FillChildTable(cursor, source:str, user_btn:str, private:int):
    id_pic = 0;
    id_video = 0;
    for root, dirnames, filenames in os.walk(source, followlinks=True):
        cursor.execute('''INSERT INTO path ( path_file, user, private) VALUES (?,?,?)''', (root,user_btn,private))
        id = cursor.lastrowid
        #if private == 1:
        #    print('FillChildTable: source=', source)
        #    print('FillChildTable: id=', id)
        for filename in filenames:
            #if private == 1:
            #    print('FillChildTable: filename=', filename)
            if filename.endswith((".jpg",".JPG")):
                cursor.execute('INSERT INTO picture (id_path, name_file) VALUES (?, ?)', (id, filename))
                id_pic = cursor.lastrowid
            if filename.endswith((".mov", ".MOV", ".mpg", ".MPG", ".mpeg", ".MPEG", ".mp4", ",MP4")):
                cursor.execute('INSERT INTO video (id_path, name_file) VALUES (?, ?)', (id, filename))
                id_video = cursor.lastrowid
        id +=1

def FillTable(db_path:str, sources:dict):
    db_path_new = NewNameDB(db_path)
    db_path_new = os.path.abspath(db_path_new)
    if os.path.exists(db_path_new):
        os.remove(db_path_new)
    connection = sqlite3.connect(db_path_new)
    #conn = sqlite3.connect(":memory:")
    cursor = connection.cursor()
    cursor.execute("BEGIN TRANSACTION")
    cursor.execute('''
CREATE TABLE IF NOT EXISTS path (
id INTEGER PRIMARY KEY,
path_file TEXT NOT NULL,
user TEST NOT NULL,
private INTEGER NOT NULL
)
''')
    for key, val in sources.items():
        CreateChildTable(cursor)
        #CreateChildTable(cursor, val['name_tbl'] + '_video')
        #CreateChildTable(cursor, val['name_tbl'] + '_private')
        #CreateChildTable(cursor, val['name_tbl'] + '_video_private')
        FillChildTable(cursor, val['path'], key.lower(),0)
        FillChildTable(cursor, val['path_private'], key.lower(), 1)
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
    return db_path_new

def MoveDataToNewDB(db_path:str, db_path_new:str, sources:dict):
    #print('MoveDataToNewDB: start')
    conn_old = sqlite3.connect(db_path)
    conn_new = sqlite3.connect(db_path_new)
    cursor_old = conn_old.cursor()
    cursor_new = conn_new.cursor()
    cursor_new.execute("BEGIN TRANSACTION")
    for name_t in ['picture', 'video']:
        #name_t = val['name_tbl'] + dop
        #query = 'SELECT ' + name_t + '.id, ' + name_t + '.id_telegram FROM path, ' + name_t + ' WHERE (path.id = ' + name_t + '.id_path)'
        query = 'SELECT ' + name_t + '.id, ' + name_t + '.id_telegram, ' + name_t + '.id_telegram2, ' + \
                name_t + '.id_telegram3, ' + name_t + '.id_telegram4, path.id, path.path_file, ' + name_t + '.name_file FROM path, ' + \
                name_t + ' WHERE ((path.id = ' + name_t + '.id_path) AND (' + name_t + '.id_telegram != "NON"))'
        cursor_old.execute(query)
        rows_old = cursor_old.fetchall()
        for row in rows_old:
            query = 'SELECT ' + name_t + '.id FROM path, ' + \
                    name_t + ' WHERE ((path.id = ' + name_t + '.id_path) AND (' + name_t + '.name_file == "' + row[7] + \
                    '") AND (path.path_file == "' + row[6] + '"))'
            cursor_new.execute(query)
            rows_new = cursor_new.fetchall()
            if len(rows_new)>0:
                id_new = rows_new[0][0]
                query = 'UPDATE ' + name_t + ' SET id_telegram="' + row[1] + '", ' + \
                        'id_telegram2="' + row[2] + '", ' + 'id_telegram3="' + row[3] + '", ' + \
                        'id_telegram4="' + row[4] + '" WHERE id=' + str(id_new)
                cursor_new.execute(query)        
    conn_new.commit()
    conn_old.commit()
    conn_new.close()
    conn_old.close()
    return

def UpdateDB(db_path:str, sources:dict):
    #print('UpdateDB: обновление базы начато ', datetime.now())
    db_path_new = FillTable(db_path, sources)
    if os.path.exists(db_path):
        MoveDataToNewDB(db_path, db_path_new, sources)
        #print('UpdateDB: перемещение завершено')

def CreateProp(db_path:str, sources:dict):
    global prop_db
    if prop_db:
        return
    prop_db = dict(sources)

async def workDB(db_path:str, sources:dict):
    while (True):
        if checkUpdateDB(db_path):
            loop = asyncio.get_running_loop()
            future = loop.run_in_executor(None, UpdateDB, db_path, sources)
            await asyncio.sleep(1)
            result = await future
            #print('workDB: обновление завершено')
            if os.path.exists(db_path):
                os.remove(db_path)
                #print('workDB: текущая база удалена')
            db_path_new = NewNameDB(db_path)
            db_path_new = os.path.abspath(db_path_new)
            os.rename(db_path_new, db_path)
            CreateProp(db_path, sources)
            #print('workDB: введена в работу новая база ', datetime.now())
        else:
            CreateProp(db_path, sources)
        await asyncio.sleep(600)

def GetIdVideo(db_path:str, path_file:str, user_btn:str):
    if not prop_db:
        return None
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    #name_t = prop_db[name.lower()]['name_tbl']
    query = 'SELECT video.id_telegram FROM path, video WHERE (path.user = ' + user_btn.lower() + ') and (path.id = video.id_path)and(path_file||''/''||name_file = ' + path_file + ')'
    cursor.execute(query)
    result = cursor.fetchone()
    connection.commit()
    connection.close()
    if result:
        result[0]
    return None

def RemoveFromDB(db_path:str, path_file:str, user_btn:str):
    if not prop_db:
        return None
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    #name_t = prop_db[name.lower()]['name_tbl']
    query = 'SELECT picture.id, picture.id_telegram FROM path, picture WHERE (path.user = ' + user_btn.lower() + ') and (path.id = picture.id_path)and(path_file||''/''||name_file = ' + path_file + ')'
    cursor.execute(query)
    result = cursor.fetchone()
    if not result:
        return
    query = 'DELETE FROM ' + name_t + 'where ' + name_t + '.id = ' + str(result[0])
    cursor.execute(query)
    connection.commit()
    connection.close()

def SetIdPict(id_telegram:int, id_pict:int, user_btn:str):
    connection = sqlite3.connect(Settings.db_path)
    cursor = connection.cursor()
    #name_t = prop_db[name.lower()]['name_tbl']
    query = 'UPDATE picture SET id_telegram = "' + str(id_telegram) + '" WHERE id = ' + str(id_pict)
    #print(query)
    cursor.execute(query)
    connection.commit()
    connection.close()

def MarkBIGVideo(id_video:int, db_path:str, user_btn:str):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    query = 'UPDATE video SET bad_label = "BIG" WHERE id = ' + str(id_video)
    cursor.execute(query)
    connection.commit()
    connection.close()

def MarkUnkownErr(id_video:int, db_path:str, user_btn:str):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    query = 'UPDATE video SET bad_label = "UNKERR" WHERE id = ' + str(id_video)
    cursor.execute(query)
    connection.commit()
    connection.close()

def delete_picture_all():
    for root, dirnames, filenames in os.walk('PICTURE'):
                for filename in filenames:
                        os.remove(os.path.join(root, filename))

async def delete_picture(path:str):
    #await asyncio.sleep(10800) #3 часа
    await asyncio.sleep(1800) #30 минут
    os.remove(path)

def ReduceImage(file_path:str, w:int, h:int):
    #print('ReduceImage: start')
    r = w * h
    im = Image.open(file_path)
    width, height = im.size
    if width < w and height < h:
        return file_path
    k = width/height
    height = math.sqrt(r/k)
    width = k * height
    
    im.thumbnail((width,height), Image.Resampling.LANCZOS)
    name = os.path.basename(file_path)
    file, ext = os.path.splitext(name)
    file_path_new = 'PICTURE/' + file + '.verysmall' + ext    
    im.save(file_path_new, "JPEG")
    asyncio.create_task(delete_picture(file_path_new))
    #im.save(file + '.small.jpg', "JPEG", quality=100)
    return file_path_new

def CheckPictureAndCorrection(file_path:str):
    #print('CheckPicture: start')
    #Проверим размер ширина+высота < 10000
    size = (os.path.getsize(file_path))/(1024*1024)
    try:
        im = Image.open(file_path)
    except Exception as e:
        msg = str(e)
        save_error("ошибка в CheckPictureAndCorrection: "+msg)
        return 0
    width, height = im.size
    k = width/height
    h = 10000/(k+1)
    w = h*k
    if ((width + height) > 10000) or (size >50):
        #print('CheckPicture: ширина + высота > 10000 w=', width, ' h=', height, '\nили '\
        #      'размер больше 50Mb size=', size)
        im.thumbnail((w,h), Image.Resampling.LANCZOS)
        name = os.path.basename(file_path)
        file, ext = os.path.splitext(name)
        file_path_new = 'PICTURE/' + file + '.small' + ext
        im.save(file_path_new, "JPEG")
        asyncio.create_task(delete_picture(file_path_new))
        #im.save(file + '.small.jpg', "JPEG", quality=100)
    ratio = width/height
    if (ratio > 20 )or(ratio < 1/20):
        #print('CheckPicture: ширина и высота отличаются более чем в 20 раз')
        return None
    return file_path

def RandomPicture(user_btn:str, user=''):
    #print('RandomPicture: start')
    global flag_updatedb
    #global test_flag
    if not prop_db:
        return None
    connection = sqlite3.connect(Settings.db_path)
    cursor = connection.cursor()
    if user_btn.lower() == user.lower():
        private = ''
    else:
        private = ' and (path.private = 0)'
    #name_t = prop_db[name.lower()]['name_tbl']
    for i in range(1, 100):
        query = 'SELECT path_file, name_file, picture.id, picture.id_telegram FROM path, picture WHERE (picture.bad_label is NULL)' + \
                ' and (path.id = picture.id_path) and (path.user = "' + user_btn.lower() + '") ' + private
        #query = 'SELECT path_file, name_file, ' + name_t + '.id, ' + name_t + '.id_telegram FROM path, ' + name_t + ' WHERE (' + name_t + '.bad_label is NULL) and (path.id = ' + name_t + '.id_path)and(' + name_t + '.id = 170)' #182#3
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            break
        number = random.randint(1, len(rows))
        id = 1
        for row in rows:
            if id == number:
                break
            id = id + 1
        path = "/".join([row[0], row[1]])
        path_orig = path
        if os.path.exists(path):
            if row[3] == 'NON':
                path = CheckPictureAndCorrection(path)
                if path == None:
                    query = 'UPDATE picture SET bad_label = "PHOTO_INVALID_DIMENSIONS" WHERE id = ' + str(row[2])
                    cursor.execute(query)
                elif path == 0:
                    query = 'UPDATE picture SET bad_label = "PIL.UNIDENTIFIEDIMAGEERROR" WHERE id = ' + str(row[2])
                    cursor.execute(query)
                else:
                    #asyncio.create_task(delete_picture(path))
                    break
        else:
            flag_updatedb = True
            query = 'DELETE FROM picture WHERE id = ' + str(row[2])
            cursor.execute(query)
    connection.commit()
    #query = 'SELECT id_path, name_tbl, id_file, id_t FROM path, ' + name_t + ',  WHERE (path.id = ' + name_t + '.id_path)'
    connection.close()
    if rows:
        #if test_flag:
            result = [row[3], row[2], path, path_orig]
        #else:
            #result = ['awdfsd', row[2], path]
    else:
        result = None
    #test_flag = True
    #print('RandomPicture: return file ', result)
    return result

def SetIdVideo(id_telegram:int, id_video:int, user_btn:str, number:int):
    #print('SetIdVideo: id=', id_video)
    connection = sqlite3.connect(Settings.db_path)
    cursor = connection.cursor()
    if number == 1:
        query = 'UPDATE video SET id_telegram = "' + str(id_telegram) + '" WHERE id = ' + str(id_video)
    else:
        query = 'UPDATE video SET id_telegram' + str(number) + ' = "' + str(id_telegram) + '" WHERE id = ' + str(id_video)
    #print(query)
    cursor.execute(query)
    connection.commit()
    connection.close()

def RemoveIdPicture(id_pict:int, user_btn:str):
    #print('RemoveIdPicture: id=', id_pict)
    connection = sqlite3.connect(Settings.db_path)
    cursor = connection.cursor()
    #name_t = prop_db[name.lower()]['name_tbl']
    query = 'UPDATE picture SET id_telegram = "NON" WHERE id = ' + str(id_pict)
    cursor.execute(query)
    connection.commit()
    connection.close()

def RemoveIdVideo(id_video:int, user_btn:str):
    #print('RemoveIdVideo: id=', id_video)
    connection = sqlite3.connect(Settings.db_path)
    cursor = connection.cursor()
    query = 'UPDATE video SET id_telegram = "NON" WHERE id = ' + str(id_video)
    cursor.execute(query)
    connection.commit()
    connection.close()

def RandomVideo(db_path:str, user_btn:str, user=''):
    global flag_updatedb
    #global test_flag
    if not prop_db:
        return None
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    if user_btn.lower() == user.lower():
        private = ''
    else:
        private = ' and (path.private = 0)'
    for i in range(1, 50):
        #query = 'SELECT path_file, name_file, ' + name_t + '.id, ' + name_t + '.id_telegram FROM path, ' + name_t + ' WHERE (' + name_t + '.bad_label is NULL) and (path.id = ' + name_t + '.id_path)'
        #query = 'SELECT path_file, name_file, ' + name_t + '.id, ' + name_t + '.id_telegram, ' + name_t + '.id_telegram2, ' + \
        #        name_t + '.id_telegram3, ' + name_t + '.id_telegram4 ' + \
        #         ' FROM path, ' + name_t + ' WHERE (' + name_t + '.bad_label is NULL) and (path.id = ' + name_t + '.id_path)and(' + name_t + '.id = 1)' #1571#180#9#408 #12 #509
        query = 'SELECT path_file, name_file, video.id, video.id_telegram, video.id_telegram2, ' + \
                'video.id_telegram3, video.id_telegram4 ' + \
                 ' FROM path, video WHERE (video.bad_label is NULL) and (path.id = video.id_path) and (path.user = "' + user_btn.lower() + '") ' + private #1571#180#9#408 #12 #509
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            break
        number = random.randint(1, len(rows))
        id = 1
        for row in rows:
            if id == number:
                break
            id = id + 1
        path = "/".join([row[0], row[1]])
        if os.path.exists(path):
            break
        else:
            flag_updatedb = True
            query = 'DELETE FROM video WHERE id = ' + str(row[2])
            cursor.execute(query)
    connection.commit()
    connection.close()
    if rows:
        #if test_flag:
        result = [row[3], row[2], path, [row[4], row[5], row[6]]]
        #else:
            #result = ['vggsartg', row[2], path]
    else:
        result = None
    #test_flag = True
    return result
    
async def test_workDB():
    while (True):
        print("делаем разную работу")
        if len(prop_db) > 0:
            print("случайная картинка:")
            print(RandomPicture(Settings.db_path, "случайное фото"))
            print("случайное видео:")
            print(RandomVideo(Settings.db_path, "случайное фото"))
        await asyncio.sleep(3)

async def test_main():
    sources={
        "случайное фото":{
            'name_tbl':'picture',
            'path':'SOURCE/RANDOM_FOTO'},
        "максим":{
            'name_tbl':'maksim',
            'path':'SOURCE/МАКСИМ'},
        "катя":{
            'name_tbl':'katya',
            'path':'SOURCE/КАТЯ'},
        "рома":{
            'name_tbl':'roma',
            'path':'SOURCE/РОМА'}
        }
    task1 = test_workDB()
    task2 = workDB(Settings.db_path, sources)
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    asyncio.run(test_main())
