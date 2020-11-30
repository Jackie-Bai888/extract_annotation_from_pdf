## 介绍  
### 你是否还在为 获取不到自己在pdf中做了注释的单词而苦恼？？  
### 你是否还因为 想记却记不住文献中的陌生单词而苦恼？？  
### 别慌，你的救星来啦。
本项目是获取在pdf中标注了注释的单词以及对应的注释，目前实现的获取的注释类型只有下划线。将单词以及注释保存到txt文本中，然后将单词导入到背单词软件中就可以背诵了(这里推荐墨墨背单词)

## 代码文件为extracting_word_from_pdf.py
# Install
1.安装PyPDF4
pip install PyPDF4  
[GitHub Pages](https://pages.github.com/)  
2.安装PyMuPDF  
pip install PyMuPDF  
3.申请百度云文字识别应用(因为谷歌Tesseract-OCR识别不准)  
(1)登录百度智能云,选择用户中心,选择文字识别   
![文字识别](https://github.com/xiaobailearn/extract_annotation_from_pdf/blob/main/%E6%96%87%E5%AD%97%E8%AF%86%E5%88%AB.png)  
(2)创建应用，创建好后记住应用的API Key和Secret Key，在之后请求文字识别接口要用到  
![文字识别](https://github.com/xiaobailearn/extract_annotation_from_pdf/blob/main/%E4%BF%AE%E6%94%B9id.png)

# Note
1.getting_word_from_pdf.py中的PDF_PATH、PDF_FILE_NAME、SAVE_WORD_FILE 需要替换成自己的  
![文字识别](https://github.com/xiaobailearn/extract_annotation_from_pdf/blob/main/%E8%B7%AF%E5%BE%84.png)
2.host中需要将client_id替换成应用的API Key，将client_secret替换成Secret Key
