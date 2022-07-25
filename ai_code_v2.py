import math
import os
import uuid

import imutils
import mediapipe as mp
import cv2
import sys
import imagezmq

APP_FOLDER_SERVICE_PATH = '/home/deepak/Documents/myProjects/ttpl/face_cropped/'
# APP_FOLDER_SERVICE_PATH = '/home/admin1/Videos/run/'

FACE_DETECTION_CONF = 0.5

# MEDIAPIPE FACE DETECTOR MODEL
mp_drawing = mp.solutions.drawing_utils
mp_face_detection = mp.solutions.face_detection
face_detection_model = mp_face_detection.FaceDetection(
    model_selection=1, min_detection_confidence=FACE_DETECTION_CONF)

FACE_SAVING_PATH = f'{APP_FOLDER_SERVICE_PATH}/camera_faces'

# CAMERA SETTINGS VARIABLE
cameras_ip_list = []
cameras_port_list = []
cameras_username_list = []
cameras_password_list = []
cameras_name_list = []

lastActive = {}
folder_names = {}
imageHub = imagezmq.ImageHub()
while True:
    try:
        (rpiName, frame) = imageHub.recv_image()
        imageHub.send_reply(b'OK')

        # print("rpiName::", rpiName.split('@@'))
        # rpiName, IS_FRAME = rpiName.split('@@')

        for_face_frame = frame

        image_height, image_width, _ = frame.shape
        frame = imutils.resize(frame, width=400)
        # # frame = cv2.flip(frame, 1)
        (h, w) = frame.shape[:2]

        if 'AI' in rpiName:
            image = for_face_frame
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_detection_model.process(image)

            if results.detections:
                print(f'Total face detected {len(results.detections)}')
                for detection in results.detections:
                    print(detection)
                    # mp_drawing.draw_detection(image, detection)
                    location = detection.location_data.relative_bounding_box
                    x = location.xmin  # normalized coordinates
                    y = location.ymin
                    w = location.width
                    h = location.height
                    x_px = min(math.floor(x * image_width), image_width - 1)  # denormalized coordinates
                    y_px = min(math.floor(y * image_height), image_height - 1)
                    w_px = min(math.floor(w * image_width), image_width - 1)
                    h_px = min(math.floor(h * image_height), image_height - 1)
                    # cv2.rectangle(baseimage,(x_px,y_px),(x_px+w_px,y_px+h_px),color=(255,0,255),thickness=1)
                    face = (x_px, y_px, w_px, h_px)
                    cv2_x, cv2_y, cv2_w, cv2_h = face
                    cv2_x = max(cv2_x, 0)
                    cv2_y = max(cv2_y, 0)
                    face_x = cv2_x
                    face_y = cv2_y
                    endX = cv2_x + cv2_w
                    endY = cv2_y + cv2_h

                    padding = 40
                    new_cv2_x = max(int(cv2_x - padding), 0)
                    new_cv2_y = max(int(cv2_y - padding), 0)
                    new_endX = min(int(endX + padding), image_width)
                    new_endY = min(int(endY + padding), image_height)
                    atleast_hero_image_path = None
                    cropped_baseImage = image[new_cv2_y:new_endY, new_cv2_x:new_endX]
                    image_name = str(uuid.uuid4()) + ".jpg"
                    file_name = os.path.join(FACE_SAVING_PATH, image_name)
                    cv2.imwrite(file_name, cropped_baseImage)

            else:
                print("Face not found")

            scale_percent = 40  # percent of original size
            width = int(for_face_frame.shape[1] * scale_percent / 100)
            height = int(for_face_frame.shape[0] * scale_percent / 100)
            dim = (width, height)

            # resize image
            resized = cv2.resize(for_face_frame, dim, interpolation=cv2.INTER_AREA)
            # cv2.imshow("roi", resized)
            # cv2.imshow("Mask", frame)

            key = cv2.waitKey(30)
            if key == 27:
                break

    except Exception as error:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno

        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
        print("Exception error: ", error)

cv2.destroyAllWindows()
