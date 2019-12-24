"""
本程序实现对24位真彩色bmp图片的显示功能、缩放功能、镜像功能、调整亮度功能、调整对比功能
图像旋转功能和图像平移功能还存在问题，生成的图片无法加载
"""
import numpy as np
import cv2
import math
from struct import unpack

# bmp文件
class BMP :
    def __init__(self):
        """初始化"""
        # bmp文件的文件头(bmp file header)
        self.bfType = None                      # 文件类型
        self.bfSize = None                      # 文件大小
        self.bfReserved1 = None                 # 保留字段
        self.bfReserved2 = None                 # 保留字段
        self.bfOffBits = None                   # 从文件头到位图数据的偏移量（文件头+位图信息头+调色板长度）

        # 位图信息头(bitmap information)
        self.biSize = None                      # 信息头的大小
        self.biWidth = None                     # 图像宽度，以像素为单位
        self.biHeight = None                    # 图像高度，以像素为单位
        self.biPlanes = None                    # 颜色平面数
        self.biBitCount = None                  # 每像素比特数，即每个像素用多少位表示
        self.biCompression = None               # 图像的压缩类型
        self.biSizeImage = None                 # 位图数据的大小（=文件大小-偏移量）
        self.biXPelsPerMeter = None             # 水平分辨率，单位是像素/米，有符号整数
        self.biYPelsPerMeter = None             # 垂直分辨率，单位是像素/米，有符号整数
        self.biClrUsed = None                   # 位图使用的调色盘中的颜色索引数
        self.biClrImportant = None              # 对图像显示有重要影响的颜色索引数目

        # 调色板(color palette)，可选项
        # 采用24位真彩色位图，无需使用调色板模块。用3个字节（24位）的实际RGB值表示一个像素。
        # （同理，32位真彩色位图也不需要调色板模块。用4个字节（32位）的RGBA值表示一个像素。）

        # 位图数据(bitmap data)
        self.bmp_data = []

        # 存储R、G、B 三个通道的值，方便后续处理
        self.R = []
        self.G = []
        self.B = []

    def resolve(self, filePath):
        """解析BMP文件
        :param filePath: BMP文件地址
        """
        # 打开bmp文件
        file = open(filePath, 'rb')

        # 读取bmp文件的文件头(bmp file header)，14字节
        self.bfType = unpack('<h', file.read(2))[0]             # 2字节，文件类型，BMP文件这两个字节为0x4d42，字符显示为'BM'
        self.bfSize = unpack('<i', file.read(4))[0]             # 4字节，文件大小
        self.bfReserved1 = unpack('<h', file.read(2))[0]        # 2字节，保留字段，必须设为0
        self.bfReserved2 = unpack('<h', file.read(2))[0]        # 2字节，保留字段，必须设为0
        self.bfOffBits = unpack('<i', file.read(4))[0]          # 4字节，从文件头到位图数据的偏移量（即文件头+位图信息头+调色板长度）
        
        # 读取位图信息头(bitmap information)，40字节
        self.biSize = unpack('<i', file.read(4))[0]             # 4字节，信息头的大小，BMP文件为0x28，即40
        self.biWidth = unpack('<i', file.read(4))[0]            # 4字节，以像素为单位表示图像的宽度
        self.biHeight = unpack('<i', file.read(4))[0]           # 4字节，以像素为单位表示图像的高度
        self.biPlanes = unpack('<h', file.read(2))[0]           # 2字节，颜色平面数，总设为1
        self.biBitCount = unpack('<h', file.read(2))[0]         # 2字节，比特数/像素数，即每个像素用多少位表示(每像素比特数)       
        self.biCompression = unpack('<i', file.read(4))[0]      # 4字节，图像的压缩类型，最常用的是0，即BI_RGB格式，表示不压缩
        self.biSizeImage = unpack('<i', file.read(4))[0]        # 4字节，位图数据的大小，biSizeImage=bfSize-bfOffBits，即图像大小=文件大小-偏移量。BI_RGB格式时，可设置为0
        self.biXPelsPerMeter = unpack('<i', file.read(4))[0]    # 4字节，水平分辨率，单位是像素/米，有符号整数
        self.biYPelsPerMeter = unpack('<i', file.read(4))[0]    # 4字节，垂直分辨率，单位是像素/米，有符号整数
        self.biClrUsed = unpack('<i', file.read(4))[0]          # 4字节，位图使用的调色板中的颜色索引数，biClrUsed=2^biBitCount.为0说明适用所有
        self.biClrImportant = unpack('<i', file.read(4))[0]     # 4字节，对图像显示有重要影响的颜色索引数目。为0说明都重要

        # 本程序仅处理24位真彩色图片
        if self.biBitCount != 24 :
            print('输入的图片比特值为 ：' + str(self.biBitCount) + '\t 与程序不匹配')

        # 调色板(color palette)，可选项
        # 采用24位真彩色位图，无需使用调色板模块。用3个字节（24位）的实际RGB值表示一个像素。
        # （同理，32位真彩色位图也不需要调色板模块。用4个字节（32位）的RGBA值表示一个像素。）

        # 读取位图数据(bitmap data)，字节数 = biSizeImage
        # self.bmp_data = []                                      # 存储位图数据（还未读入）
        for height in range(self.biHeight):
            bmp_data_row = []                                   # 存储一行位图数据（还未读入）
            
            # 四字节填充位检测
            # windows默认的扫描的最小单位是4字节，数据对齐有利于提高数据获取速度
            # BMP图像要求每行的数据长度必须是4的倍数，如果不够需要进行0比特填充
            # 因此位图数据的大小不一定 = 宽 * 高 * 每像素字节数，因为每行可能还有0比特填充
            count = 0                                           # 一行位图数据的字节计数
            # 遍历像素读取一行位图数据
            for width in range(self.biWidth):
                bmp_data_row.append([unpack('<B', file.read(1))[0], unpack('<B', file.read(1))[0], unpack('<B', file.read(1))[0]])
                count += 3                               #  24位真彩色BMP，3字节/像素
            # bmp四字节对齐原则，若一行的字节计数count不是4的倍数，说明有填充，需要继续读填充
            while count % 4 != 0:
                file.read(1)
                count += 1
            self.bmp_data.append(bmp_data_row)                  # 真正读完一行位图数据
        
        # 数据的大小端问题（读取、写入数据以小端模式）
        # 因为bmp文件读取是从左到右读像素、从下到上读行，而上面是按照从上到下的顺序读取行的，所以需对行逆转
        self.bmp_data.reverse()
        
        # bmp文件读取结束
        file.close()

        # 存储R、G、B 三个通道的值，方便后续处理
        self.RGB()

    def RGB(self):
        """存储R、G、B 三个通道的值，方便后续处理"""
        # 先清空，以重新写入
        self.R.clear()
        self.G.clear()
        self.B.clear()
        for row in range(self.biHeight):
            # 每行位图数据的RGB
            R_row = []
            G_row = []
            B_row = []
            for col in range(self.biWidth):
                B_row.append(self.bmp_data[row][col][0])
                G_row.append(self.bmp_data[row][col][1])
                R_row.append(self.bmp_data[row][col][2])
            self.B.append(B_row)
            self.G.append(G_row)
            self.R.append(R_row)

    def generate(self, filePath):
        """生成bmp文件
        :param filePath: 存储生成的bmp文件的路径
        """
        file = open(filePath, 'wb+')

        # 写入文件头
        file.write(i_to_bytes(self.bfType, 2))
        file.write(i_to_bytes(self.bfSize, 4))
        file.write(i_to_bytes(self.bfReserved1, 2))
        file.write(i_to_bytes(self.bfReserved2, 2))
        file.write(i_to_bytes(self.bfOffBits, 4))

        # 写入信息头
        file.write(i_to_bytes(self.biSize, 4))
        file.write(i_to_bytes(self.biWidth, 4))
        file.write(i_to_bytes(self.biHeight, 4))
        file.write(i_to_bytes(self.biPlanes, 2))
        file.write(i_to_bytes(self.biBitCount, 2))
        file.write(i_to_bytes(self.biCompression, 4))
        file.write(i_to_bytes(self.biSizeImage, 4))
        file.write(i_to_bytes(self.biXPelsPerMeter, 4))
        file.write(i_to_bytes(self.biYPelsPerMeter, 4))
        file.write(i_to_bytes(self.biClrUsed, 4))
        file.write(i_to_bytes(self.biClrImportant, 4))

        # 写入位图数据
        bmpData = self.bmp_data.copy()  # 若直接赋值，而不是用copy()，会使得两个变量占用同一地址，则需要在函数尾重新reverse，否则双数次缩放时图像会上下倒转
        bmpData.reverse()   # 重新逆转（大小端问题）
        # for bit in bmpData:
        #     file.write(bit)
        for height in range(self.biHeight):
            count = 0
            for width in range(self.biWidth):
                file.write(i_to_bytes(bmpData[height][width][0], 1))
                file.write(i_to_bytes(bmpData[height][width][1], 1))
                file.write(i_to_bytes(bmpData[height][width][2], 1))
                count += 3
            while count % 4 != 0:
                file.write(i_to_bytes(0, 1))     # 四字节对齐原则，若一行的字节数不是4的倍数，则填充？（一个英文标点占一字节）
                count += 1

        # 关闭文件
        file.close()

    def zoom_in_and_out(self, new_width, new_height):
        """bmp图片的放大和缩小（双线性插值法）
        原理参考：https://blog.csdn.net/weixinhum/article/details/38963705       
        :paran new_width: 目标图片的宽
        :param new_height: 目标图片的高
        """
        new_bmp_data = []

        self.RGB()  # 确保RGB是正确的

        # 双线性插值法实现图片的放大/缩小
        for height in range(new_height):
            new_bmp_data_row = []

            for width in range(new_width):
                # 计算目标图像的像素映射到原图像的位置P
                original_h = height / new_height * self.biHeight
                original_w = width / new_width * self.biWidth

                # 点P在原图像素方块左上角点A的坐标（高和宽）
                A_w = int(original_w)
                A_h = int(original_h)

                # 计算原图像映射点P到左上角点A的水平/竖直距离
                distance_Aw = original_w - A_w
                distance_Ah = original_h - A_h

                # 左上角点A 右上角点B 左下角点C 右下角点D的RGB值
                A_r = self.R[A_h][A_w]
                A_g = self.G[A_h][A_w]
                A_b = self.B[A_h][A_w]

                if A_w + 1 == self.biWidth:    # 边界点
                    B_r = A_r
                    B_g = A_g
                    B_b = A_b
                else:
                    B_r = self.R[A_h][A_w + 1]
                    B_g = self.G[A_h][A_w + 1]
                    B_b = self.B[A_h][A_w + 1]

                if A_h + 1 == self.biHeight:   # 边界点
                    C_r = A_r
                    C_g = A_g
                    C_b = A_b
                else:
                    C_r = self.R[A_h + 1][A_w]
                    C_g = self.G[A_h + 1][A_w]
                    C_b = self.B[A_h + 1][A_w]

                if A_w + 1 == self.biWidth:   # 边界点
                    D_r = C_r
                    D_g = C_g
                    D_b = C_b
                elif A_h + 1 == self.biHeight:# 边界点
                    D_r = B_r
                    D_g = B_g
                    D_b = B_b
                else:
                    D_r = self.R[A_h + 1][A_w + 1]
                    D_g = self.G[A_h + 1][A_w + 1]
                    D_b = self.B[A_h + 1][A_w + 1]

                # 点E F的RGB
                E_r = (1 - distance_Aw) * A_r + distance_Aw * B_r
                E_g = (1 - distance_Aw) * A_g + distance_Aw * B_g
                E_b = (1 - distance_Aw) * A_b + distance_Aw * B_b
                F_r = (1 - distance_Aw) * C_r + distance_Aw * D_r
                F_g = (1 - distance_Aw) * C_g + distance_Aw * D_g
                F_b = (1 - distance_Aw) * C_b + distance_Aw * D_b

                # 点P的RGB
                P_r = (1 - distance_Ah) * E_r + distance_Ah * F_r
                P_g = (1 - distance_Ah) * E_g + distance_Ah * F_g
                P_b = (1 - distance_Ah) * E_b + distance_Ah * F_b

                new_bmp_data_row.append([int(P_b), int(P_g), int(P_r)])
            
            new_bmp_data.append(new_bmp_data_row)
        
        self.bmp_data = new_bmp_data
        self.biWidth = new_width
        self.biHeight = new_height
        self.biSizeImage = new_height * new_width * self.biBitCount
        self.bfSize = self.biSizeImage + 54

        self.RGB()

    def mirror(self):
        """镜像"""
        mirror_bmp_data = self.bmp_data.copy()

        for height in range(self.biHeight):
            mirror_bmp_data[height].reverse()       # 每行数据左右翻转

        self.bmp_data = mirror_bmp_data.copy()

        self.RGB()

    def rotate(self, degree):
        """旋转图像（图像错误）
        原理参考：https://blog.csdn.net/liyuan02/article/details/6750828
        :param degree: 旋转的度数
        """
        # 旋转角度的余弦/正弦值
        sin_degree = math.sin(math.radians(degree))
        cos_degree = math.cos(math.radians(degree))
        
        # 旋转后图像的宽和高（取绝对值后向上取整）
        new_width = math.ceil(abs(self.biHeight * sin_degree + self.biWidth * cos_degree))
        new_height = math.ceil(abs(self.biHeight * cos_degree + self.biWidth * sin_degree))

        dx = -0.5 * new_width * cos_degree - 0.5 * new_height * sin_degree + 0.5 * self.biWidth
        dy = 0.5 * new_width * sin_degree - 0.5 * new_height * cos_degree + 0.5 * self.biHeight

        self.RGB()  # 确保RGB是正确的

        new_bmp_data = []

        # 旋转后的图片的点(x, y)即(width, height)
        for height in range(new_height):
            new_bmp_data_row = []

            for width in range(new_width):
                # (x, y)对应于原图片的(x0, y0)即(original_w, original_h)
                original_w = width * cos_degree + height * sin_degree + dx
                original_h = -width * sin_degree + height * cos_degree + dy

                if original_w < self.biWidth and original_h < self.biHeight:
                    P_r = self.R[round(original_h)][round(original_w)]
                    P_g = self.G[round(original_h)][round(original_w)]
                    P_b = self.B[round(original_h)][round(original_w)]
                else:
                    P_r = 0
                    P_g = 0
                    P_b = 0

                new_bmp_data_row.append([int(P_b), int(P_g), int(P_r)])
            
            new_bmp_data.append(new_bmp_data_row)

        self.bmp_data = new_bmp_data.copy()
        self.biWidth = new_width
        self.biHeight = new_height
        self.biSizeImage = new_height * new_width * self.biBitCount
        self.biSize = self.biSizeImage + 54

        self.RGB()     

    def translation(self, dx, dy):
        """图像平移（改变图像大小）（生成的图片打不开）
        :param dx: x轴（即宽）方向移动距离，负数左移，正数右移
        :param dy: y轴（即高）方向移动距离，负数上移，正数下移
        """
        # 平移后图像的宽和高
        new_width = self.biWidth + abs(dx)
        new_height = self.biHeight + abs(dy)

        new_bmp_data = []

        for height in range(new_height):
            new_bmp_data_row = []

            # 上/下黑色填充
            if (dy > 0 and height < dy) or (dy < 0 and height >= self.biHeight):
                for width in range(new_width):
                    new_bmp_data_row.append([0, 0, 0])
            else:
                for width in range(new_width):
                    # 左/右填充
                    if(dx > 0 and width < dx) or (dx < 0 and width >= self.biWidth):
                        new_bmp_data_row.append([0, 0, 0])
                    else:
                        if dx > 0:
                            original_x = width - dx
                        else:
                            original_x = width
                        if dy > 0:
                            original_y = height - dy
                        else:
                            original_y = height
                        new_bmp_data_row.append([self.bmp_data[original_y][original_x][0], 
                                                self.bmp_data[original_y][original_x][1], 
                                                self.bmp_data[original_y][original_x][2]])
            
            new_bmp_data.append(new_bmp_data_row)

        self.bmp_data = new_bmp_data
        self.biWidth = new_width
        self.biHeight = new_height
        self.biSizeImage = new_height * new_width * self.biBitCount
        self.biSize = self.biSizeImage + 54

        self.RGB()

    def brightness(self, multiple):
        """调整图片亮度
        :param multiple: 亮度提高倍数(0-)（eg. 1.1，则RGB值变为原本的1.1倍，上下限分别为255和0）
        """
        for height in range(self.biHeight):
            for width in range(self.biWidth):
                self.bmp_data[height][width][0] = min(round(self.bmp_data[height][width][0] * multiple), 255)
                self.bmp_data[height][width][1] = min(round(self.bmp_data[height][width][1] * multiple), 255)
                self.bmp_data[height][width][2] = min(round(self.bmp_data[height][width][2] * multiple), 255)

        self.RGB()

    def contrast(self, contrast=50, threshold=50):
        """调整对比度
        原理参考：https://blog.csdn.net/maozefa/article/details/7069001
        :param contrast: 对比度增量
        :param threshold: 给定的阈值
        """
        for height in range(self.biHeight):
            for width in range(self.biWidth):
                if contrast == 255:
                    if self.bmp_data[height][width][0] >= threshold:
                        self.bmp_data[height][width][0] = 255
                    else:
                        self.bmp_data[height][width][0] = 0
                    if self.bmp_data[height][width][1] >= threshold:
                        self.bmp_data[height][width][1] = 255
                    else:
                        self.bmp_data[height][width][1] = 0
                    if self.bmp_data[height][width][2] >= threshold:
                        self.bmp_data[height][width][2] = 255
                    else:
                        self.bmp_data[height][width][2] = 0
                elif contrast > 0:
                    self.bmp_data[height][width][0] += round((self.bmp_data[height][width][0] - threshold) * (1 / (1 - contrast / 255) - 1))
                    self.bmp_data[height][width][1] += round((self.bmp_data[height][width][1] - threshold) * (1 / (1 - contrast / 255) - 1))
                    self.bmp_data[height][width][2] += round((self.bmp_data[height][width][2] - threshold) * (1 / (1 - contrast / 255) - 1))
                elif contrast <= 0:
                    self.bmp_data[height][width][0] += round((self.bmp_data[height][width][0] - threshold) * contrast / 255)
                    self.bmp_data[height][width][1] += round((self.bmp_data[height][width][1] - threshold) * contrast / 255)
                    self.bmp_data[height][width][2] += round((self.bmp_data[height][width][2] - threshold) * contrast / 255)
        
        self.RGB()


