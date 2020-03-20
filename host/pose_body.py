import cv2
import time
import numpy as np
from rk_socket_class import rk_socket_client

MODEL_WIDTH = 160
MODEL_HEIGHT = 160

demo_name = "rockx_pose_body"

def pre_process(frame):
	image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	image = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
	return image

def post_process(img, data, fps):
	font = cv2.FONT_HERSHEY_SIMPLEX;
	color = (0, 255, 255)
	x_scale = img.shape[1]/MODEL_WIDTH
	y_scale = img.shape[0]/MODEL_HEIGHT

	for i in range(0, int(data['count'])):
		for j in range(0, int(data['keypoints'][i]['count'])):
			points = data['keypoints'][i]['points'][j]
			x = int(points[0] * x_scale)
			y = int(points[1] * y_scale)
			cv2.circle(img, (x, y), 3, color, 3)

		pair = ((1,2), (1,5), (2,3), (3,4), (5,6), (6,7),
				(1,8), (8,9), (9,10), (1,11), (11,12), (12,13),
				(1,0), (0,14), (14,16), (0,15), (15,17))
		for n in range(len(pair)):
			points = data['keypoints'][i]['points']
			x0 = int(points[pair[n][0]][0] * x_scale)
			y0 = int(points[pair[n][0]][1] * y_scale)
			x1 = int(points[pair[n][1]][0] * x_scale)
			y1 = int(points[pair[n][1]][1] * y_scale)
			if x0 > 0 and x1 > 0 and y0 > 0 and y1 > 0:
				cv2.line(img, (x0, y0), (x1, y1), color, 2)


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
	rknn = rk_socket_client(demo_name, port = 8003)
	#capture = cv2.VideoCapture("data/3.mp4")
	capture = cv2.VideoCapture(0)
	rknn.run(capture, pre_process, post_process)
