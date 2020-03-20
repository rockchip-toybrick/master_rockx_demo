from rk_socket_class import rk_socket_server
from rockx import RockX
import time

demo_name = "rockx_pose_body"
pose_handle =  RockX(RockX.ROCKX_MODULE_POSE_BODY)

def inference(img):
	in_img_h, in_img_w = img.shape[:2]
	time1 = time.time()
	ret, results = pose_handle.rockx_pose_body(img, in_img_w, in_img_h, RockX.ROCKX_PIXEL_FORMAT_BGR888)
	time2 = time.time()
	print("inference use " + str(time2-time1) + "sec")

	data = {}

	for result in results:
		keypoint = {}
		for p in result.points:
			point = [0, 0]
			point[0] = p.x
			point[1] = p.y
			keypoint.setdefault('points', []).append(point)
		keypoint['count'] = len(result.points)
		data.setdefault('keypoints', []).append(keypoint)

	data['count'] = len(results)
	return data

if __name__ == '__main__':
	rockx = rk_socket_server(8003)
	rockx.service(demo_name, inference)

