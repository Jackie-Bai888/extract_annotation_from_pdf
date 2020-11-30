import base64
import copy
import glob
import os
import time
from io import open

import fitz
import requests
from PyPDF4 import PdfFileReader, PdfFileWriter
import shutil

PDF_PATH = r'C:\Users\btt07\Documents\学习\文献\目标识别'  #要读取的pdf的路径
PDF_FILE_NAME = 'CornerNet-Lite Efficient Keypoint-Based.pdf'  #要读取的pdf文件
SAVE_WORD_FILE = 'word2.txt'   #要存放word的文件以及路径
#用PyPDF4进行读取文件
def read_pdf_use_pydpf():
    '''
    读取pdf，将pdf的mediabox设置为注释框的大小
    :return: 注释内容
    '''
    print('------start read pdf------')
    pdf_file_path = PDF_PATH + '\\' + PDF_FILE_NAME
    anno_ls = []  # 记录注释内容
    with open(pdf_file_path, 'rb') as f:
        pdf = PdfFileReader(f)
        pdf_output = PdfFileWriter()
        number_of_pages = pdf.getNumPages()
        for i in range(number_of_pages):
            page = pdf.getPage(i)
            try:
                annots = page['/Annots']
                for annot in annots:
                    '''
                    拷贝page对象为一个新对象，不然每次都会修改page，从而影响下次的执行
                    因为page包含了io.TextIOWrapper，所以无法进行深度复制
                    '''
                    annot_page = copy.copy(page)
                    if annot.getObject()['/Subtype'] == '/Underline':
                        #以下的坐标为一个注释对应一条下划线，如果一个注释对应多条或者对应的是换行的一条的话 将获取不到该单词
                        quad_point = annot.getObject()['/QuadPoints']
                        print(quad_point)
                        if(len(quad_point)<=8):
                            anno_ls.append(annot.getObject()['/Contents'])
                            print(anno_ls)
                            up_l_x, up_l_y, up_r_x, up_r_y, low_l_x, low_l_y, low_r_x, low_r_y = annot.getObject()['/QuadPoints']
                            print(up_l_x, up_l_y, up_r_x, up_r_y, low_l_x, low_l_y, low_r_x, low_r_y)
                            '''
                            mediaBox#对于要修改的mediaBox，需要进行深度复制，不然会影响page的mediaBox
                            拷贝page和深度拷贝mediaBox 缺一不可
                            '''
                            box = copy.deepcopy(annot_page.mediaBox)
                            box.lowerLeft = (low_l_x, low_l_y)
                            box.lowerRight = (low_r_x, low_r_y)
                            box.upperLeft = (up_l_x, up_l_y)
                            box.upperRight = (up_r_x, up_r_y)
                            annot_page.mediaBox = box
                            pdf_output.addPage(annot_page)
            except:
                # there are no annotations on this page
                pass
        pdf_output.write(open('mediabox.pdf', 'wb'))
    print('------finish read pdf------')
    return anno_ls

def pdf_to_img(pdfPath=None):
    '''
    该方法是将pdf转换为img
    这样做是因为如果用读pdf的工具包，读到的内容仍然为pdf整个文本的内容，不是mediabox的内容，所以要将其展示给user的media box转为图片
    :param pdfPath:如果之后需要调用该方法且传递参数的话会方便一些
    '''
    print('------start transform pdf to img------')
    pdfPath = 'mediabox.pdf'
    imagePath = 'img'
    pdfDoc = fitz.open(pdfPath)
    for pg in range(pdfDoc.pageCount):
        page = pdfDoc[pg]
        rotate = int(0) #旋转度数
        # 每个尺寸的缩放系数为2，提高分辨率，使图片最短边>15px 才能达到百度接口的识别要求
        # 此处若是不做设置，默认图片大小为：792X612, dpi=72
        zoom_x = 2  # (1.33333333-->1056x816)   (2-->1584x1224)
        zoom_y = 2
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)

        if not os.path.exists(imagePath):  # 判断存放图片的文件夹是否存在
            os.makedirs(imagePath)  # 若图片文件夹不存在就创建
        print('creat_'+str(pg)+'.png')
        pix.writePNG(imagePath+'/'+'images_%s.png' % pg)  # 将图片写入指定的文件夹内

    print('------finish transform pdf to img------')

def get_words_from_img():
    '''
    该函数是调用百度通用文字识别接口进行文字识别(从图片中识别单词)
    host中的client_id是文字识别应用中的API Key，client_secret是文字识别中的Secret Key(自己要提前申请文字识别应用)
    :return:单词列表
    '''
    print('------start get words from img------')
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=**&client_secret=**'
    response = requests.get(host) #获取token
    words = []
    if response:
        access_token = response.json()['access_token']
        '''
        通用文字识别
        '''
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        # 二进制方式打开图片文件
        ls = glob.glob('img/*.png')
        img_name_list = sorted(ls, key=lambda name: int(name.split('.png')[0][11:]))
        num = 0 #因为qps最高只能为2，所以就用num统计次数，如果是2的倍数就sleep 1s
        for img in img_name_list:
            f = open(img, 'rb')
            img = base64.b64encode(f.read())
            params = {"image": img}
            # access_token = ''
            request_url = request_url + "?access_token=" + access_token
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(request_url, data=params, headers=headers)
            if response:
                word = response.json()['words_result'][0]['words']
                words.append(word)
            num += 1
            if num % 2 == 0:
                time.sleep(1)
    print('------finish get words from img------')
    return words


def save_word(anno_ls=None, word_ls=None):
    '''
    将单词和注释相匹配
    :param anno_ls:注释列表，和单词列表的index是相对应的
    :param word_ls:单词列表
    '''
    print('------start save words to txt------')
    with open(SAVE_WORD_FILE,'w') as f:
        for num, word in enumerate(word_ls):
            f.write(word+' '+anno_ls[num])
            f.write('\n')
    print('------finish save words to txt------')


def del_redundant_file():
    '''
    将所有的过度文件进行删除,给人一种中间无任何输出的感觉
    '''
    print('------start delete redundant file------')
    folder = 'img' #要删除的目录
    shutil.rmtree(folder)
    os.remove('./mediabox.pdf')
    print('------end delete redundant file------')

if __name__ == '__main__':
    anno_ls = read_pdf_use_pydpf()
    pdf_to_img()
    word_ls = get_words_from_img()
    print('anno_ls', end='')
    print(anno_ls)
    print('word_ls', end='')
    print(word_ls)
    save_word(anno_ls,word_ls)
    del_redundant_file()

