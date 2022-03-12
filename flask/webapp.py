from crypt import methods
from flask import Flask, render_template, Response, session, redirect, url_for, request
import cv2
import time
from wtforms import Form, BooleanField, StringField, validators, SubmitField, RadioField, SelectField, TextAreaField
from wtforms.validators import DataRequired, StopValidation
from flask_wtf import FlaskForm


class VideoCamera(object):
    def __init__(self):# 通過opencv獲取實時影片流
        self.video = cv2.VideoCapture("/home/teddy/ITS/yolov5_deepsort/highway.mp4") 
        # self.video = cv2.VideoCapture(0)
    def __del__(self):
        self.video.release()
    def get_frame(self):
        success, image = self.video.read()
        # 因為opencv讀取的圖片並非jpeg格式，因此要用motion JPEG模式需要先將圖片轉碼成jpg格式圖片
        ret, jpeg = cv2.imencode('.jpg', image)
        time.sleep(0.05)
        return jpeg.tobytes()

class MyForm(FlaskForm):
    name = StringField('你的名字')
    agreed = BooleanField('同意加入這個組織？')
    gender = RadioField('請輸入性別', choices=[('M','男生'),('F','女生')])
    hobby = SelectField('你的興趣', choices=[('sports','運動'),('travel','旅遊'),('movie','電影')])
    others= TextAreaField('備註')
    submit = SubmitField("確認")
    pass

app = Flask(__name__)
app.config['SECRET_KEY']='mykey'

def gen(camera):
    while True:
        frame = camera.get_frame()
        # 使用generator函式輸出影片流， 每次請求輸出的content型別是image/jpeg
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route("/", methods = ['GET', 'POST'])
def index():
    '''home'''
    form = MyForm()
    # video_form = video_buttom()
    if form.is_submitted() and form.validate():
        session['name'] = form.name.data
        session['agreed'] = form.agreed.data
        session['gender'] = form.gender.data
        session['hobby'] = form.hobby.data
        session['others'] = form.others.data
        return redirect(url_for('thankyou'))

    elif request.method=='POST':
        if request.form.get('action1') == 'Video':
            return redirect(url_for('video'))
        elif request.form.get('action2') == 'Video_2':
            return redirect(url_for('video'))
        else:
            pass
    elif request.method == 'GET':
        return render_template('home.html', form=form)
    return render_template('home.html', form=form)

@app.route('/thankyou')
def thankyou():
    """thankyou"""
    return render_template('thankyou.html')

@app.route('/video')  # 這個地址返回影片流響應
def video():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')   

if __name__ == '__main__':
    app.run(debug=True)
    # from waitress import serve
    # serve(app, host='0.0.0.0',port = 5000)