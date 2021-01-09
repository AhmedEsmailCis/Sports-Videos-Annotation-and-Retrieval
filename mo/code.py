import cv2
import matplotlib.pyplot as plt
import numpy as np
from numpy import array
import glob
from os import listdir
import os
import sys
import threading
import time
#############################################################################################
semaphore = threading.Semaphore(1)
###############################################################################################
def GetImageDescriptor(frame):
    # Initiate SIFT detector
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sift = cv2.xfeatures2d.SIFT_create()
    # find the keypoints and descriptor with SIFT
    kp, desc = sift.detectAndCompute(gray,None)
    return desc
####################################################################################################
def GetVideoDescriptors(VideoName):
    DescriptorList=[]
    capture = cv2.VideoCapture(VideoName)
    #Num Of Frame Per Second (frameRate)
    frameRate = int(capture.get(cv2.CAP_PROP_FPS)) - 1
    FramePtr = 0    #in first Frame
    while capture.isOpened():
        #Set capture in Frame Position >> FramePtr
        capture.set(cv2.CAP_PROP_POS_FRAMES, FramePtr)
        flag, Frame = capture.read()
        if flag == False:
            break
        Descriptor=GetImageDescriptor(Frame)
        DescriptorList.append(Descriptor)
        FramePtr=FramePtr+frameRate
    semaphore.acquire()
    VideosNames1.append(VideoName)
    VideosFeatures.append(DescriptorList)
    print(VideoName)
    print("**********")
    semaphore.release()
    return DescriptorList
##############################################################################################
def FeatureMatching(imageFeature,FeatureOfVideo,VideoName):
    # create BFMatcher object
    bf = cv2.BFMatcher()
    NumOfGoodPoint=[]
    GoodPoint = []
    ratio = 0.6     # match for 60/100
    for feature in FeatureOfVideo:
        # Match descriptors.
        matches = bf.knnMatch(imageFeature, feature,k=2)
        for C1,C2 in matches:
            if C1.distance < ratio * C2.distance:
                GoodPoint.append(C1)
        NumOfGoodPoint.append(len(GoodPoint))
        GoodPoint.clear()
    # Return maximum Num Of good Point
    semaphore.acquire()
    VideosNames2.append(VideoName)
    GoodPointsOfVideo.append(max(NumOfGoodPoint))
    semaphore.release()
    return max(NumOfGoodPoint)
##############################################################################################
def Show_video(Video_path):
    capture = cv2.VideoCapture(Video_path)
    while capture.isOpened():
        flag, Frame = capture.read()
        if flag == False:
            break
        cv2.imshow('video', Frame)
        cv2.waitKey(27)
##############################################################################################
def ExtractFeaturesFromVideos(ListOfVideosName):
    for video in ListOfVideosName:
        t = threading.Thread(target=GetVideoDescriptors, args=(video,))
        t.daemon = True
        t.start()
        threads.append(t)
    for x in threads:  # Wait for all of threads to finish
        x.join()
    threads.clear()
##############################################################################################
def Search(imageFeature):
    for i in range(0, len(VideosNames1)):
        t = threading.Thread(target=FeatureMatching, args=(imageFeature, VideosFeatures[i], VideosNames1[i],))
        t.daemon = True
        t.start()
        threads.append(t)

    for x in threads:  # Wait for all of threads to finish
        x.join()
    threads.clear()
##############################################################################################
def RankingTheVideos():
    GoodPointsOfVideo[::-1], VideosNames2[::-1] = zip(*sorted(zip(GoodPointsOfVideo, VideosNames2)))  # ranking Videos
##############################################################################################
def main():
    global VideosFeatures, VideosNames1, threads, GoodPointsOfVideo, VideosNames2
    VideosNames1 = []
    VideosFeatures = []
    threads = []
    GoodPointsOfVideo = []
    VideosNames2 = []
    videos_name = ['D:/uploaded_videos/GoalSalahInMC.mp4','D:/uploaded_videos/GoalAboTrakaInOrlando.mp4','D:/uploaded_videos/GoalMessiInRB.mp4','D:/uploaded_videos/GoalCr7InBarchalona.mp4']
    ExtractFeaturesFromVideos(videos_name)
    image = cv2.imread('D:\search_images\GoalAboTrakaInOrlando.png')
    Features1 = GetVideoDescriptors(videos_name[0])   # Descriptors for Video 1
    Features2 = GetVideoDescriptors(videos_name[1])   # Descriptors for Video 2
    Features3 = GetVideoDescriptors(videos_name[2])   # Descriptors for Video 3
    Features4 = GetVideoDescriptors(videos_name[3])   # Descriptors for Video 4
    #.............................................................
    imageFeature = GetImageDescriptor(image)  # Descriptors for Image
    numOfGoodPoint1 = FeatureMatching(imageFeature, Features1,videos_name[0])
    numOfGoodPoint2 = FeatureMatching(imageFeature, Features2,videos_name[1])
    numOfGoodPoint3 = FeatureMatching(imageFeature, Features3,videos_name[2])
    numOfGoodPoint4 = FeatureMatching(imageFeature, Features4,videos_name[3])

    print(numOfGoodPoint1)
    print(numOfGoodPoint2)
    print(numOfGoodPoint3)
    print(numOfGoodPoint4)

    Show_video(videos_name[1])
    cv2.destroyAllWindows()
    print("Program Finished")
#########################################################################################################
if __name__ == '__main__':
    main()









