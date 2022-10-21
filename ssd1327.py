__version__ = "1.1.1"

from micropython import const  # 从MicroPython中导入const
import framebuf  # 导入显示内容缓冲区

# SSD1327命令寄存器编号定义
SET_COL_ADDR = const(0x15)  # 设定行位址
SET_SCROLL_DEACTIVATE = const(0x2E)  # 设定卷动不活动
SET_ROW_ADDR = const(0x75)  # 设定列位址
SET_CONTRAST = const(0x81)  # 设定显示对比
SET_SEG_REMAP = const(0xA0)  # 设定显示节段重新映射
SET_DISP_START_LINE = const(0xA1)  # 设定显示起始列
SET_DISP_OFFSET = const(0xA2)  # 设定显示偏移量
SET_DISP_MODE = const(0xA4)  # 设定显示模式：一般0xA4, 全亮0xA5, 全灭0xA6, 反相0xA7
SET_MUX_RATIO = const(0xA8)  # 设定多重寻址
SET_FN_SELECT_A = const(0xAB)  # 设定功能选择A
SET_DISP = const(0xAE)  # 设定显示电源关闭0xAE,电源开启0xAF
SET_PHASE_LEN = const(0xB1)  # 设定显示节段波形长度
SET_DISP_CLK_DIV = const(0xB3)  # 设定显示派波除数
SET_SECOND_PRECHARGE = const(0xB6)  # 设定第二段充电电压
SET_GRAYSCALE_TABLE = const(0xB8)  # 设定灰阶表
SET_GRAYSCALE_LINEAR = const(0xB9)  # 设定灰阶线性度
SET_PRECHARGE = const(0xBC)  # 设定预充电电压
SET_VCOM_DESEL = const(0xBE)  # 设定 VCOM 电压
SET_FN_SELECT_B = const(0xD5)  # 设定功能选择B
SET_COMMAND_LOCK = const(0xFD)  # 命令设置锁定

# registers
# SSD1327 设置命令/数据 (后六位为0)
REG_CMD = const(0x80)  # 设置为命令，Co=1, D/C#=0
REG_DATA = const(0x40)  # 设置为数据，Co=0, D/C#=1


