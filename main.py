#%% EVERYTHING
import cv2
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import os
import re
from time import sleep
from tqdm.auto import tqdm

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

def save_img(folder_path, img_name, img):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    cv2.imwrite(folder_path+'/'+img_name, img)

def get_img_size(img):
    return img.shape[:2] # height, width

def apply_crt_filter(filepath, scale = 1, blur=True, scanlines=True):
    filename = re.sub(r'(^.*/)|(\..*)', '', filepath)
    img = cv2.imread(filepath)
    # Resize image
    height, width = img.shape[:2]
    print(filename,height,width)
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

def overlay_pixel(img1,y1,x1,img2,y2,x2,scale=1):
    try:
        img1[y1,x1] = min(255,img2[y2,x2]/scale+img1[y1,x1])
    except:
        pass

def project_img(img, scale, channels=3, loadingbar_colour="white"):
    height,width = get_img_size(img)
    projection = np.zeros((height*scale,width*scale, channels), dtype=np.uint8)
    sigma_y = 2
    sigma_x = 3
    sigma_a = 1
    for h in tqdm(range(height),colour=loadingbar_colour,ascii=True):
        for w in range(width):
            overlay_pixel(projection,h*scale,w*scale-scale//2,img,h,w)
            # LOOP FROM 0-(SCALE-1) FOR THIS AND BELOW
            overlay_pixel(projection,h*scale,w*scale,img,h,w)

            for x in range(0,scale+1):
                for y in range(0,scale+1):
                    if x==0 and y==0: continue
                    overlay_pixel(projection,h*scale+y,w*scale-scale//2+x,img,h,w,x*sigma_x+y*sigma_y+sigma_a)
                    overlay_pixel(projection,h*scale-y,w*scale-scale//2+x,img,h,w,x*sigma_x+y*sigma_y+sigma_a)
                    overlay_pixel(projection,h*scale+y,w*scale-scale//2-x,img,h,w,x*sigma_x+y*sigma_y+sigma_a)
                    overlay_pixel(projection,h*scale-y,w*scale-scale//2-x,img,h,w,x*sigma_x+y*sigma_y+sigma_a)

                    overlay_pixel(projection,h*scale+y,w*scale+x,img,h,w,x*sigma_x+y*sigma_y+sigma_a)
                    overlay_pixel(projection,h*scale-y,w*scale+x,img,h,w,x*sigma_x+y*sigma_y+sigma_a)
                    overlay_pixel(projection,h*scale+y,w*scale-x,img,h,w,x*sigma_x+y*sigma_y+sigma_a)
                    overlay_pixel(projection,h*scale-y,w*scale-x,img,h,w,x*sigma_x+y*sigma_y+sigma_a)
    return projection

def apply_crt_filter2(filepath):
    filename = re.sub(r'(^.*/)|(\..*)', '', filepath)
    img = cv2.imread(filepath)
    img_original = img.copy()
    height,width = get_img_size(img)
    height_new,width_new = height//2,width//2
    img = cv2.resize(img, (width_new,height_new), interpolation=cv2.INTER_NEAREST)
    blue,green,red = cv2.split(img)

    print("starting projection...")
    proj_blue = project_img(blue,4,1,"blue")
    print("projected blue!")
    proj_green = project_img(green,4,1,"green")
    print("projected green!")
    proj_red = project_img(red,4,1,"red")
    print("projected red!")
    img_crt = cv2.merge([proj_blue,proj_green,proj_red])

    save_img('output/crt',filename+'.png',img_crt)



# apply_crt_filter('assets/jpg/sonic.jpg')
# apply_crt_filter('assets/png/sonic2.png')
# for image_path in os.listdir('assets\\png'):
#     apply_crt_filter('assets/png/'+image_path,2,scanlines=False)
# apply_crt_filter('assets/png/sonic2.png')
# apply_crt_filter('assets/png/celeste.png',6)
# apply_crt_filter('assets/png/super_metroid.png')
apply_crt_filter2('assets/png/super_metroid.png')


# sqr_size = 5
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
