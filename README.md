# esp32_micropython_ssd1327
# 介绍
在esp32芯片上使用micropython驱动ssd1327 1.5寸屏幕，使用上位机服务器获取中文字库（也可使用本地字库）

# 使用

## 服务端

需要安装nodejs 16 及以上的环境，其他版本未经测试
进入server文件夹，在文件夹内打开cmd窗口，输入 `npm i` 开始安装依赖，然后输入 `node main.js` 即可开启服务端，服务端端口可在main.js内的port值进行修改

## 客户端-esp32

用Thonny软件将根目录下python文件上传到esp32内，电脑开启热点并设置2.4Ghz(其他网络也可，但需要部署服务端)，执行`test-main.py`即可

# 函数说明

## test-main.py
ltext_cn(oled, string, x_axis, y_axis)
```
oled:传入oled类，用于执行显示等操作
string:传入的中文字体(符),自动从字库文件中寻找对应字体
x_axis:X轴像素坐标
y_axis:Y轴像素坐标
功能:使用本地字库显示中文字体，字库未完善可自行按需在 font.py 增加字体，暂未兼容中英及符号共存
使用方法：ltext_cn(oled, "测试", 10, 20)
```
text_cn(oled, string, x_axis, y_axis, col=1, size=16)
```
oled:传入oled类，用于执行显示等操作
string:传入的中文字体(符),自动从服务端字库文件中寻找对应字体(符)
x_axis:X轴像素坐标
y_axis:Y轴像素坐标
col:灰度显示等级，可显示0-16级灰度，可不传入值，默认为1
size:字体大小，默认为16号字体，可不传入值，需要服务端有该类字体（目前服务器仅取模了16号字体，暂未完善各类字号的适配）
功能:使用服务端字库显示中文字体，服务端字库已从新华字典网获取3500字并取模，增加了部分常用符号，可自行按需在 font.js 增加字体，可兼容中英及符号共存
使用方法：text_cn(oled, "测试123abc!!", 20, 40)
```

## ssd1327.py

待完善...

如有Bug等问题可提交Issue反馈，谢谢
