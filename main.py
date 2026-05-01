#%% EVERYTHING
import cv2
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import os
import math
import re
from time import sleep
from tqdm.auto import tqdm
from playsound3 import playsound

# Grab suitable images from gifs
# for image_path in os.listdir('assets\gif'):
#     with Image.open('assets/gif/'+image_path) as im:
#         im.seek(5)
#         im.save('assets/png/{}.png'.format(image_path.replace(".gif","")))

# This might be ported to another language.

# image_path = 'assets/jpg/sonic.jpg'
# image = cv2.imread(image_path)
# h, w = image.shape[:2]
# # fig, axs = plt.subplots(2,2,figsize=(9,9))

# # Original Image
# image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# # axs[0][0].imshow(image_rgb)
# # axs[0][0].set_title('Original Image')

# # Gaussian Blur
# Gaussian = cv2.GaussianBlur(image, (15, 15), 0)
# Gaussian_rgb = cv2.cvtColor(Gaussian, cv2.COLOR_BGR2RGB)  
# # axs[0][1].imshow(Gaussian_rgb)
# # axs[0][1].set_title('Gaussian Blur')
# cv2.imwrite('output/gaussian/sonic.png',Gaussian)

# # Median Blur
# median = cv2.medianBlur(image, 11)  
# median_rgb = cv2.cvtColor(median, cv2.COLOR_BGR2RGB)  
# # axs[1][0].imshow(median_rgb)
# # axs[1][0].set_title('Median Blur')
# cv2.imwrite('output/median/sonic.png',median)

# # Simulate green phosphor: Keep only green channel, make others 0
# # green_phosphor = image.copy()
# # green_phosphor[:, :, 0] = 0 # Blue
# # green_phosphor[:, :, 2] = 0 # Red
# # Add slight blur to simulate glow

