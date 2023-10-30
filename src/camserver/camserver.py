''' Simple steaming server for the camera. '''


from flask import Flask, Response, render_template
import cv2
import atexit


class Camera(object):
    def __init__(self, camera_id=0, pi=False, width=640, height=480):
        if pi:
            self.pi = True
            import picamera
            self.cap = picamera.PiCamera()
            self.cap.resolution = (640, 480)
            self.cap.framerate = 24
            self.rawCapture = picamera.array.PiRGBArray(self.cap, size=(640, 480))
            self.stream = self.cap.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        else:
            self.cap = cv2.VideoCapture(0)

        # just in case the camera was not released
        atexit.register(self.__del__)

    def __del__(self):
        if self.pi:
            self.cap.close()
        else:
            self.cap.release()

    def get_frame(self):
        if self.pi:
            frame = self.stream.__next__().array
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        else:
            ret, frame = self.cap.read()
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()



if __name__ == '__main__':
    # running the app
    import argparse

    parser = argparse.ArgumentParser(description='Run the camera server.')
    parser.add_argument('--camera_id', type=int, default=0)
    parser.add_argument('--pi', action='store_true')
    parser.add_argument('--width', type=int, default=640)
    parser.add_argument('--height', type=int, default=480)
    args = parser.parse_args()

    app = Flask(__name__)
    cam = Camera(camera_id=args.camera_id, pi=args.pi, width=args.width, height=args.height)

    width = int(cam.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cam.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


    @app.route('/')
    def index():
        return render_template('index.html', width=width, height=height)

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



