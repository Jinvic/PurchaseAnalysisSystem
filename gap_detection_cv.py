import cv2
import math

GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)  # 高斯内核大小
GAUSSIAN_BLUR_SIGMA_X = 0  # 高斯内核X方向上标准偏差
CANNY_THRESHOLD1 = 200  # 最小判定临界点
CANNY_THRESHOLD2 = 450  # 最大判定临界点
ALLOWABLE_ERROR = 0.1  # 允许误差范围为10%


# 高斯滤波
def get_gaussian_blur_image(image):
    return cv2.GaussianBlur(src=image,
                            ksize=GAUSSIAN_BLUR_KERNEL_SIZE,
                            sigmaX=GAUSSIAN_BLUR_SIGMA_X)


# 边缘检测
def get_canny_image(image):
    return cv2.Canny(image=image,
                     threshold1=CANNY_THRESHOLD1,
                     threshold2=CANNY_THRESHOLD2)


# 轮廓提取
def get_contours(image):
    contours, _ = cv2.findContours(
        image=image,
        mode=cv2.RETR_CCOMP,  # 轮廓检索方式-检测所有的轮廓，只建立两个等级关系，顶层为连通域的外围边界，次层为洞的内层边界
        method=cv2.CHAIN_APPROX_SIMPLE  # 轮廓近似方式-仅保存轮廓的拐点信息
    )
    return contours


# 计算矩形大小
def get_area(height, width):
    area = height*width
    return area


# 计算矩形周长
def get_length(height, width):
    length = (height+width)*2
    return length


# 判断缺口是否为矩形
def is_square(height, width):
    error = abs(height-width)/width
    if (error < 0.05):
        return True
    else:
        return False


# 缺口检测算法，返回偏移量
def gap_detection():
    image_raw = cv2.imread('bigimg.png')  # 读取原始图片
    image_gaussian_blur = get_gaussian_blur_image(image_raw)  # 高斯滤波处理
    image_canny = get_canny_image(image_gaussian_blur)  # 边缘检测处理
    contours = get_contours(image_canny)  # 轮廓提取处理
    cv2.imwrite('image_canny.png', image_canny)
    cv2.imwrite('image_gaussian_blur.png', image_gaussian_blur)

    image_slide = cv2.imread('smallimg.png')  # 读取滑块图片
    slide_height, slide_width, _ = image_slide.shape  # 获取宽高信息
    target_area = get_area(slide_height, slide_width)  # 目标面积
    target_length = get_length(slide_height, slide_width)  # 目标周长
    offset = None
    for contour in contours:  # 遍历轮廓
        x, y, w, h = cv2.boundingRect(contour)
        contour_area = get_area(h, w)  # 轮廓面积
        contour_length = get_length(h, w)  # 轮廓周长
        area_error = abs((contour_area-target_area)/target_area)
        length_error = abs((contour_length-target_length)/target_length)
        if is_square(h, w) and area_error <= ALLOWABLE_ERROR and length_error <= ALLOWABLE_ERROR:
            cv2.rectangle(image_raw, (x, y), (x + w, y + h), (0, 0, 255), 2)
            offset = x
    cv2.imwrite('image_label.png', image_raw)
    print('offset', offset)
    # cv2.imshow('result', image_raw)
    # cv2.waitKey(500)
    # cv2.destroyAllWindows()

    # 原图大小和渲染大小不一致，需要等比换算。
    if offset != None:
        _, image_width, _ = image_raw.shape  # 原图宽度
        render_width = 242  # 渲染宽度
        offset = math.ceil(offset*(render_width/image_width))

    # TODO 检测失败处理
    return offset


# if __name__ == '__main__':
#     gap_detection()
