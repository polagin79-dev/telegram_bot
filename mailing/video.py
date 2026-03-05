import asyncio
import subprocess
import time
import os
import cv2
import ffmpeg
import shutil

from mydb.db_work import workDB, RandomVideo, MarkBIGVideo, MarkUnkownErr
from settings import Settings

idx = 0
maxsize = 50

def SplitVideo(name:str, sz:int, path_file):
        #print('SplitVideo: start')
        probe = ffmpeg.probe(name)
        duration = float(probe["format"]["duration"])
        count_part = int(sz/(maxsize-5))+1
        if count_part > 4:
                return "BIG"
        drtn = duration / count_part
        #ffmpeg -i video_5221532379_1.mp4 -c copy -map 0 -segment_time 00:00:20 -f segment output%03d.mp4
        #print('SplitVideo: start: делим ' + name + ' на ' + str(count_part) + ' частей')
        result = subprocess.run(['/usr/bin/ffmpeg', '-i', name, '-c', 'copy', '-map', '0', '-segment_time', str(drtn), '-f', 'segment', 'VIDEO/output%03d.mp4'], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if result.stdout.find('Error') == -1:
                #print('SplitVideo: успешное разбиение')
                p4 = None
                if os.path.exists('VIDEO/output003.mp4'):
                        p4 = ['NON', path_file[1], 'VIDEO/output003.mp4', path_file[2], None]
                p3 = None
                if os.path.exists('VIDEO/output002.mp4'):
                        p3 = ['NON', path_file[1], 'VIDEO/output002.mp4', path_file[2], p4]
                p2 = None
                if os.path.exists('VIDEO/output001.mp4'):
                        p2 = ['NON', path_file[1], 'VIDEO/output001.mp4', path_file[2], p3]
                p1 = None
                if os.path.exists('VIDEO/output000.mp4'):
                        p1 = ['NON', path_file[1], 'VIDEO/output000.mp4', path_file[2], p2]
                return p1
        else:
                #print('SplitVideo: не успешное разбиение')
                MarkUnkownErr(path_file[1], Settings.db_path, name_t)
                return None

def MakeRes(path_file):
        #print('MakeRes: start')
        #print('MakeRes: path_file=', path_file)
        res3 = None
        if path_file[3][2] != "NON":
                res3 = [path_file[3][2], path_file[1], '', path_file[2], None]
        res2 = None
        if path_file[3][1] != "NON":
                res2 = [path_file[3][1], path_file[1], '', path_file[2], res3]
        res1 = None
        if path_file[3][0] != "NON":
                res1 = [path_file[3][0], path_file[1], '', path_file[2], res2]
                
        res = [path_file[0], path_file[1], '', path_file[2], res1]     
        return res

def video_compress(get_random_file_video, dop_text:str, name_t:str):
        #print('video_compress: start')
        global idx
        idx = idx + 1
        name = 'VIDEO/video' + dop_text + '_' + str(idx) + '.mp4'
        while (os.path.exists(name)):
                idx = idx + 1
                name = 'VIDEO/video' + dop_text + '_' + str(idx) + '.mp4'
        for i in range(1, 11):
                path_file = get_random_file_video()
                if path_file != None:
                        vid = cv2.VideoCapture( path_file[2] )
                        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                        vid.release()
                        if (height > width):
                                dop_par = '404'
                        else:
                                dop_par = '718'
                #print('video_compress: i=', i)
                #print('video_compress: i=', i, ' path_file=', path_file)
                if path_file == None:                        
                        time.sleep(1)
                else:
                        if path_file[0] == 'NON':                                
                                #GetIdVideo(Settings.db_path, path_file, name)
                                #result = subprocess.run(['/usr/bin/ffmpeg', '-i', path_file[2], 'VIDEO/video' + dop_text + '.mp4'], encoding='utf-8', capture_output=True, text=True)
                                #result = subprocess.run(['/usr/bin/ffmpeg', '-i', path_file[2], name, '-b 1000k'], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                                #result = subprocess.run(['/usr/bin/ffmpeg', '-i', path_file[2], name], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                                #result = subprocess.run(['/usr/bin/ffmpeg', '-i', path_file[2], '-vf scale=' + dop_par + ':-1 -c:v libx265 -crf 28', name], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                                #result = subprocess.run(['/usr/bin/ffmpeg', '-i', path_file[2], '-vf scale=150:-1', '-c:v libx265', '-crf 28', name], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                                #result = subprocess.run(['/usr/bin/ffmpeg', '-i', path_file[2], '-vf', 'scale=' + dop_par + ':-1', '-c:v', 'libx265', '-crf', '28', name], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                                result = None
                                if (os.path.exists(path_file[2])):
                                        size = (os.path.getsize(path_file[2]))/(1024*1024)
                                if size >= maxsize:
                                        #print('video_compress: начали сжатие для id=', path_file[1], ' №', i)
                                        result = subprocess.run(['/usr/bin/ffmpeg', '-i', path_file[2], '-vf', 'scale=' + dop_par + ':-1', '-c:v', 'libx264', '-crf', '28', name], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                                else:
                                        shutil.copy(path_file[2], name)
                                        return [path_file[0], path_file[1], name, path_file[2], None]
                                #print('video_compress: result.stdout=', result.stdout)
                                if (os.path.exists(name)):
                                        size = (os.path.getsize(name))/(1024*1024)
                                else:                                        
                                        size = 0
                                #print('size=', size)
                                if (size < maxsize) and (result.stdout.find('Error') == -1):
                                        #print('video_compress: успешное сжатие')
                                        return [path_file[0], path_file[1], name, path_file[2], None]
                                elif size >= maxsize:
                                        #print('video_compress: ', result.stdout)
                                        #print('video_compress: сжатие для id=', path_file[1], '№', i, 'не удачное')
                                        #print('video_compress: помечаем в базе файл', path_file[2])
                                        result_split = SplitVideo(name, size, path_file)
                                        if result_split != None:
                                                #print('video_compress: успешное разбиение')
                                                return result_split
                                        elif result_split == "BIG":
                                                MarkBIGVideo(path_file[1], Settings.db_path, name_t)
                                                #print('video_compress: удаляем ', name)
                                                os.remove(name)
                                        else:#None
                                                pass
                                        #if result.stdout.find('Error') != -1:
                                        #        print(result.stdout)
                                        #        print("error=", result.stdout.find('Error'))
                                else:
                                        #print('video_compress: result.stdout=', result.stdout)
                                        MarkUnkownErr(path_file[1], Settings.db_path, name_t)
                        else:
                                #print('video_compress: есть id_telegram')
                                res = MakeRes(path_file)
                                return res
                                #return [path_file[0], path_file[1], '', path_file[2], None]
        return None

def delete_video_all():
        for root, dirnames, filenames in os.walk('VIDEO'):
                for filename in filenames:
                        os.remove(os.path.join(root, filename))

async def delete_video(path:str):
        await asyncio.sleep(10800) #3 часа
        os.remove(path)
                        
async def get_random_video(name:str, user = None):
        #print('get_random_video: start')
        if user != None:
                dop_text = "_" + str(user)
                if Settings.send_video.count(user) > 0:
                        return 'above the limit'
                Settings.send_video.append(user)
        else:
                dop_text = ""
        loop = asyncio.get_running_loop()
        #print(RandomVideo(Settings.db_path, 'случайное фото'))
        if user != None:
                user_name = Settings.users[str(user)]['name_btn']
        else:
                user_name = ''
        f=lambda : RandomVideo(Settings.db_path, name, user_name)
        future = loop.run_in_executor(None, video_compress, f, dop_text, name)
        await asyncio.sleep(1)
        result = await future
        #print('get_random_video: result=', result)
        if (result == None) and (user != None):
                Settings.send_video.remove(user)
                return None
        if result != None and result[2] != '':
                asyncio.create_task(delete_video(result[2]))
        if user in Settings.send_video:
                Settings.send_video.remove(user)        
        return result

async def work_get_video():
    await asyncio.sleep(7)    
    while (True):
        result = await get_video()
        #print(result[2])
        await asyncio.sleep(30)

async def test_main():
    task1 = work_get_video()
    task2 = workDB(Settings.db_path, Settings.sources)
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    asyncio.run(test_main())
