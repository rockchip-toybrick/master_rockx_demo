from rk_socket_class import rk_socket_server
import toybrick as toy
import time

demo_name = "rockx_face_landmark"
face_det = toy.createRockx(toy.RockxType.ROCKX_MODULE_FACE_DETECTION)
face_landmark68 = toy.createRockx(toy.RockxType.ROCKX_MODULE_FACE_LANDMARK_68)

def inference(img):
	total_result = {'result':-1, 'count':0}
	tmp_result = []

	time1 = time.time()
	res_det = face_det.inference(img)
	try:
		for i in range(res_det['count']):
			obj = res_det['objs'][i]
			result = face_landmark68.inference(img, (obj['left'], obj['top'], obj['right'], obj['bottom']))
			time2 = time.time()
			tmp_result.append(result)
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

