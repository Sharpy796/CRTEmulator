#%% EVERYTHING
import cv2
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import os
import re
from tqdm.auto import tqdm
from playsound3 import playsound
from scipy.ndimage import gaussian_filter

# Grab suitable images from gifs
# for image_path in os.listdir('assets\gif'):
#     with Image.open('assets/gif/'+image_path) as im:
#         im.seek(5)
#         im.save('assets/png/{}.png'.format(image_path.replace(".gif","")))

def save_img(folder_path, img_name, img, verbose=True):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    cv2.imwrite(folder_path+"/"+img_name, img)
    if verbose: print("image saved at '"+folder_path+"/"+img_name+"'")

def get_img_size(img):
    return img.shape[:2] # height, width

def project_img(img, upscale, color, offset=1):
    height, width = get_img_size(img)

    upscaled = np.repeat(np.repeat(img[:, :], upscale, axis=0), upscale, axis=1)
    for each in range(height//2):
        upscaled[2*each*upscale] = np.zeros((1,width*upscale))
        upscaled[2*each*upscale+1] = np.zeros((1,width*upscale))
        upscaled[2*each*upscale+2] = np.zeros((1,width*upscale))
    upscaled = upscaled.transpose()
    for each in range(width):
        if color == "red":
            upscaled[each*upscale+(upscale-2)] = np.zeros((1,height*upscale))
            upscaled[each*upscale+(upscale-1)] = np.zeros((1,height*upscale))
        if color == "green":
            upscaled[each*upscale] = np.zeros((1,height*upscale))
            upscaled[each*upscale+(upscale-1)] = np.zeros((1,height*upscale))
        if color == "blue":
            upscaled[each*upscale] = np.zeros((1,height*upscale))
            upscaled[each*upscale+(upscale-2)] = np.zeros((1,height*upscale))
    upscaled = upscaled.transpose()
    upscaled = upscaled.astype(np.float32)
    
    sigma_y = 1
    sigma_x = 5/4
    
    blended = np.zeros_like(upscaled)
    blended[:, :] = gaussian_filter(upscaled[:, :], sigma=(sigma_y,sigma_x))

    projection = np.minimum(255.0, np.maximum(upscaled, blended*4))

    return projection.astype(np.float32)

def apply_crt_filter2(filepath="",img=None,filename=None,downscale=2,upscale=3,verbose=True,save=True,sound=False):
    if filename == None:
        filename = re.sub(r'(^.*/)|(\..*)', '', filepath)
    if img is None:
        img = cv2.imread(filepath)
    img_original = img.copy()
    height,width = get_img_size(img)
    height_new,width_new = int(height/downscale),int(width/downscale)
    img = cv2.resize(img, (width_new,height_new), interpolation=cv2.INTER_NEAREST)
    blue,green,red = cv2.split(img)

    if verbose: print("starting projection...")
    proj_blue = project_img(blue,upscale,"blue")
    if verbose: print("projected blue!")
    proj_green = project_img(green,upscale,"green")
    if verbose: print("projected green!")
    proj_red = project_img(red,upscale,"red")
    if verbose: print("projected red!")
    img_crt = cv2.merge([proj_blue,proj_green,proj_red])

    if save: save_img('output/crt',filename+'.png',img_crt,verbose)
    if sound: playsound('sounds/yougotmail.mp3')

for image_path in tqdm(os.listdir('assets\\png'),ascii=True):
    apply_crt_filter2('assets/png/'+image_path,verbose=False,downscale=1)
apply_crt_filter2('assets/png/Earthworm_Jim_2_lvl1.png',downscale=1,upscale=3,verbose=False) # TODO: Account for 480i in gif
apply_crt_filter2('assets/png/sonic2.png',downscale=0.5,verbose=False)
apply_crt_filter2('assets/png/cinema.png',downscale=5,verbose=False)
apply_crt_filter2('assets/png/celeste.png',downscale=3,upscale=3,verbose=False,sound=True)

# TODO: Create gifs of this
print("Images filtered!")

# %%