def i_to_bytes(number, length, byteorder='little'):
    """整型转字节型（字符）
    :param number: 待转换的整型
    :param length: 转换目标有多少个字符，只能多不能少，多了话，多余的字符会被十六进制的0填充，少了的话会报错
    :param byteorder: 大小端
    :return : 字符
    """
    return number.to_bytes(length, byteorder)


def bytes_to_i(mbytes, byteorder='little'):
    """字符转整型
    :param mbytes: 带转换的字符
    :param byteorder: 大小端
    :return : 整型
    """
    return int.from_bytes(mbytes, byteorder)


def main():
    # 命令行传入的文件路径
    # filePath = input('请输入图片名(.bmp)：')
    filePath = 'demo.bmp'

    # 读取BMP文件
    bmpFile = BMP()
    bmpFile.resolve(filePath)

    # R, G, B 三个通道 [0, 255]
    R = bmpFile.R
    G = bmpFile.G
    B = bmpFile.B

    # 显示图像
    b = np.array(B, dtype = np.uint8)
    g = np.array(G, dtype = np.uint8)
    r = np.array(R, dtype = np.uint8)
    merged = cv2.merge([b, g, r])   # 合并R、G、B分量 默认顺序为 B、G、R
    cv2.imshow(filePath, merged)

    cv2.waitKey(0)                  # 不加这行会窗口无响应或直接一闪而过 
    # 是一个和键盘绑定的函数，它的作用是等待一个键盘的输入
    # （因为我们创建的图片窗口如果没有这个函数的话会闪一下就消失了，所以如果需要让它持久输出，我们可以使用该函数）。
    # 它的参数是毫秒级。该函数等待任何键盘事件的指定毫秒。如果您在此期间按下任何键，程序将继续进行。我们也可以将其设置为一个特定的键。

    """
    # 图像缩放
    # 放大图像(程序运行需要几秒钟)
    bmpFile.zoom_in_and_out(1356, 1482)
    bmpFile.generate('large.bmp')

    # 缩小图像
    bmpFile.zoom_in_and_out(339, 370)
    bmpFile.generate('small.bmp')

    # 再放大图像
    bmpFile.zoom_in_and_out(452, 494)
    bmpFile.generate('2-3.bmp')

    # 变回原始大小
    bmpFile.zoom_in_and_out(678, 741)
    bmpFile.generate('normal.bmp')

    # 镜像
    bmpFile.mirror()
    bmpFile.generate('mirror.bmp')
    """

    # 旋转
    # bmpFile.rotate(90)  # 旋转30°
    # bmpFile.generate('rotate.bmp')

    # 平移
    # bmpFile.translation(50, 50)
    # bmpFile.generate('translation.bmp')

    """
    # 调整图片亮度
    # 调整亮度为1.5倍
    bmpFile.brightness(1.5)
    bmpFile.generate('brightness.bmp')
    
    # 调整图片对比度
    bmpFile.contrast(255, 120)
    bmpFile.generate('contrast.bmp')
    """


if __name__ == '__main__':
    main()