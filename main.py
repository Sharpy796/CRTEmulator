#%% EVERYTHING
# IMPORTS
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

# FUNCTIONS
def save_img(folder_path, img_name, img, verbose=True):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    cv2.imwrite(folder_path+"/"+img_name, img)
    if verbose: print("image saved at '"+folder_path+"/"+img_name+"'")

def get_img_size(img):
    return img.shape[:2] # height, width

def project_img(img, upscale, color, offset=False):
    height, width = get_img_size(img)

    upscaled = np.repeat(np.repeat(img[:, :], upscale, axis=0), upscale, axis=1)
    for each in range(height//2):
        upscaled[upscale*offset+2*each*upscale] = np.zeros((1,width*upscale))
        upscaled[upscale*offset+2*each*upscale+1] = np.zeros((1,width*upscale))
        upscaled[upscale*offset+2*each*upscale+2] = np.zeros((1,width*upscale))
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

def playsoundfinished():
    playsound('sounds/yougotmail.mp3')

def apply_crt_filter2(filepath=None,img=None,filename=None,downscale=1,upscale=3,verbose=True,save=True,sound=False,offset=False):
    if filename == None and filepath != None:
        filename = re.sub(r'(^.*/)|(\..*)', '', filepath)
    if img is None:
        img = cv2.imread(filepath)
    img_original = img.copy()
    height,width = get_img_size(img)
    height_new,width_new = int(height/downscale),int(width/downscale)
    img = cv2.resize(img, (width_new,height_new), interpolation=cv2.INTER_NEAREST)
    blue,green,red = cv2.split(img)

    if verbose: print("starting projection...")
    proj_blue = project_img(blue,upscale,"blue",offset)
    if verbose: print("projected blue!")
    proj_green = project_img(green,upscale,"green",offset)
    if verbose: print("projected green!")
    proj_red = project_img(red,upscale,"red",offset)
    if verbose: print("projected red!")
    img_crt = cv2.merge([proj_blue,proj_green,proj_red])

    if save: save_img('output/crt',filename+'.png',img_crt,verbose)
    if sound: playsoundfinished()
    return cv2.merge([proj_red,proj_green,proj_blue]) # returns RGB

def create_gif(img_arr, filepath, duration=20, disposal=2):
    frames = [Image.fromarray(img.astype(np.uint8), 'RGB') for img in img_arr]
    
    # Build a global palette by quantizing a composite of all frames
    combined = Image.new('RGB', (frames[0].width, frames[0].height * len(frames)))
    for i, frame in enumerate(frames):
        combined.paste(frame, (0, i * frames[0].height))
    
    palette_source = combined.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    
    # Apply that single palette to every frame
    quantized_frames = [frame.quantize(palette=palette_source, dither=0) for frame in frames]
    
    quantized_frames[0].save(
        filepath,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=duration,
        loop=0,
        optimize=False,  # Don't let Pillow mess with the palette
        disposal=0  # ← Clear to background before each frame
    )

# def create_gif(img_arr,filepath,duration=20):
#     gif = [Image.fromarray(img.astype(np.uint8),'RGB') for img in img_arr]
#     gif[0].save(filepath, save_all=True, append_images=gif[1:], duration=duration, loop=0)

def apply_crt_filter2_gif(filepath="",img=None,filename=None,downscale=1,upscale=3,verbose=False):
    if filename == None:
        filename = re.sub(r'(^.*/)|(\..*)', '', filepath)
    processed_images = []
    duration,disposal = 0,None
    with Image.open(filepath) as im:
        im.seek(min(im.n_frames,3))
        duration = im.info['duration']
        disposal = im.disposal_method
        
        if not os.path.exists('output/crt/gif/'+filename):
            os.makedirs('output/crt/gif/'+filename)
        for frame in tqdm(range(im.n_frames),ascii=True,desc="Processing "+filename+'.gif'):
            im.seek(frame)
            im.save('output/crt/gif/'+filename+'/frame'+str(frame)+'.png',optimize=False)
            processed_images.append(apply_crt_filter2('output/crt/gif/'+filename+'/frame'+str(frame)+'.png',img=img,filename=filename,downscale=downscale,upscale=upscale,verbose=verbose,save=False))
    create_gif(processed_images,'output/crt/gif/'+filename+'.gif',duration=duration,disposal=disposal)



# IMAGE FILTERING
# 240p resolution filters
# for image_path in tqdm(os.listdir('assets\\png'),ascii=True):
#     apply_crt_filter2('assets/png/'+image_path,verbose=False)
# apply_crt_filter2('assets/png/sonic2.png',downscale=0.5,verbose=False)
# apply_crt_filter2('assets/png/cinema.png',downscale=5,verbose=False)
# apply_crt_filter2('assets/png/celeste.png',downscale=3,upscale=3,verbose=False,sound=True)

# 240p resolution filters - GIFS
apply_crt_filter2_gif('assets/gif/super_metroid.gif',verbose=False)
apply_crt_filter2_gif('assets/gif/super_bomberman_5.gif',verbose=False)
apply_crt_filter2_gif('assets/gif/cinema.gif',downscale=3)

# 480i resolution filters
# frame1 = apply_crt_filter2('assets/png/Earthworm_Jim_2_lvl1.png',filename='Earthworm_Jim_2_lvl1_frame1',upscale=3,verbose=False,offset=False)
# frame2 = apply_crt_filter2('assets/png/Earthworm_Jim_2_lvl1.png',filename='Earthworm_Jim_2_lvl1_frame2',upscale=3,verbose=False,offset=True)
# gif = [frame1,frame2]
# create_gif(gif,'output/crt/gif/Earthworm_Jim_2_lvl1.gif')

# TODO: Create gifs
playsoundfinished()
print("Images filtered!")

# %%