def apply_scanlines(img, interval, offset=0, vertical=False, color=(25,0,0),thickness=1,inplace=True):
    if not inplace: img = img.copy()
    h,w = img.shape[:2]
    if vertical:
        for i in range(w//interval):
            img = cv2.line(img, (i*interval+offset,0), (i*interval+offset,w),color,thickness)
    else:
        for i in range(h//interval):
            img = cv2.line(img, (0,i*interval+offset), (w,i*interval+offset),color,thickness)
    return img

def overlayImages(img1,img2,weight1):
    return cv2.addWeighted(img1,weight1,img2,1-weight1, 0)

def save_img(folder_path, img_name, img, verbose=True):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    cv2.imwrite(folder_path+"/"+img_name, img)
    if verbose: print("image saved at '"+folder_path+"/"+img_name+"'")

def get_img_size(img):
    return img.shape[:2] # height, width

def apply_crt_filter(filepath, scale = 1, blur=True, scanlines=True):
    filename = re.sub(r'(^.*/)|(\..*)', '', filepath)
    img = cv2.imread(filepath)
    # Resize image
    height, width = img.shape[:2]
    new_h, new_w = 0,0
    if 0 < scale and scale < 1 and type(scale) == float:
        new_h = (int)(height/scale)
        new_w = (int)(width/scale)
    else:
        new_h = height//scale
        new_w = width//scale
    img = cv2.resize(img, (new_w,new_h), interpolation=cv2.INTER_NEAREST)
    # height, width = new_h, new_w
    # Increase saturation
    # imghsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype("float32")
    # (h, s, v) = cv2.split(imghsv)
    # s = s*1.25
    # s = np.clip(s,0,255)
    # imghsv = cv2.merge([h,s,v])
    # imgrgb = cv2.cvtColor(imghsv.astype("uint8"), cv2.COLOR_HSV2BGR)
    # Create copy to edit with
    # img_crt = imgrgb.copy()
    img_crt = img.copy()
    # Apply vertical scanlines
    # interval2 = 3
    # for i in range(width//interval2):
    #     img_crt = cv2.line(img_crt, (i*interval2+interval2//2,0), (i*interval2+interval2//2,height),(0,0,0), 1)

    
    # num = 10
    # alpha = 0.05
    # offset division = 5
    
    # if blur:
    #     img_crt = cv2.blur(img_crt, (2,1))

    # Apply basic scanlines
    for i in range(height//2):
        img_crt = cv2.line(img_crt, (0,i*2), (width,i*2),(0,0,0),1)
    # Upscale to twice its regular resolution for subpixel detail
    img_crt = cv2.resize(img_crt, (width*2,height*2), interpolation=cv2.INTER_NEAREST)
    # Apply blur to simulate dithering
    img_crt = cv2.GaussianBlur(img_crt,(7,1),1.5)
    img_crt = cv2.GaussianBlur(img_crt,(1,3),0)

    # # Apply horizontal scanlines
    # if scanlines:
    #     overlay = img_crt.copy()
    #     num = 8
    #     alpha = 0.05
    #     for i in range(num+1):
    #         temp = apply_scanlines(overlay,num,inplace=False,offset=num-i)
    #         offset = (num-i)/12
    #         img_crt = cv2.addWeighted(temp, alpha+offset, img_crt, 1-alpha-offset, 0)
    

    # Apply blur
    # img_crt = cv2.GaussianBlur(img_crt, (5,1),1)

    
    # Apply small blur on scanlines
    # size = 3
    # img_crt = cv2.GaussianBlur(img_crt, (size,size), 0.6)
    # # Apply contrast
    # lab= cv2.cvtColor(img_crt, cv2.COLOR_BGR2LAB)
    # l_channel, a, b = cv2.split(lab)
    # clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8,8))

    # cl = clahe.apply(l_channel)
    # limg = cv2.merge((cl,a,b))
    # enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    # img_crt = np.hstack((img_crt, enhanced_img))
    # weight1 = 2.5
    # img_crt = cv2.addWeighted(img_crt, weight1, imgrgb, 0, -50)
    # TODO: blur horizontally more than vertically

    # split into colors
    # blue,green,red = cv2.split(img_crt)
    # size,weight = (3,1),0.5
    # blue = cv2.GaussianBlur(blue,size,weight)
    # green = cv2.GaussianBlur(green,size,weight)
    # red = cv2.GaussianBlur(red,size,weight)
    # img_crt = cv2.merge([blue,green,red])
    
    # img_bilateral = cv2.bilateralFilter(img_crt,5,150,150)
    # img_bilateral = cv2.GaussianBlur(img_crt,(3,1),0.6)
    # img_crt = overlayImages(img_crt,img_bilateral,0)

    # Resize back to original size
    # img_crt = cv2.resize(img_crt, (width,height), interpolation=cv2.INTER_NEAREST)
    # Save output
    save_img('output/crt',filename+'.png',img_crt)

def overlay_pixel(img1,y1,x1,img2,y2,x2,xoff=0,yoff=0,divisor=1):
    # gaussian = (math.e**(-(xoff**2+yoff**2)/(2*(sigma**2))))/(2*math.pi*(sigma**2))
    y1 += yoff
    x1 += xoff
    try:
        # img1[y1,x1] = min(255,img2[y2,x2]*gaussian+img1[y1,x1])
        img1[y1,x1] = min(255,img2[y2,x2]/divisor+img1[y1,x1])
    except:
        pass

def expand(img_to,y0,x0,yrange,xrange,img_from,y_from,x_from):
    yscale  = 2
    xscale  = 5
    gamma   = 1
    for y in range(min(yrange,1),max(0,yrange+1)):
        for x in range(min(xrange,1),max(0,xrange+1)):
            try:    img_to[y0+y,x0+x] = min(255,img_from[y_from,x_from]*(1/(abs(x)*xscale+abs(y)*yscale+gamma))+img_to[y0+y,x0+x])
            except: continue

def project_pixel(img_to, y_to, x_to, img_from, y_from, x_from, scale_y, scale_x):
    val = img_from[y_from, x_from]
    h_to, w_to = img_to.shape[:2]

    def safe_expand(dy, dx):
        expand(img_to, y_to + dy, x_to + dx, dy - (scale_y - 1 if dy == scale_y - 1 else 0), ...)
        # call expand only if target is in bounds
        ty, tx = y_to + dy, x_to + dx
        if 0 <= ty < h_to and 0 <= tx < w_to:
            expand(img_to, ty, tx, ...)

    # --- Corners ---
    expand(img_to, y_to,           x_to,           -scale_y, -scale_x, img_from, y_from, x_from)
    expand(img_to, y_to,           x_to+scale_x-1, -scale_y,  scale_x, img_from, y_from, x_from)
    expand(img_to, y_to+scale_y-1, x_to,            scale_y, -scale_x, img_from, y_from, x_from)
    expand(img_to, y_to+scale_y-1, x_to+scale_x-1,  scale_y,  scale_x, img_from, y_from, x_from)

    # --- Edges (non-corner) ---
    for y in range(1, scale_y - 1):
        expand(img_to, y_to+y, x_to,           0, -scale_x, img_from, y_from, x_from)
        expand(img_to, y_to+y, x_to+scale_x-1, 0,  scale_x, img_from, y_from, x_from)

    for x in range(1, scale_x - 1):
        expand(img_to, y_to,           x_to+x, -scale_y, 0, img_from, y_from, x_from)
        expand(img_to, y_to+scale_y-1, x_to+x,  scale_y, 0, img_from, y_from, x_from)

    # --- All pixels (interior + border): apply blended value ---
    y_end = min(y_to + scale_y, h_to)
    x_end = min(x_to + scale_x, w_to)
    y_start = max(y_to, 0)
    x_start = max(x_to, 0)

    if y_start < y_end and x_start < x_end:
        region = img_to[y_start:y_end, x_start:x_end]
        img_to[y_start:y_end, x_start:x_end] = (
            np.minimum(255, val + region) * 0.3
        )

# def project_pixel(img_to,y_to,x_to,img_from,y_from,x_from,scale_y,scale_x):
#     for y in range(scale_y):
#         for x in range(scale_x):
#             if x==0:
#                 if y==0:
#                     expand(img_to,y_to+y,x_to+x,-scale_y,-scale_x,img_from,y_from,x_from)
#                 elif y==scale_y-1:
#                     expand(img_to,y_to+y,x_to+x,scale_y,-scale_x,img_from,y_from,x_from)
#                 expand(img_to,y_to+y,x_to+x,0,-scale_x,img_from,y_from,x_from)
#             elif x==scale_x-1:
#                 if y==0:
#                     expand(img_to,y_to+y,x_to+x,-scale_y,scale_x,img_from,y_from,x_from)
#                 if y==scale_y-1:
#                     expand(img_to,y_to+y,x_to+x,scale_y,scale_x,img_from,y_from,x_from)
#                 expand(img_to,y_to+y,x_to+x,0,scale_x,img_from,y_from,x_from)
#             if y==0:
#                 expand(img_to,y_to+y,x_to+x,-scale_y,0,img_from,y_from,x_from)
#             elif y==scale_y-1:
#                 expand(img_to,y_to+y,x_to+x,scale_y,0,img_from,y_from,x_from)
#             try:    img_to[y_to+y,x_to+x] = min(255,img_from[y_from,x_from]+img_to[y_to+y,x_to+x])*0.3
#             except: continue
# TODO: Colors are too bright
# def project_img(img, scale, channels=3, loadingbar_colour="white"):
#     height,width = get_img_size(img)
#     projection = np.zeros((height*scale,width*scale, channels), dtype=np.float32)
#     for h in tqdm(range(height),colour=loadingbar_colour,ascii=True,desc=loadingbar_colour.ljust(5," ")):
#         for w in range(width*scale):
#             project_pixel(projection,h*scale,w,img,h,w//scale,scale//2,scale+1)
#     return projection
import numpy as np
from scipy.ndimage import uniform_filter
from scipy.ndimage import *

def project_img(img, scale, color):
    height, width = get_img_size(img)
    
    # 1. Nearest-neighbour upscale in one shot (no Python loops)
    #    np.repeat duplicates each pixel `scale` times in both axes
    # upscaled = np.repeat(np.repeat(img[:, :, :channels], scale, axis=0), scale, axis=1)
    upscaled = np.repeat(np.repeat(img[:, :], scale, axis=0), scale, axis=1)
    for each in range(height):
        upscaled[each*scale] = np.zeros((1,width*scale))
        upscaled[each*scale+1] = np.zeros((1,width*scale))
    upscaled = upscaled.transpose()
    for each in range(width):
        upscaled[each*scale] = np.zeros((1,height*scale))
        if color == "red":
            upscaled[each*scale+2] = np.zeros((1,height*scale))
            upscaled[each*scale+3] = np.zeros((1,height*scale))
        if color == "green":
            upscaled[each*scale+1] = np.zeros((1,height*scale))
            upscaled[each*scale+3] = np.zeros((1,height*scale))
        if color == "blue":
            upscaled[each*scale+1] = np.zeros((1,height*scale))
            upscaled[each*scale+2] = np.zeros((1,height*scale))
    upscaled = upscaled.transpose()
    upscaled = upscaled.astype(np.float32)
    
    kernel_y = scale//2
    kernel_x = scale*2
    kernel_y += 1-kernel_y%2
    kernel_x += 1-kernel_x%2

    # sigma_y = 0.9
    # sigma_x = 2
    sigma_y = kernel_y/3
    sigma_x = kernel_x/4
    
    blended = np.zeros_like(upscaled)
    # blended[:, :] = uniform_filter(upscaled[:, :], size=(kernel_y, kernel_x), mode='nearest')*4
    blended[:, :] = gaussian_filter(upscaled[:, :], sigma=(sigma_y,sigma_x))*scale*1.75
    # blended[:, :] = maximum_filter(upscaled[:, :], size=(1,7))
    # blended[:, :] = percentile_filter(upscaled[:, :], 80, size=(1,3))
    
    # 3. Apply the 0.3 factor and clip to 255
    projection = np.minimum(255.0, upscaled + blended)
    
    return projection.astype(np.float32)

def apply_crt_filter2(filepath="",img=None,filename=None,downscale=2,scale=4,verbose=True,save=True):
    if filename == None:
        filename = re.sub(r'(^.*/)|(\..*)', '', filepath)
    if img is None:
        img = cv2.imread(filepath)
    img_original = img.copy()
    height,width = get_img_size(img)
    if downscale > 1:
        height_new,width_new = height//downscale,width//downscale
        img = cv2.resize(img, (width_new,height_new), interpolation=cv2.INTER_NEAREST)
    blue,green,red = cv2.split(img)

    if verbose: print("starting projection...")
    proj_blue = project_img(blue,scale,"blue")
    if verbose: print("projected blue!")
    proj_green = project_img(green,scale,"green")
    if verbose: print("projected green!")
    proj_red = project_img(red,scale,"red")
    if verbose: print("projected red!")
    img_crt = cv2.merge([proj_blue,proj_green,proj_red])

    if save: save_img('output/crt',filename+'.png',img_crt,verbose)
    if verbose: playsound('sounds/yougotmail.mp3')
    # return img_crt
# def apply_crt_filter2(filepath="", img=None, filename=None, scale=4, verbose=True, save=True):
#     if filename is None:
#         filename = re.sub(r'(^.*/)|(\..*)', '', filepath)

#     # --- GIF handling ---
#     if filepath.endswith('.gif'):
#         gif = Image.open(filepath)
#         frames = []
#         durations = []

#         for frame_num in tqdm(range(gif.n_frames), ascii=True, colour="purple", desc="Filtering GIF"):
#             gif.seek(frame_num)
#             durations.append(gif.info.get('duration', 100))
#             frame_arr = np.array(gif.convert('RGB'))
#             frame_bgr = cv2.cvtColor(frame_arr, cv2.COLOR_RGB2BGR)  # PIL is RGB, cv2 is BGR
#             processed = _apply_crt_to_frame(frame_bgr, scale)
#             frames.append(Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)))

#         if save:
#             frames[0].save(
#                 f'output/crt/gif/{filename}.gif',
#                 append_images=frames[1:],
#                 save_all=True,
#                 loop=0,
#                 duration=durations
#             )
#         return frames

#     # --- Single image handling ---
#     if img is None:
#         img = cv2.imread(filepath)
#     result = _apply_crt_to_frame(img, scale)
#     if save:
#         save_img('output/crt', filename + '.png', result, verbose)
#     if verbose:
#         playsound('sounds/yougotmail.mp3')
#     return result


# def _apply_crt_to_frame(img, scale):
#     height, width = get_img_size(img)
#     img = cv2.resize(img, (width // 2, height // 2), interpolation=cv2.INTER_NEAREST)
#     blue, green, red = cv2.split(img)

#     proj_blue  = project_img(blue,  scale, "blue")
#     proj_green = project_img(green, scale, "green")
#     proj_red   = project_img(red,   scale, "red")

#     return cv2.merge([proj_blue, proj_green, proj_red])


# apply_crt_filter('assets/jpg/sonic.jpg')
# apply_crt_filter('assets/png/sonic2.png')
# for image_path in tqdm(os.listdir('assets\\png'),ascii=True):
#     apply_crt_filter2('assets/png/'+image_path,verbose=False)
apply_crt_filter2('assets/png/Earthworm_Jim_2_lvl1.png',downscale=1)
apply_crt_filter2('assets/png/sonic2.png',downscale=1)
# apply_crt_filter('assets/png/celeste.png',6)
apply_crt_filter2('assets/png/super_metroid.png')
# apply_crt_filter2('assets/gif/super_metroid.gif')
# project_gif('assets/gif/super_metroid.gif')

# sqr_size = 
# # glow = cv2.GaussianBlur(green_phosphor, (sqr_size,sqr_size), 23)
# glow = cv2.GaussianBlur(image, (sqr_size,sqr_size), 23)
# interval = 3
# color = 0
# for i in range(h//interval):
#     glow = cv2.line(glow, (0,i*interval+interval//2), (w,i*interval+interval//2),(100,color,color), 1)
# # glow = cv2.bilateralFilter(glow, 3, 200, 9)
# # Combine
# # weight1 = 0.5
# # phosphor = cv2.addWeighted(image, weight1, glow, 1-weight1, 8)
# # phosphor_rgb = cv2.cvtColor(phosphor, cv2.COLOR_BGR2RGB)
# # axs[1][1].imshow(phosphor_rgb)
# # axs[1][1].set_title('Phosphor Filter')
# cv2.imwrite('output/phosphor/sonic.png',glow)




# # Bilateral Blur
# bilateral = cv2.bilateralFilter(image, 15, 150, 150)  
# bilateral_rgb = cv2.cvtColor(bilateral, cv2.COLOR_BGR2RGB)  
# axs[1][1].imshow(bilateral_rgb)
# axs[1][1].set_title('Bilateral Blur')
# cv2.imwrite('output/bilateral/robocop_3.png',bilateral)

# for row in axs:
#     for ax in row:
#         ax.axis('off')



# plt.show()
# %%
