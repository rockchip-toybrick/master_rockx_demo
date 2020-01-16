from rk_socket_class import rk_socket_server
from rockx import RockX
import time

demo_name = "rockx_object_detect"
object_handle = RockX(RockX.ROCKX_MODULE_OBJECT_DETECTION)

def inference(img):
	data = {}
	time1 = time.time()
	in_img_h, in_img_w = img.shape[:2]
	ret, results = object_handle.rockx_face_detect(img, in_img_w, in_img_h, RockX.ROCKX_PIXEL_FORMAT_BGR888)
	time2 = time.time()
	print("inference use " + str(time2-time1) + "sec")

	for result in results:
		obj = {}
		obj['left'] = result.box.left
		obj['left'] = result.box.left
		obj['top'] = result.box.top
		obj['right'] = result.box.right
		obj['bottom'] = result.box.bottom
		obj['label'] = RockX.ROCKX_OBJECT_DETECTION_LABELS_91[result.cls_idx]
		data.setdefault('objs', []).append(obj)

	data['count'] = len(results)
	return data

if __name__ == '__main__':
	rockx = rk_socket_server()
	rockx.service(demo_name, inference)

