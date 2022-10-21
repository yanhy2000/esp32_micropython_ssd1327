# -*- coding: utf-8 -*-
from machine import SPI, Pin
from ssd1327 import *
from font import font16
import time
import network
import ujson as json
import urequests as requests

led = Pin(2, Pin.OUT)
spi = SPI(1, 10000000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
oled = SSD1327_SPI(128, 128, spi, dc=Pin(16), res=Pin(17), cs=Pin(15))

data_url = "http://192.168.137.1:3000" #此链接为上位机服务器的链接，端口可在服务器端源代码main.js的4行修改
ssid = "wlan_ssid" #修改为实际连接的2.4Ghz wifi网络
password = "password"


def ltext_cn(oled, string, x_axis, y_axis): # 使用本地字库
    offset = 0
    print(string)
    for k in string:
        code = 0x00
        data_code = k.encode("UTF-8")
        code |= data_code[0] << 16
        code |= data_code[1] << 8
        code |= data_code[2]
        byte_data = font16[code]
        for y in range(0, 16):
            a = bin(byte_data[y]).replace("0b", "")
            while len(a) < 8:
                a = "0" + a

            b = bin(byte_data[y + 16]).replace("0b", "")
            while len(b) < 8:
                b = "0" + b
            for x in range(0, 8):
                oled.pixel(x_axis + offset + x, y + y_axis, int(a[x]))
                oled.pixel(x_axis + offset + x + 8, y + y_axis, int(b[x]))
        offset += 16


def text_cn(oled, string, x_axis, y_axis, col=1, size=16): # 联网后连接服务端所获取的字库
    offset = 0
    fonts = ""
    print(string)
    pix = 0
    for k in string:
        print(type(k))
        if(k==" "):
            fonts = fonts + str(0x20) + "+"
        else:     
            code = 0x00
            data_code = k.encode("UTF-8")
            print(data_code)
            if(len(data_code)==1):
                print(len(data_code),"pix=",pix)
                oled.text(k,x_axis+pix,y_axis+8,col)
                pix=pix+8
            else:
                pix=pix+16
                code |= data_code[0] << 16
                code |= data_code[1] << 8
                code |= data_code[2]
                fonts = fonts + str(code) + "+"
    font_str = json.dumps(fonts)
    font_url = data_url+"/esp32/font?" + str(font_str) + "&" + str(size)
    print(font_url)
    msg = requests.get(font_url)
    msg.encoding = "utf-8"
    font_code = msg.text.split("+")
    for i in font_code:
        l_str = i.strip("[")
        r_str = l_str.strip("]")
        byte_data = eval(r_str)
        for y in range(0, 16):
            a = bin(byte_data[y]).replace("0b", "")
            while len(a) < 8:
                a = "0" + a
            b = bin(byte_data[y + 16]).replace("0b", "")
            while len(b) < 8:
                b = "0" + b
            for x in range(0, 8):
                col_a = int(a[x])
                col_b = int(b[x])
                if(col_a == 1):
                    col_a = col
                if(col_b == 1):
                    col_b = col
                oled.pixel(x_axis + offset + x, y + y_axis,col_a )
                oled.pixel(x_axis + offset + x + 8, y + y_axis, col_b)
        offset += 16


def main():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("Begin to connect wifi...")
    oled.text("Welcome!",40,80)
    oled.show()
    if not wlan.isconnected():
        print("connecting to network...")
        oled.text('connecting...',0,100)
        oled.show()
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    wlan_config = wlan.ifconfig()
    print(wlan_config)


    oled.fill(0)
    logo=framebuf.FrameBuffer(bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00>\x00\x00A\x00\x00\x81\x00\x0e\x80\x80\x11\x00@ \x00@ \x00@ \x00@\x1f\xff\x80\x00\x00\x00\x04D\x00\x02"\x00\x01\x11\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),20,20,framebuf.MONO_HLSB)
    oled.blit_buf(logo,40,60)
    text_cn(oled,"测试Test123",0,90)
    text_cn(oled, "aaa", 0, 0)
    text_cn(oled, "bbb", 0, 20)
    text_cn(oled, "ccc,测试", 0, 40)

    # cityid = "101230201"
    # url = "http://www.tianqiapi.com/api/?version=v6&cityid=" + cityid + "&appid=65251531&appsecret=Yl2bzCYb"
    # r = requests.get(url)
    # data = json.loads(r.content.decode())
    # oled.text("%s"%data["date"], 0, 0)
    # oled.line(0, 13, 128, 13,10)
    # oled.line(0, 15, 128, 15,10)
    # oled.text("City: %s"%data["cityEn"],                0, 20)          # prints the string at 32 font size at position (0, 48)
    # oled.text("Humidity: %s"%data["humidity"], 0, 30)
    # oled.text("Temp: %s - %s"%(data["tem2"], data["tem1"]), 0, 40)
    # oled.text("==wlan-config==",0,90)
    # oled.text("ip%s"%wlan_config[0],0,100)
    # oled.text("GW%s"%wlan_config[2],0,110)
    oled.show()

if __name__ == "__main__":
    led.on()
    time.sleep(0.1)
    led.off()
    time.sleep(0.1)
    led.on()
    time.sleep(0.1)
    led.off()
    time.sleep(0.1)
    led.on()
    time.sleep(0.1)
    led.off()
    main()
