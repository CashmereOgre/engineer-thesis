from imutils.video import VideoStream
from imutils import face_utils
from scipy.spatial import distance as dist
import math
import os
import imutils
import dlib
import cv2
import UdpComms as U

def eye_aspect_ratio(eye):
    return ((dist.euclidean(eye[1], eye[5]) + dist.euclidean(eye[2], eye[4])) / (2.0 * dist.euclidean(eye[0], eye[3])))

def set_eye_weight(eye):
    EAR_weight = eye_aspect_ratio(eye)
    if EAR_weight < 0.25:
        return 100
    elif EAR_weight > 0.35:
        return 0
    else:
        return abs((math.tanh((EAR_weight - 0.3) * 40) + 1) * 50 - 100)
    
def set_mouth_open_weight(mouth, calibration):
    openess = dist.euclidean(mouth[3], mouth[9])
    if openess > 3 * calibration:
        return 100
    elif openess <= calibration:
        return 0
    else:
        return ((openess/calibration) - 1) * 50

def set_smile_weight(mouth, calibration):
    smile = dist.euclidean(mouth[0], mouth[6])
    if smile > 1.4 * calibration:
        return 100
    elif smile <= calibration:
        return 0
    else:
        return ((smile / calibration) - 1) * 250


(left_eye_start, left_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(right_eye_start, right_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mouth_start, mouth_end) = face_utils.FACIAL_LANDMARKS_68_IDXS["mouth"]

calib_mouth_closed = None
calib_smile = None

predictor = dlib.shape_predictor(os.path.dirname(__file__) + "\shape_predictor_68_face_landmarks.dat")
detector = dlib.get_frontal_face_detector()
cv2.namedWindow("Output", cv2.WINDOW_AUTOSIZE)

sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001, enableRX=False, suppressWarnings=True)

video = VideoStream().start()


while cv2.getWindowProperty('Output', cv2.WND_PROP_VISIBLE):
    frame = video.read()
    frame = imutils.resize(frame, width = 500)
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = detector(grayscale, 0)

    try:
        landmarks = predictor(grayscale, faces[0])
        landmarks = face_utils.shape_to_np(landmarks)
        
        left_eye = landmarks[left_eye_start:left_eye_end]
        right_eye = landmarks[right_eye_start:right_eye_end]
        mouth = landmarks[mouth_start:mouth_end]
        
        if calib_mouth_closed is None:
            calib_mouth_closed = dist.euclidean(mouth[3], mouth[9])
        
        if calib_smile is None:
            calib_smile = dist.euclidean(mouth[0], mouth[6])
        
        left_eye_weight = set_eye_weight(left_eye)
        right_eye_weight = set_eye_weight(right_eye)
        mouth_open_weight = set_mouth_open_weight(mouth, calib_mouth_closed)
        smile_weight = set_smile_weight(mouth, calib_smile)            
        
        for(x, y) in landmarks:
            cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
    except:
        print("Face is not visible on camera")
        
    cv2.imshow("Output", frame)
       
    sock.SendData(str(left_eye_weight) + "," + str(right_eye_weight) + "," + str(mouth_open_weight) + "," + str(smile_weight))
    
    if (cv2.waitKey(5) & 0xFF)==27:   
        break
    
cv2.destroyAllWindows()
video.stop()