class SSD1327:
    def __init__(self, width=128, height=128):
        self.width = width  # 指定 OLED 显示的宽度
        self.height = height  # 指定OLED显示高度
        self.buffer = bytearray(
            self.width * self.height // 2
        )  # 外部显示为4bit(16灰阶)，要求存储体数量为长x宽的字体
        self.framebuf = framebuf.FrameBuffer(
            self.buffer, self.width, self.height, framebuf.GS4_HMSB
        )  # 配置所需储存，大小、长、宽及4bit方式。
        # 设定行列起始位置，以公式自动转换96x96, 128x128像素OLED
        self.col_addr = ((128 - self.width) // 4, 63 - ((128 - self.width) // 4))
        # 96x96     (8, 55)
        # 128x128   (0, 63)

        self.row_addr = (0, self.height - 1)
        # 96x96     (0, 95)
        # 128x128   (0, 127)

        self.offset = 128 - self.height
        # 96x96     32
        # 128x128   0

        self.poweron()  # OLED电源开启
        self.init_display()  # OLED进行初始化

    def init_display(self):  # OLED内容，依序执行命令初始化并清除OLED显示区
        for cmd in (
            SET_COMMAND_LOCK,
            0x12,  # 命令解锁(Unlock)
            SET_DISP,  # 关闭显示(Display off)
            # 设置显示解析度及排列(Resolution and layout)
            SET_DISP_START_LINE,
            0x00,  # 设定显示启始列(start line)
            SET_DISP_OFFSET,
            self.offset,  # 通过 COM 设置垂直偏移，范围为 0~127
            # 重新设置映射方式 (Set re-map)
            # 启用列地址重新映射 (Enable column address re-map)
            # 禁用半字节重映射 (Disable nibble re-map)
            # 水平地址增量 (Horizontal address increment)
            # 启用 COM 重新映射 (Enable COM re-map)
            # 启用 COM 拆分奇偶 (Enable COM split odd even)
            SET_SEG_REMAP,
            0x51,
            SET_MUX_RATIO,
            self.height - 1,
            # 设定和驱动电路(Timing and driving scheme)
            SET_FN_SELECT_A,
            0x01,  # 致能内部供电(Enable internal VDD regulator)
            SET_PHASE_LEN,
            0x51,  # Phase 1: 1 DCLK, Phase 2: 5 DCLKs
            SET_DISP_CLK_DIV,
            0x01,  # 设定显示脉波除数(Divide ratio: 1, Oscillator Frequency: 0)
            SET_PRECHARGE,
            0x08,  # 设置预充电电压（Set pre-charge voltage level: VCOMH）
            SET_VCOM_DESEL,
            0x07,  # 设定VCOM电压(Set VCOMH COM deselect voltage level: 0.86*Vcc)
            SET_SECOND_PRECHARGE,
            0x01,  # 设定第二段充电电压(Second Pre-charge period: 1 DCLK)
            SET_FN_SELECT_B,
            0x62,  # 设定功能选择B(Enable enternal VSL, Enable second precharge)
            # 设定显示(Display)
            SET_GRAYSCALE_LINEAR,  # 使用线性灰阶对照表(Use linear greyscale lookup table)
            SET_CONTRAST,
            0x7F,  # 设定对比中间亮度(Medium brightness)
            SET_DISP_MODE,  # 设定显示模式一般不反相(Normal, not inverted)
            SET_COL_ADDR,
            self.col_addr[0],
            self.col_addr[1],
            SET_ROW_ADDR,
            self.row_addr[0],
            self.row_addr[1],
            SET_SCROLL_DEACTIVATE,  # 设定卷动不启动
            SET_DISP | 0x01,
        ):  # 设定显示开启(Display on)
            self.write_cmd(cmd)  # 依序写入命令
        self.fill(0)  # 清除画面(clear screen)
        self.write_data(self.buffer)  # 显示内容

    # 关闭OLED电源
    def poweroff(self):
        self.write_cmd(SET_FN_SELECT_A)
        self.write_cmd(
            0x00
        )  # 禁用内部 VDD 稳压器，以节省电量(Disable internal VDD regulator, to save power)
        self.write_cmd(SET_DISP)

    # 打开OLED电源
    def poweron(self):
        self.write_cmd(SET_FN_SELECT_A)
        self.write_cmd(0x01)  # 启用内部 VDD 稳压器(Enable internal VDD regulator)
        self.write_cmd(SET_DISP | 0x01)

    # 调整显示对比
    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)  # 对比值0-255

    # 旋转显示内容
    def rotate(self, rotate):
        self.poweroff()
        self.write_cmd(SET_DISP_OFFSET)
        self.write_cmd(self.height if rotate else self.offset)
        self.write_cmd(SET_SEG_REMAP)
        self.write_cmd(0x42 if rotate else 0x51)
        self.poweron()

    # 显示反相(Ture/False)
    def invert(self, invert):
        self.write_cmd(
            SET_DISP_MODE | (invert & 1) << 1 | (invert & 1)
        )  # 0xA4=正常, 0xA7=反相

    # 显示缓冲区内容
    def show(self):
        self.write_cmd(SET_COL_ADDR)  # 指定行启始位置
        self.write_cmd(self.col_addr[0])
        self.write_cmd(self.col_addr[1])
        self.write_cmd(SET_ROW_ADDR)  # 指定列启始位置
        self.write_cmd(self.row_addr[0])
        self.write_cmd(self.row_addr[1])
        self.write_data(self.buffer)  # 写入缓冲区内容

    # 将所有像素填入指定颜色，4bit灰阶(0 - 15)
    def fill(self, col):
        self.framebuf.fill(col)

    # 将特定位置像素填入指定颜色，4bit灰阶(0 - 15)
    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)

    # 获取指定位置的像素色值
    def get_pixel(self, x, y):
        self.framebuf.pixel(x, y)

    # 指定起始点、终点画一条线
    def line(self, x1, y1, x2, y2, col):
        self.framebuf.line(x1, y1, x2, y2, col)

    # 指定长度、颜色画水平线
    def hline(x, y, w, col):
        self.framebuf.hline(x, y, w, col)

    # 指定长度、颜色画垂直线
    def vline(x, y, h, col):
        self.framebuf.hline(x, y, h, col)

    # 在给定位置、按照给定大小和颜色绘制一个空心矩形(1像素边框)
    def rect(x, y, w, h, c):
        self.framebuf.rect(x, y, w, h, c)

    # 在给定位置、按照给定大小和颜色绘制一个实心矩形
    def fill_rect(x, y, w, h, c):
        self.framebuf.fill_rect(x, y, w, h, c)

    # 软体显示卷动
    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)
        # software scroll

    # 在指定位置显示文字串及对应颜色，4bit灰阶(0 - 15)，预设颜色15(不传入则为1)，所有字符都有8x8像素的尺寸
    def text(self, string, x, y, col=15):
        self.framebuf.text(string, x, y, col)

    def blit_buf(self, buf, x, y):
        self.blit = self.framebuf.blit(buf, x, y)  # 在当前帧缓冲区的顶部的给定坐标下绘制另外一个帧缓冲区

    def write_cmd(self):
        raise NotImplementedError

    def write_data(self):
        raise NotImplementedError


class SSD1327_SPI(SSD1327):
    def __init__(self, width, height, spi, dc, res, cs):
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        import time

        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        super().__init__(width, height)

    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)
