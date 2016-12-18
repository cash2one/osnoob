#-*-coding:utf-8-*-
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from uuid import uuid1
import time
from apps import config, mdb_sys
from apps.shared_tools.image.image_up import local_img_del

def rndChar():
    i = random.randint(1,3)
    if i == 1:
        an = random.randint(97, 122)
    elif i == 2:
        an = random.randint(65, 90)
    else:
        an = random.randint(48, 57)
    return chr(an)

#　干扰
def rnd_dis():
    d = ['^','-', '~', '_', '.']
    i = random.randint(0, len(d)-1)
    return d[i]

# 随机颜色1:
def rndColor():
    return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

# 随机颜色2:
def rndColor2():
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

def create_code():
    # 240 x 60:
    width = 60 * 4
    height = 60
    image = Image.new('RGB', (width, height), (192, 192, 192))
    # 创建Font对象:
    font = ImageFont.truetype('/etc/fonts/ARIAL.TTF', 36)
    # 创建Draw对象:
    draw = ImageDraw.Draw(image)
    # 填充每个像素:
    for x in range(0, width, 20):
        for y in range(0, height, 10):
            draw.point((x, y), fill=rndColor())
    # 输出文字:
    _str = ""
    for t in range(4):
        c = rndChar()
        _str = "{}{}".format(_str,c)
        h = random.randint(1, height-30)
        for j in range(0, width, 30):
            dis = rnd_dis()
            w = t*15 + j
            draw.text((w, h), dis, font=font, fill=rndColor())
        draw.text((60 * t + 10, h), c, font=font, fill=rndColor2())
    # 模糊:
    image.filter(ImageFilter.BLUR)
    code_url = 'ver_code/{}.jpg'.format(uuid1())
    save_dir = '{}/{}'.format(config['upload'].HOST, code_url)
    image.save(save_dir, 'jpeg')
    _code = {'url':code_url, 'str':_str, 'time':time.time()}
    mdb_sys.db.ver_code.insert(_code)
    _code.pop('_id')
    return _code

# ----------------------------------------------------------------------------------------------------------------------
def verify_code(code_url, code):
        _code = mdb_sys.db.ver_code.find_one({'url':code_url})
        r = False
        if _code:
            if code.lower() == _code['str'].lower() and time.time()-_code['time'] < 60*10:
                r = True
        return r

# ----------------------------------------------------------------------------------------------------------------------
def vercode_del(url):
    local_img_del(url)
    try:
        mdb_sys.db.ver_code.remove({'url':url})
    except:
        pass
