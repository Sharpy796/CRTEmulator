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
import imageio as iio
import glob

# Grab suitable images from gifs
# for image_path in os.listdir('assets\gif'):
#     with Image.open('assets/gif/'+image_path) as im:
#         im.seek(5)
#         im.save('assets/png/{}.png'.format(image_path.replace(".gif","")))

# FUNCTIONS
def create_dir(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def save_img(folder_path,img_name,img,verbose=True):
    create_dir(folder_path)
    cv2.imwrite(f'{folder_path}/{img_name}', img)
    if verbose: print(f"image saved at '{folder_path}/{img_name}'")

def get_img_size(img):
    return img.shape[:2] # height, width

def project_img(img,upscale,color,offset=False,sigma_y=1,sigma_x=4):
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
    
    blended = np.zeros_like(upscaled)
    blended[:, :] = gaussian_filter(upscaled[:, :], sigma=(sigma_y,sigma_x))

    projection = np.minimum(255.0, np.maximum(upscaled, blended*5))

    return projection.astype(np.float32)

def playsoundfinished():
    playsound('sounds/yougotmail.mp3')

def apply_crt_filter2(filepath=None,filepath_save='output/crt/png',img=None,filename=None,downscale=1,upscale=3,verbose=True,save=True,sound=False,offset=False,sigma_y=1,sigma_x=4):
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
    proj_blue = project_img(blue,upscale,"blue",offset,sigma_y,sigma_x)
    if verbose: print("projected blue!")
    proj_green = project_img(green,upscale,"green",offset,sigma_y,sigma_x)
    if verbose: print("projected green!")
    proj_red = project_img(red,upscale,"red",offset,sigma_y,sigma_x)
    if verbose: print("projected red!")
    img_crt = cv2.merge([proj_blue,proj_green,proj_red])

    if save:
        save_img(filepath_save,f'{filename}.png',img_crt,verbose)
    if sound: playsoundfinished()
    return cv2.merge([proj_blue,proj_green,proj_red]) # returns BGR

def create_gif2(folder_path,folder_path_save,filename,duration=20,gif=True,video=False):
    filenames = sorted(glob.glob(f'{folder_path}/*.png'))
    frames = [Image.open(f).convert('RGB') for f in filenames]

    if gif:
        print(f"Saving '{filename}.gif'...")
        # Stitch all frames side-by-side into one giant image to build a global palette
        combined = Image.new('RGB', (frames[0].width * len(frames), frames[0].height))
        for i, f in enumerate(frames):
            combined.paste(f, (i * f.width, 0))

        # Derive the global palette from the combined image
        palette_source = combined.quantize(colors=256, method=Image.Quantize.FASTOCTREE)

        # Make sure all frames are in RGB format and not RGBA
        frames = [f.convert('RGB') for f in frames]
        # Now quantize every frame against that palette
        quantized = [f.quantize(colors=256, palette=palette_source, dither=0) for f in frames]

        quantized[0].save(
            f'{folder_path_save}/{filename}.gif',
            save_all=True,
            append_images=quantized[1:],
            loop=0,
            duration=duration,
            optimize=False,
            disposal=2
        )
        print(f"Saved '{filename}.gif'!")
    
    if video:
        print(f"Saving '{filename}.mp4'...")
        with iio.get_writer(f'{folder_path_save}/{filename}.mp4', fps=20, quality=8) as writer:
            for frame in frames:
                writer.append_data(np.array(frame))
        print(f"Saved '{filename}.mp4'!")

def apply_crt_filter2_gif(filepath="",img=None,filename=None,downscale=1,upscale=3,verbose=False,sigma_y=1,sigma_x=4):
    if filename == None:
        filename = re.sub(r'(^.*/)|(\..*)', '', filepath)
    processed_images = []
    duration = 0
    with Image.open(filepath) as im:
        im.seek(min(im.n_frames,3))
        duration = im.info['duration']
        create_dir(f'output/crt/gif/{filename}/clean')
        create_dir(f'output/crt/gif/{filename}/edited')
        for frame in tqdm(range(im.n_frames),ascii=True,desc=f"Processing '{filename}.gif'",unit='frames'):
            im.seek(frame)
            im.save(f'output/crt/gif/{filename}/clean/frame{frame:03d}.png',optimize=False)
            processed_images.append(apply_crt_filter2(filepath=f'output/crt/gif/{filename}/clean/frame{frame:03d}.png',
                                                      filepath_save=f'output/crt/gif/{filename}/edited',
                                                      filename=f'frame{frame:03d}',
                                                      downscale=downscale,
                                                      upscale=upscale,
                                                      verbose=verbose,
                                                      sigma_y=sigma_y,
                                                      sigma_x=sigma_x,
                                                      save=True))
    create_gif2(folder_path=f'output/crt/gif/{filename}/edited',
                folder_path_save=f'output/crt/gif/{filename}',
                filename=filename,
                duration=duration)



# IMAGE FILTERING
# 240p resolution filters
for img_path in tqdm(os.listdir('assets\\png'),ascii=True,desc='Processing PNGs',unit='images'):
    if not ('sonic2' in img_path or 'cinema' in img_path or 'celeste' in img_path or 'Earthworm' in img_path or 'presentation' in img_path):
        apply_crt_filter2(f'assets/png/{img_path}',verbose=False)
apply_crt_filter2('assets/png/sonic2.png',downscale=0.5,verbose=False,sigma_x=5)
apply_crt_filter2('assets/png/cinema.png',downscale=5,verbose=False,sigma_y=0.5,sigma_x=2)
apply_crt_filter2('assets/png/celeste.png',downscale=3,upscale=3,verbose=False,sigma_y=1.5)
apply_crt_filter2('assets/png/presentation_screenshot.png',verbose=False,downscale=4,sigma_x=4,sigma_y=1.5,offset=False)
apply_crt_filter2('assets/png/presentation_screenshot_username.png',verbose=False,downscale=4,sigma_x=4,sigma_y=1.5,offset=False)

# 240p resolution filters - GIFS
for gif_path in os.listdir('assets\\gif'):
    if 'cinema' not in gif_path:
        apply_crt_filter2_gif(f'assets/gif/{gif_path}')
apply_crt_filter2_gif('assets/gif/cinema.gif',downscale=3,sigma_y=0.5,sigma_x=2)

# 480i resolution filters
apply_crt_filter2('assets/png/Earthworm_Jim_2_lvl1.png',filepath_save='output/crt/gif/Earthworm_Jim_2_lvl1/edited',filename='frame00',upscale=3,verbose=False,offset=False,sigma_x=2)
apply_crt_filter2('assets/png/Earthworm_Jim_2_lvl1.png',filepath_save='output/crt/gif/Earthworm_Jim_2_lvl1/edited',filename='frame01',upscale=3,verbose=False,offset=True, sigma_x=2)
create_gif2(folder_path=f'output/crt/gif/Earthworm_Jim_2_lvl1/edited',
            folder_path_save=f'output/crt/gif/Earthworm_Jim_2_lvl1',
            filename='Earthworm_Jim_2_lvl1',
            duration=20)

playsoundfinished()
print("Images filtered!")

# %%
