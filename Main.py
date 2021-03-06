# Udacity Project: Advance Lane Finding. Main Function.
# Developed by Haowei Zhao, Oct, 2018.
# The pipeline only works with 720p video.
import numpy as np
import cv2
from utils.Calibartion import *
from utils.Convert2Binary import *
from utils.PerspectiveTrans import *
from utils.FindLane import *
from utils.DrawText import *
from moviepy.editor import VideoFileClip
from utils.Memory import *
import operator
from utils.CalculateRedius import *


str_l1 = plt.imread("test_images/straight_lines1.jpg")
str_l2 = plt.imread("test_images/straight_lines2.jpg")
test1 = plt.imread('test_images/test1.jpg')
test2 = plt.imread('test_images/test2.jpg')
test3 = plt.imread('test_images/test3.jpg')
test4 = plt.imread('test_images/test4.jpg')
test5 = plt.imread('test_images/test5.jpg')
test6 = plt.imread('test_images/test6.jpg')
chllenge = plt.imread('challenge_images/challenge.jpg')
# This is just for testing purpose
# project_1 = plt.imread('test_images/001.jpg')
# project_2 = plt.imread('test_images/002.jpg')
# project_3 = plt.imread('test_images/003.jpg')

## Initial parameters
# Convert pixel to meter to calculate radius of the lane
ym_per_pix = 30 / 720
xm_per_pix = 3.7 / 700
# Threshold of polynomial coefficient. For smoothing purpose
MAX_DIFF_0 = 5*10**-2
MAX_DIFF_1 = 20
MAX_DIFF_2 = 200
# Threshold of polynomial coefficient in meters. For smoothing purpose
MAX_DIFF_0_REAL = MAX_DIFF_0*(xm_per_pix**2/ym_per_pix)*10*2
MAX_DIFF_1_REAL = MAX_DIFF_1*(xm_per_pix/ym_per_pix)*10*2
MAX_DIFF_2_REAL = 2/ym_per_pix

