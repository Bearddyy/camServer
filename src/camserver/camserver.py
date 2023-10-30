''' Simple steaming server for the camera. '''


from flask import Flask, Response, render_template
import cv2
import atexit


class Camera(object):
    def __init__(self, camera_id=0):
        self.cap = cv2.VideoCapture(0)

        # just in case the camera was not released
        atexit.register(self.__del__)

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        ret, frame = self.cap.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()



if __name__ == '__main__':
    # running the app
    import argparse

    parser = argparse.ArgumentParser(description='Run the camera server.')
    parser.add_argument('--camera_id', type=int, default=0)
    args = parser.parse_args()

    app = Flask(__name__)
    cam = Camera(args.camera_id)

    @app.route('/')
    def index():
        return render_template('index.html')

    def gen():
        while True:
            frame = cam.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    @app.route('/video_feed')
    def video_feed():
        return Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    app.run(host='', port=5000, debug=True)
    


