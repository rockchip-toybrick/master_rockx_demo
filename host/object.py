import cv2
import time
import numpy as np
from rk_socket_class import rk_socket_client

MODEL_WIDTH = 300
MODEL_HEIGHT = 300

demo_name = "rockx_object_detect"

def pre_process(frame):
	image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	image = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
	return image

def post_process(img, data, fps):
	x_scale = img.shape[1]/MODEL_WIDTH
	y_scale = img.shape[0]/MODEL_HEIGHT
	for i in range(0, data['count']):
		x1 = int(data['objs'][i]['left']*x_scale)
		y1 = int(data['objs'][i]['top']*y_scale)
		x2 = int(data['objs'][i]['right']*x_scale)
		y2 = int(data['objs'][i]['bottom']*y_scale)
		cv2.rectangle(img, (x1, y1), (x2, y2), (0, 100, 255), 2)
		cv2.putText(img, data['objs'][i]['label'], (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 255), 2)

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
	rknn = rk_socket_client(demo_name, port = 8002)
	#capture = cv2.VideoCapture("data/3.mp4")
	capture = cv2.VideoCapture(0)
	rknn.run(capture, pre_process, post_process)
