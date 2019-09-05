# 前言 
本demo用于演示RK1808主动模式的跨平台特性，RK1808端接收上位机发送的图像数据，调用rockx进行推理，并将结果返回给上位机进行显示。

# 上位机部署
1. python3.6环境准备
2. Linux/MacOS: pip3 install –-user opencv-python 
3. Windows: pip3 install opencv-python 
4. 参考wiki的[http://t.rock-chips.com/wiki.php?mod=view&id=62](http://t.rock-chips.com/wiki.php?mod=view&id=62 "《Web配置介绍》")，通过网页192.168.180.8将计算棒配置成主动模式
5. 参考wiki说明[http://t.rock-chips.com/wiki.php?mod=view&id=76](http://t.rock-chips.com/wiki.php?mod=view&id=76 "《配置计算棒网络共享》")，配置RK1808计算棒NAT网络共享。
6. 上位机插入USB camera或者使用内置摄像头
7. 运行RK1808端服务程序之后，启动上位机端程序。以face_landmark为例，等待RK1808端启动face_landmark_server.py以后，上位机端运行face_landmark_server.py
8. 安卓端源码参考[https://github.com/rockchip-toybrick/master_rockx_android_demo](https://github.com/rockchip-toybrick/master_rockx_android_demo "https://github.com/rockchip-toybrick/master_rockx_android_demo")


# 1808端部署
1. sudo dnf install -y python3-opencv
2. sudo dnf install –y rockx-devel
3. sudo dnf install –y python3-toybrick-0.2-12.aarch64.rpm
