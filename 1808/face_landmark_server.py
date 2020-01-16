from rk_socket_class import rk_socket_server
from rockx import RockX
import time

demo_name = "rockx_face_landmark"
face_det = RockX(RockX.ROCKX_MODULE_FACE_DETECTION)
face_landmark68 = RockX(RockX.ROCKX_MODULE_FACE_LANDMARK_68)

def inference(img):
	total_result = {'result':-1, 'count':0}
	obj = {}
	tmp_result = []

	in_img_h, in_img_w = img.shape[:2]

	time1 = time.time()
	ret, results = face_det.rockx_face_detect(img, in_img_w, in_img_h, RockX.ROCKX_PIXEL_FORMAT_BGR888)
	try:
		for result in results:
			ret, landmark = face_landmark68.rockx_face_landmark(img, in_img_w, in_img_h,
                                                                RockX.ROCKX_PIXEL_FORMAT_BGR888,
                                                                  result.box)
			print(landmark)
			time2 = time.time()
			for p in landmark.landmarks:
				mark = [0, 0]
				mark[0] = p.x
				mark[1] = p.y
				obj.setdefault('marks', []).append(mark)

			obj['count'] = len(landmark.landmarks)
			tmp_result.append(obj)
			total_result['count'] += 1
			print("inference use " + str(time2-time1) + "sec")

		total_result['objs'] = tmp_result
		total_result['result'] = 0

	except Exception as e:
			print(e)

	return total_result

if __name__ == '__main__':
	rockx = rk_socket_server()
	rockx.service(demo_name, inference)

