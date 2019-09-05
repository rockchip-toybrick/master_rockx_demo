from rk_socket_class import rk_socket_server
import toybrick as toy
import time

demo_name = "rockx_object_detect"
object_handle =  toy.createRockx(toy.RockxType.ROCKX_MODULE_OBJECT_DETECTION)

def inference(img):
	time1 = time.time()
	result = object_handle.inference(img)
	time2 = time.time()
	print("inference use " + str(time2-time1) + "sec")
	return result

if __name__ == '__main__':
	rockx = rk_socket_server()
	rockx.service(demo_name, inference)

