import os
from flask import Flask, url_for, render_template, redirect, session, flash, request
from forms import UploadForm
from werkzeug import secure_filename

app = Flask(__name__)

# 为程序设置密钥
app.secret_key = os.getenv('SECRET_KEY', 'secret string')

# 上传文件存储路径
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')

# 请求数据（上传文件大小）最大限制为1G，超过此限制返回413错误响应
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  

class Experiment:
    """实验"""
    def __init__(self, id, name, request, content):
        """初始化
        :param id: 实验编号
        :param name: 实验名称
        :param request: 实验要求
        :param content: 提交内容
        """
        self.id = id
        self.name = name
        self.request = request
        self.content = content

def init_info():
    """初始信息"""
    experiments = []
    experiment1 = Experiment(id=1, name="实验一 音频采集与处理", 
        request="用录音机录制一首自己唱的歌或朗诵，准备一段背景音乐，并合成录制的声音文件和背景音乐。",
        content="背景音乐文件、声音文件、合成作品、实验报告（电子版+打印版）。")
    experiments.append(experiment1)
    experiment2 = Experiment(id=2, name="实验二 图像处理", 
        request="（1）选取适当的图片素材和世界地图，运用各种选取方法制作一幅由世界名胜照片揉和在一起的背景。利用图层效果制作一幅有地形质感的世界地图。调整并合并所有层存储为各种图像文件格式并压缩。 \
        （2）显示一个bmp文件的程序，并实现图像亮度、对比度调整、图像平移、放大、旋转和镜像。",
        content="图片素材、合成图片、显示bmp的程序代码、显示bmp的可执行文件、实验报告（电子版+打印版）。")
    experiments.append(experiment2)
    experiment3 = Experiment(id=3, name="实验三 动画制作", 
        request="根据实验1中得到的歌曲或配乐朗诵，做一段Flash不少于1分半钟，并合成为一段动画MV。",
        content="动画素材、Flash源文件、Flash导出影片、实验报告（电子版+打印版）。")
    experiments.append(experiment3)
    experiment4 = Experiment(id=4, name="实验四 网站制作", 
        request="个人页面开发，包含个人基本信息，整个课程的各次实验信息，并实现媒体文件上传、下载功能实现。",
        content="网页制作素材、网页源代码、实验报告（电子版+打印版）。")
    experiments.append(experiment4)
    return experiments

experiments = init_info()   # 四次实验的信息

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html', experiments=experiments)

@app.route('/experiment/<int:id>', methods=['GET', 'POST'])
def experiment(id):
    upload_form = UploadForm()
    if upload_form.validate_on_submit():
        f = upload_form.file.data                   # 上传的文件

        # 修改了secure_filename源码以支持中文，否则secure_filename()会过滤掉中文，只剩下扩展名
        # 参考：https://blog.csdn.net/qq_30490489/article/details/92000197
        filename = secure_filename(f.filename)      # 文件名

        # 存储到上传路径
        experiment_name = 'experiment' + str(id)    # 本实验名, eg.'experiment1'
        experiment_path = os.path.join(app.config['UPLOAD_PATH'], experiment_name)  # 本实验上传路径
        f.save(os.path.join(experiment_path, filename)) # 存储上传文件

        flash('Upload success.')

        session['filename'] = [filename]

        return redirect(url_for('experiment', id=id))

    return render_template('experiment.html', experiment=experiments[id-1], upload_form=upload_form)