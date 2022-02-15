import cv2
import glob
import re
import os
import numpy as np
import sys
from tqdm import tqdm

def read_img(path,color,dirpath,fps,height,width):
  mov = cv2.VideoCapture(path)
  rate = fps
  n = 0
  while True:
    ret, frameImg = mov.read()
    if rate == 120:
      n += 1
      if n%2 == 0:
        ret, frameImg = mov.read()
    if rate == 60:
      n += 1
      if n%4 == 0:
        ret, frameImg = mov.read()
    if ret:
      reImg = cv2.resize(frameImg, dsize=(width, height))
      write_data = mpeg2yuv(reImg,path,dirpath,color)
      if color == 444 or color == 400:
        write_yuv(*write_data)
    else:
      return

def mpeg2yuv(img,path,dir_path,color):
  height,width,c = img.shape
  b,g,r = img[:,:,0], img[:,:,1], img[:,:,2]
  cal_arr = np.array([[0.256788,0.504129,0.097906],
                      [0.148223,0.290993,0.439216],
                      [0.439216,0.367788,0.071427]])
  if color == 444:
    y = (cal_arr[0,0]*r+cal_arr[0,1]*g+cal_arr[0,2]*b).astype(np.uint8)+16
    u = ((-1)*cal_arr[1,0]*r-cal_arr[1,1]*g+cal_arr[1,2]*b).astype(np.uint8)+128
    v = (cal_arr[2,0]*r-cal_arr[2,1]*g-cal_arr[2,2]*b).astype(np.uint8)+128
    yuv = np.r_["0",y,u,v]
    return path, dir_path, yuv, str(width), str(height), str(color)
  elif color == 422:
    y = (cal_arr[0,0]*r+cal_arr[0,1]*g+cal_arr[0,2]*b).astype(np.uint8)+16
    u = ((-1)*cal_arr[1,0]*r-cal_arr[1,1]*g+cal_arr[1,2]*b).astype(np.uint8)+128
    v = (cal_arr[2,0]*r-cal_arr[2,1]*g-cal_arr[2,2]*b).astype(np.uint8)+128
    u = np.delete(u,slice(None,None,2),axis=1)
    v = np.delete(v,slice(None,None,2),axis=1)
    write_yuv(path,dir_path,y,str(width),str(height),str(color))
    write_yuv_(path,dir_path,u,str(width),str(height),str(color))
    write_yuv_(path,dir_path,v,str(width),str(height),str(color))
    return
  elif color == 420:
    y = (cal_arr[0,0]*r+cal_arr[0,1]*g+cal_arr[0,2]*b).astype(np.uint8)+16
    u = ((-1)*cal_arr[1,0]*r-cal_arr[1,1]*g+cal_arr[1,2]*b).astype(np.uint8)+128
    v = (cal_arr[2,0]*r-cal_arr[2,1]*g-cal_arr[2,2]*b).astype(np.uint8)+128
    u = np.delete(u,slice(None,None,2),axis=1)
    v = np.delete(v,slice(None,None,2),axis=1)
    u = np.delete(u,slice(None,None,2),axis=0)
    v = np.delete(v,slice(None,None,2),axis=0)
    write_yuv(path,dir_path,y,str(width),str(height),str(color))
    write_yuv_(path,dir_path,u,str(width),str(height),str(color))
    write_yuv_(path,dir_path,v,str(width),str(height),str(color))
    return
  else:
    y = (cal_arr[0,0]*r+cal_arr[0,1]*g+cal_arr[0,2]*b).astype(np.uint8)+16
    return path, dir_path, y, str(width), str(height), str(color)

def write_yuv(img_path,dir_path,yuv,w,h,c):
  img_path_re = os.path.split(img_path)[1].rstrip('.JPG')
  img_new_path = dir_path + re.sub("\..*$", "", img_path_re) +'('+w+'x'+h+',YUV'+c+').yuv'
  with open(img_new_path,'ab') as f:
    f.write(yuv)

def write_yuv_(img_path,dir_path,yuv,w,h,c):
  img_path_re = os.path.split(img_path)[1].rstrip('.JPG')
  img_new_path = dir_path + re.sub("\..*$", "", img_path_re) +'('+w+'x'+h+',YUV'+c+').yuv'
  with open(img_new_path,'ab') as f:
    f.write(yuv)

def main(color,fps,height,width):
  new_dir_name = '../movie_yuv/'
  isfile1 = '../movie_yuv'
  isfile2 = '../movie_original'
  movie_path = '../movie_original/*'
  # path founding
  er = 'ERROR: Path Not Found. Create the directory and exit.'
  if (os.path.isdir(isfile1) == False or
    os.path.isdir(isfile2) == False):
    if (os.path.isdir(isfile1) == False and
      os.path.isdir(isfile2) == False):
      os.mkdir(isfile1)
      os.mkdir(isfile2)
      print(er)
      sys.exit()
    elif os.path.isdir(isfile1) == False:
      os.mkdir(isfile1)
      print(er)
      sys.exit()
    else:
      os.mkdir(isfile2)
      print(er)
      sys.exit()
  files = glob.glob(movie_path)
  if len(files) == 0:
    print('INFO: MOVIES NOT FOUND.')
    sys.exit()
  for file in tqdm(files, desc='MPEG 2 YUV'+str(color)+' Processing',position=0,leave=False):
    read_img(file, color, new_dir_name,fps,height,width)
  print('COMPLETED')

if __name__ == '__main__':
  # ERROR output
  er = '''
  ERROR: Incorrect argument entered. Please enter CORRECT argument.
  Correct command: python jpgxyuv.py [YUV-format] [fps] [height] [width]
  ex) python jpgxyuv.py 444 60 720 480
    - 444 : JPEG convert to YUV444 (4:4:4)
    - 422 : JPEG convert to YUV422 (4:2:2)
    - 420 : JPEG convert to YUV420 (4:2:0)
    - 400 : JPEG convert to YUV400 (4:0:0)
  [fps = 60] -> 60fps movie file convert to 30fps YUV movie file.
  [fps = 120] -> 120fps movie file convert to 30fps YUV movie file.
  [fps = otherwise] -> Convert to Same fps YUV movie file. 
  '''
  arglen = sys.argv
  if len(arglen) < 2:
    print(er)
    exit()
  c = int(arglen[1])
  f = int(arglen[2])
  h = int(arglen[3])
  w = int(arglen[4])
  if (c == 444 or c == 422 or c == 420 or c == 400):
    main(c,f,w,h)
    sys.exit()
  else:
    print(er)
    sys. exit()