class AdvanceLaneDetect:
    def __init__(self):
        self.objPoints, self.imgPoints = Derive_Points_from_board()
        # The deque of left and right lane
        self.left_lane_que = creat_lane_list()
        self.right_lane_que = creat_lane_list()
        # The deque of left and right lane in meters
        self.left_lane_que_real = creat_lane_list_real()
        self.right_lane_que_real = creat_lane_list_real()
        # Left and right lane polynomial coefficients.
        self.left_fit = None
        self.right_fit = None
        # Left and right lane polynomial coefficients in meters
        self.left_fit_real = None
        self.right_fit_real = None

    def image_pipline(self,img):
        # Undistort the image
        unDist = Undistort(img, self.objPoints, self.imgPoints)
        plt.imsave('output_images/test1_unDistorted.png',unDist)
        # Binary = Convert2Binary_LAB_L(unDist) # Uncomment this if you want to use LAB color space
        # Create a binary image that highlights the left and right lane
        Binary = Convert2Binary_Sobel_S(unDist)
        plt.imsave('output_images/test1_Binary.png', Binary)
        # Transfer the perspective to bird eye view
        Warped = PerspectiveTrans(Binary)
        plt.imsave('output_images/test1_Warped.png', Warped)

        window_width = 50
        window_height = 80
        margin = 80
        # Highlight the left and right lane using convolution
        left_lane_x, left_lane_y, right_lane_x, right_lane_y, masked_Warped, bottom_lane_position = draw_lane_pix(Warped,
                                                                                                                  window_width,
                                                                                                                  window_height,
                                                                                                                  margin)

        plt.imsave('output_images/test1_masked_Warped.png', masked_Warped)

        # Fit a second order polynomial on the masked and warped image
        polyfit_image, self.left_fit, self.right_fit, = fit_poly(left_lane_x, left_lane_y,right_lane_x, right_lane_y,masked_Warped)
        plt.imsave('output_images/test1_polyfit_Warped.png', polyfit_image)
        # To calculate the real radius, we need to fit a polynomial in meters
        polyfit_image_real, self.left_fit_real, self.right_fit_real = fit_poly_real(left_lane_x, left_lane_y,
                                                                                    right_lane_x, right_lane_y,
                                                                                    masked_Warped)

        # Calculate the lane position at the bottom. This would help us to calculate the offset between car position and lane center
        left_bottom = bottom_lane_position[0][0]
        right_bottom = bottom_lane_position[0][1]
        bottom_lane_position=[left_bottom,right_bottom]
        # Unwarp the binary image back to original perspective
        Unwarped_with_lane = unwarp_with_lane(Warped, self.left_fit, self.right_fit)
        # Draw the original result
        left_R, right_R = CalculateRadius(self.left_fit_real,self.right_fit_real,masked_Warped)
        result = cv2.addWeighted(unDist, 1, Unwarped_with_lane, 0.3, 0)
        result = DrawText(result, left_R, right_R, bottom_lane_position)

        return result


    ## Todo: this pipline is designed for challange video, where we should use only color to identify the lane.
    def image_challenge_pipline(self,img):
        unDist = Undistort(img, self.objPoints, self.imgPoints)
        plt.imsave('challenge_outputs/challenge_unDistorted.png',unDist)
        Binary = Convert2Binary_LAB_L(unDist)# Use LAB color space.

        plt.imsave('challenge_outputs/challenge_Binary.png', Binary)

        Warped = PerspectiveTrans(Binary)
        plt.imsave('challenge_outputs/challenge_Warped.png', Warped)

        window_width = 50
        window_height = 80
        margin = 80
        left_lane_x, left_lane_y, right_lane_x, right_lane_y, masked_Warped, bottom_lane_position = draw_lane_pix(Warped,
                                                                                                                  window_width,
                                                                                                                  window_height,
                                                                                                                  margin)

        plt.imsave('challenge_outputs/challenge_masked_Warped.png', masked_Warped)


        polyfit_image, self.left_fit, self.right_fit, = fit_poly(left_lane_x, left_lane_y,right_lane_x, right_lane_y,masked_Warped)

        plt.imsave('challenge_outputs/challenge_polyfit_Warped.png', polyfit_image)

        polyfit_image_real, self.left_fit_real, self.right_fit_real = fit_poly_real(left_lane_x, left_lane_y,
                                                                                    right_lane_x, right_lane_y,
                                                                                    masked_Warped)

        left_bottom = bottom_lane_position[0][0]
        right_bottom = bottom_lane_position[0][1]
        bottom_lane_position=[left_bottom,right_bottom]


        Unwarped_with_lane = unwarp_with_lane(Warped, self.left_fit, self.right_fit)

        left_R, right_R = CalculateRadius(self.left_fit_real,self.right_fit_real,masked_Warped)
        result = cv2.addWeighted(unDist, 1, Unwarped_with_lane, 0.3, 0)
        result = DrawText(result, left_R, right_R, bottom_lane_position)

        return result

    # Vedio piplane
    def video_pipline(self,img):
        unDist = Undistort(img, self.objPoints, self.imgPoints)
        Binary = Convert2Binary_Sobel_S(unDist)

        Warped = PerspectiveTrans(Binary)

        window_width = 50
        window_height = 80
        margin = 80
        # Search around the first position
        left_lane_x, left_lane_y, right_lane_x, right_lane_y, masked_Warped, bottom_lane_position = draw_lane_pix(Warped,
                                                                                                                  window_width,
                                                                                                                  window_height,
                                                                                                                  margin)


        left_bottom = bottom_lane_position[0][0]
        right_bottom = bottom_lane_position[0][1]

        # Check if it is a bad frame. If it is a bad frame, then use mean value of in the memory
        if len(self.left_lane_que) == 0 and len(self.right_lane_que) == 0:
            # This is the first frame
            polyfit_image, self.left_fit, self.right_fit = fit_poly(left_lane_x, left_lane_y,
                                                                                  right_lane_x, right_lane_y,
                                                                                  masked_Warped)

            polyfit_image_real, self.left_fit_real, self.right_fit_real = fit_poly_real(left_lane_x, left_lane_y,
                                                                    right_lane_x, right_lane_y,
                                                                    masked_Warped)


            self.left_lane_que = left_lane_add(self.left_lane_que,self.left_fit,left_bottom)
            self.right_lane_que = right_lane_add(self.right_lane_que,self.right_fit,right_bottom)

            self.left_lane_que_real = left_lane_add(self.left_lane_que_real, self.left_fit_real, left_bottom)
            self.right_lane_que_real = right_lane_add(self.right_lane_que_real, self.right_fit_real, right_bottom)

            left_fit_mean, left_bottom_mean = left_lane_mean(self.left_lane_que)
            right_fit_mean, right_bottom_mean = right_lane_mean(self.right_lane_que)

            left_fit_mean_real, left_bottom_mean = left_lane_mean(self.left_lane_que_real)
            right_fit_mean_real, right_bottom_mean = right_lane_mean(self.right_lane_que_real)

        else:
            # For the rest of the frame , we can search around the lane base to identify the lane pixels. This would help reduce the noise.
            left_lane_x, left_lane_y, right_lane_x,right_lane_y = search_around_poly(masked_Warped,self.left_fit, self.right_fit,window_width)
            polyfit_img, self.left_fit, self.right_fit = fit_poly(left_lane_x, left_lane_y, right_lane_x, right_lane_y,masked_Warped)

            polyfit_image_real, self.left_fit_real, self.right_fit_real = fit_poly_real(left_lane_x, left_lane_y,
                                                                    right_lane_x, right_lane_y,
                                                                    masked_Warped)


            left_fit_mean, left_bottom_mean = left_lane_mean(self.left_lane_que)
            right_fit_mean, right_bottom_mean = right_lane_mean(self.right_lane_que)

            left_fit_mean_real, left_bottom_mean = left_lane_mean(self.left_lane_que_real)
            right_fit_mean_real, right_bottom_mean = right_lane_mean(self.right_lane_que_real)

            # The diff of image poly
            left_fit_diff = list(map(operator.sub,self.left_fit,left_fit_mean))
            right_fit_diff = list(map(operator.sub,self.right_fit,right_fit_mean))
            # Drive the absolute value
            left_fit_diff = [abs(x) for x in left_fit_diff]
            right_fit_diff = [abs(y) for y in right_fit_diff]

            # The diff of real poly
            left_fit_diff_real = list(map(operator.sub,self.left_fit_real,left_fit_mean_real))
            right_fit_diff_real = list(map(operator.sub,self.right_fit_real,right_fit_mean_real))
            # Drive the absolute value
            left_fit_diff_real = [abs(x) for x in left_fit_diff_real]
            right_fit_diff_real = [abs(y) for y in right_fit_diff_real]

            # If it is a good frame, then append it to the deque and use mean values
            if left_fit_diff[0] < MAX_DIFF_0 and left_fit_diff[1] < MAX_DIFF_1 and left_fit_diff[2] < MAX_DIFF_2:
                self.left_lane_que = left_lane_add(self.left_lane_que, self.left_fit, left_bottom)
                left_fit_mean, left_bottom_mean = left_lane_mean(self.left_lane_que)

            if right_fit_diff[0] < MAX_DIFF_0 and right_fit_diff[1] < MAX_DIFF_1 and right_fit_diff[2] < MAX_DIFF_2:
                self.right_lane_que = right_lane_add(self.right_lane_que, self.right_fit, right_bottom)
                right_fit_mean, right_bottom_mean = right_lane_mean(self.right_lane_que)

            if left_fit_diff_real[0] < MAX_DIFF_0_REAL and left_fit_diff_real[1] < MAX_DIFF_1_REAL and left_fit_diff_real[2] < MAX_DIFF_2_REAL:
                self.left_lane_que_real = left_lane_add(self.left_lane_que_real, self.left_fit_real, left_bottom)
                left_fit_mean_real, left_bottom_mean= left_lane_mean(self.left_lane_que_real)

            if right_fit_diff_real[0] < MAX_DIFF_0_REAL and right_fit_diff_real[1] < MAX_DIFF_1_REAL and right_fit_diff_real[2] < MAX_DIFF_2_REAL:
                self.right_lane_que_real = right_lane_add(self.right_lane_que_real, self.right_fit_real, right_bottom)
                right_fit_mean_real, right_bottom_mean = right_lane_mean(self.right_lane_que_real)

        bottom_lane_position=[left_bottom_mean,right_bottom_mean]

        Unwarped_with_lane = unwarp_with_lane(Warped, left_fit_mean, right_fit_mean)
        left_R, right_R = CalculateRadius(left_fit_mean_real,right_fit_mean_real,masked_Warped)
        result = cv2.addWeighted(unDist, 1, Unwarped_with_lane, 0.3, 0)
        result = DrawText(result, left_R, right_R, bottom_lane_position)

        return result


