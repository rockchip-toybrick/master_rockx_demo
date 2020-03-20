import cv2
import time
import numpy as np
from rk_socket_class import rk_socket_client

MODEL_WIDTH = 300
MODEL_HEIGHT = 300

demo_name = "rockx_face_landmark"

def pre_process(frame):
	image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	image = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
	return image

def post_process(img, data, fps):
	x_scale = img.shape[1]/MODEL_WIDTH
	y_scale = img.shape[0]/MODEL_HEIGHT

	if data is not None and data['result'] == 0 and int(data['count']) > 0:
		for i in range(0, data['count']):
			obj = data['objs'][i]
			for j in range(0, obj['count']):
				x = int(obj['marks'][j][0] * x_scale)
				y = int(obj['marks'][j][1] * y_scale)
				cv2.circle(img, (x, y), 2, (0, 255, 0), -1);

	str_fps = "FPS: " + str(fps)
	cv2.putText(img, text=str_fps, org=(3, 15), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
			 fontScale=0.50, color=(255, 0, 0), thickness=2)

	cv2.imshow("results", img)
	c = cv2.waitKey(1) & 0xff
	if c == 27:
		cv2.destroyAllWindows()
		return -1
	else:
		return 0

if __name__ == '__main__':
	rknn = rk_socket_client(demo_name, port = 8001)
	#capture = cv2.VideoCapture("data/3.mp4")
	capture = cv2.VideoCapture(0)
	rknn.run(capture, pre_process, post_process)
