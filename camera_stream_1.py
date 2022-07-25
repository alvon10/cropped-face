# import the necessary packages
from imutils.video import VideoStream
import imagezmq
import schedule
import socket
import time


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


# local_server_ip = '192.168.10.67'
local_server_ip = get_ip_address()

# initialize the ImageSender object with the socket address of the
# server
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(local_server_ip))

# get the host name, initialize the video stream, and allow the
# camera sensor to warmup

rpiusername = 'admin'
rpipassword = 'ttpl1234'
rpiip = '192.168.10.171'
rpiport = '7554'
rpiName = f'AI'

# vs = VideoStream(src=f'rtsp://{rpiusername}:{rpipassword}@{rpiip}:{rpiport}/11').start()
# vs = VideoStream(src=f'rtsp://{rpiusername}:{rpipassword}@{rpiip}:{rpiport}/').start()
# vs = VideoStream(src=f'rtsp://{rpiip}:{rpiport}/user={rpiusername}&password={rpipassword}&channel=1&stream=0.sdp?').start()
# vs = VideoStream(usePiCamera=True, resolution=(320, 240)).start()
# vs = VideoStream(0, resolution=(320, 240)).start()

time.sleep(2.0)

PREV_STATE = 256
IS_CONNECTED = False


def check_camera_stream():
    global IS_CONNECTED
    try:
        vs = VideoStream(src=0).start()
	    #vs = VideoStream(src=f'rtsp://{rpiusername}:{rpipassword}@{rpiip}:{rpiport}/12').start()
        time.sleep(2)
        frame = vs.read()
        if frame is not None:
            p = 0
        else:
            print(f'stream error 1')
            p = 256
    except Exception as err:
        print(f'stream error 2=> {err}')
        p = 256

    if PREV_STATE == 256 and p == 0:
        # send_alert("USBC", f"Usb connected")
        IS_CONNECTED = True
        while IS_CONNECTED:
            try:
                frame = vs.read()
                sender.send_image(rpiName, frame)
            except Exception as error:
                print("Camera stream read issue >> ", error)
                # send_alert("USBDC", f"Usb disconnected")
                IS_CONNECTED = False


schedule.every(10).seconds.do(check_camera_stream)
while True:
    schedule.run_pending()
    time.sleep(1)