AdvanceLaneDetect_image = AdvanceLaneDetect()
Final_str_l1 = AdvanceLaneDetect_image.image_pipline(str_l1)
plt.imsave('output_images/straight_lines1.png',Final_str_l1)
Final_str_l2 = AdvanceLaneDetect_image.image_pipline(str_l2)
plt.imsave('output_images/straight_lines2.png',Final_str_l2)
Final_test1 = AdvanceLaneDetect_image.image_pipline(test1)
plt.imsave('output_images/test1.png',Final_test1)
Final_test2 = AdvanceLaneDetect_image.image_pipline(test2)
plt.imsave('output_images/test2.png',Final_test2)
Final_test3 = AdvanceLaneDetect_image.image_pipline(test3)
plt.imsave('output_images/test3.png',Final_test3)
Final_test4 = AdvanceLaneDetect_image.image_pipline(test4)
plt.imsave('output_images/test4.png',Final_test4)
Final_test5 = AdvanceLaneDetect_image.image_pipline(test5)
plt.imsave('output_images/test5.png',Final_test5)
Final_test6 = AdvanceLaneDetect_image.image_pipline(test6)
plt.imsave('output_images/test6.png',Final_test6)
Final_challenge = AdvanceLaneDetect_image.image_challenge_pipline(chllenge)
plt.imsave('challenge_outputs/challenge.png',Final_challenge)

