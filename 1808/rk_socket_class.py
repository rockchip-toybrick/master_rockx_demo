import socket
import numpy as np
import cv2 as cv
import json
import threading
import queue
import time

queue_max_size = 3
model_name_max_size = 64
queue_timeout = 2

class rk_socket_client:
	def __init__(self, model_name, ip = '192.168.180.8', port = 8002):
		self.run_flag = 0
		if len(model_name) > model_name_max_size:
			return None

		try:
			self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.sock.connect((ip, port))
			self.sock.send(str.encode(model_name.ljust(model_name_max_size)))
			print('wait 1808 ready...')
			ready = self.sock.recv(5)
			print(ready)
			if ready != b'ready':
				return None
			self.img_queue = queue.Queue(queue_max_size)

		except Exception as e:
			print(e)
			return None

	def __del__(self):
		if self.sock is not None:
			self.sock.close()

	def __send_frame(self, conn, frame):
		result, imgencode = cv.imencode('.jpg', frame)
		data = np.array(imgencode)
		stringData = data.tostring()
		sock_data = str.encode(str(len(stringData)).ljust(16)) + stringData
		conn.send(sock_data);

	def __recvall(self, conn, count):
		buf = b''
		while count:
			newbuf = conn.recv(count)
			if not newbuf: return None
			buf += newbuf
			count -= len(newbuf)
		return buf

	def __recieve_result(self, conn):
		length = self.__recvall(conn, 16)
		stringData = self.__recvall(conn, int(length))
		data = json.loads(stringData)

		return data

	def run(self, capture, f_pre_process, f_post_process):
		self.run_flag = 1
		t_send = threading.Thread(target=self.__t_send, args=(capture, f_pre_process, self.img_queue))
		t_send.start()
		self.__t_recv(f_post_process, self.img_queue)
		t_send.join()

	def __t_send(self, capture, pre_process, img_queue):
		print("__t_send start")
		error_count = 0
		try:
			while self.run_flag:
				ret, frame = capture.read()
				if ret == True:
					error_count = 0
					img_queue.put(frame, timeout=queue_timeout)
					img = pre_process(frame)
					self.__send_frame(self.sock, img)
				else:
					error_count += 1
					if error_count > 10:
						print("get frame error, abort demo!")
						self.run_flag = 0
		except Exception as e:
			print(e)
			self.run_flag = 0
			return None
		print("__t_send end")

	def __t_recv(self, post_process, img_queue):
		print("__t_recv start")
		accum_time = 0
		curr_fps = 0
		fps = 0
		prev_time = time.time()
		try:
			while self.run_flag:
				result = self.__recieve_result(self.sock)
				image = img_queue.get(timeout=queue_timeout)
				curr_time = time.time()
				exec_time = curr_time - prev_time
				prev_time = curr_time
				accum_time += exec_time
				curr_fps += 1
				if accum_time > 1:
					accum_time -= 1
					fps = curr_fps
					curr_fps = 0

				ret = post_process(image, result, fps)
				if ret < 0:
					print("post_process error, abort demo!")
					self.run_flag = 0

		except Exception as e:
			self.run_flag = 0
			print(e)
			return None
		print("__t_recv end")

class rk_socket_server:
	def __init__(self, port = 8002):
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sock.bind(('0.0.0.0', port))
		self.run_flag = 0
		self.img_queue = queue.Queue(queue_max_size)
		self.res_queue = queue.Queue(queue_max_size)

	def __del__(self):
		self.sock.close()

	def service(self, name, f_inference):
		try:
			self.sock.listen(1)
			print('start listen...')

			while 1:
				conn, addr = self.sock.accept()
				t = threading.Thread(target=self.__t_recv, args=(name, f_inference, conn, addr))
				t.start()
				t.join()

		except Exception as e:
			t.join()
			self.run_flag = 0
			self.sock.close()
			print(e)
			return -1

		return 0

	def __t_infer(self, type_name, f_inference):
		print("__t_infer start")
		try:
			while self.run_flag:
				time1 = time.time()
				img = self.img_queue.get(timeout=queue_timeout)
				time2 = time.time()
				result = f_inference(img)
				time3 = time.time()
				self.res_queue.put(result, timeout=queue_timeout)
				time4 = time.time()
				#print("get:" + str(time2-time1) + ", infer:" + str(time3-time2) + ", put:" + str(time4-time3))
		except Exception as e:
			self.run_flag = 0
			print(e)

		print("__t_infer end")

	def __t_send(self, conn, res_queue):
		print("__t_send start")
		try:
			while self.run_flag:
				result = self.res_queue.get(timeout=queue_timeout)
				self.__send_result(conn, result)
		except Exception as e:
			self.run_flag = 0
			print(e)
		print("__t_send end")

	def __t_recv(self, name, f_inference, conn, addr):
		print('connect from:'+str(addr))

		first_frame = 0
		self.run_flag = 1
		type_name = conn.recv(model_name_max_size)
		type_name = type_name.strip().decode()

		print(type_name)
		try:
			if type_name == name:
				conn.send(b'ready')
			else:
				conn.send(b'error')

			while self.run_flag:
				decimg = self.__recieve_frame(conn)
				if decimg is None:
					break
				self.img_queue.put(decimg, timeout=queue_timeout)

				if first_frame == 0:
					first_frame = 1

					t_infer = threading.Thread(target=self.__t_infer, args=(type_name, f_inference))
					t_send = threading.Thread(target=self.__t_send, args=(conn, self.res_queue))
					t_infer.start()
					t_send.start()
		except Exception as e:
			self.run_flag = 0
			print(e)

		if first_frame:
			t_infer.join()
			t_send.join()
		conn.close()
		print("__deal finish")

	def __recieve_frame(self, conn):
		try :
			length = self.__recvall(conn, 16)
			stringData = self.__recvall(conn, int(length))
			data = np.frombuffer(stringData, np.uint8)
			decimg=cv.imdecode(data,cv.IMREAD_COLOR)
		except (RuntimeError, TypeError, NameError):
			self.run_flag = 0
			return None

		return decimg

	def __recvall(self, conn, count):
		buf = b''
		while count:
			newbuf = conn.recv(count)
			if not newbuf: return None
			buf += newbuf
			count -= len(newbuf)
		return buf

	def __send_result(self, conn, result):
		stringData = json.dumps(result).encode('utf-8')
		sock_data = str.encode(str(len(stringData)).ljust(16)) + stringData
		conn.send(sock_data)
 