## This is just for testing purpose
# Final_project_1 = AdvanceLaneDetect_image.image_pipline(project_1)
# plt.imsave('output_images/001.png',Final_project_1)
# Final_project_2 = AdvanceLaneDetect_image.image_pipline(project_2)
# plt.imsave('output_images/002.png',Final_project_2)
# Final_project_3 = AdvanceLaneDetect_image.image_pipline(project_3)
# plt.imsave('output_images/003.png',Final_project_3)

# The project video
Detect = AdvanceLaneDetect()
white_output = 'video_output/project_video.mp4'
clip1 = VideoFileClip('project_video.mp4')
white_clip = clip1.fl_image(Detect.video_pipline) #NOTE: this function expects color images!!
white_clip.write_videofile(white_output, audio=False)

# The challenge video
Detect_ch = AdvanceLaneDetect()
white_output = 'video_output/challenge_video.mp4'
clip1 = VideoFileClip('challenge_video.mp4')
white_clip = clip1.fl_image(Detect_ch.video_pipline) #NOTE: this function expects color images!!
white_clip.write_videofile(white_output, audio=False)

# The harder challenge video
Detect_harder_ch = AdvanceLaneDetect()
white_output = 'video_output/harder_challenge_video.mp4'
clip1 = VideoFileClip('harder_challenge_video.mp4')
white_clip = clip1.fl_image(Detect_harder_ch.video_pipline) #NOTE: this function expects color images!!
white_clip.write_videofile(white_output, audio=False)