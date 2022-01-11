import imageio as iio
from PIL import Image
from pygifsicle import optimize

# Check image size is power of 2
filename = "arrow"
im = Image.open(filename + ".png")
im = im.convert("RGBA")
if not (im.size[0] == im.size[1] and (im.size[0] and (not(im.size[0] & (im.size[0] - 1))))):
    print("Invalid Image Size")
    exit(1)

FPS = 30
frames = []

for rotate in range(4):
    curr_region = im.size[0]

    while curr_region > 1:
        # Grab regions to translate
        regions = []
        for i in range(im.size[0] // curr_region):
            regions.append([])
            for j in range(im.size[1] // curr_region):
                d = dict()
                region = im.crop((j*curr_region, i*curr_region, (j+1)*curr_region, (i+1)*curr_region))

                d["nw"] = region.crop((0, 0, int(region.size[1]/2), int(region.size[0]/2)))
                d["ne"] = region.crop((int(region.size[1]/2), 0, region.size[1], int(region.size[0]/2)))
                d["sw"] = region.crop((0, int(region.size[0]/2), int(region.size[1]/2), region.size[0]))
                d["se"] = region.crop((int(region.size[1]/2), int(region.size[0]/2), region.size[1], region.size[0]))
                regions[-1].append(d)

        # Create frames of translation, rotating clockwise
        frame_offset = -1
        for frame in range(FPS+1):
            frame_copy = im.copy()
            if int(curr_region/2/FPS * frame) != frame_offset:
                frame_offset = int(curr_region/2/FPS * frame)
            else:
                continue

            for i in range(im.size[0] // curr_region):
                for j in range(im.size[1] // curr_region):
                    
                    # NW moving right
                    left, top = j*curr_region, i*curr_region
                    box = (left + frame_offset, top, left + int(curr_region/2) + frame_offset, top + int(curr_region/2))
                    frame_copy.paste(regions[i][j]["nw"], box)

                    # NE moving down
                    left, top = j*curr_region + int(curr_region/2), i*curr_region
                    box = (left, top + frame_offset, left + int(curr_region/2), top + int(curr_region/2) + frame_offset)
                    frame_copy.paste(regions[i][j]["ne"], box)

                    # SW moving left
                    left, top = j*curr_region + int(curr_region/2), i*curr_region + int(curr_region/2)
                    box = (left - frame_offset, top, left + int(curr_region/2) - frame_offset, top + int(curr_region/2))
                    frame_copy.paste(regions[i][j]["se"], box)

                    # SW moving up
                    left, top = j*curr_region, i*curr_region + int(curr_region/2)
                    box = (left, top - frame_offset, left + int(curr_region/2), top + int(curr_region/2) - frame_offset)
                    frame_copy.paste(regions[i][j]["sw"], box)

            frames.append(frame_copy)

        im = frame_copy.copy()
        curr_region = int(curr_region / 2)

iio.mimsave(filename + "_animated.gif", frames, 'GIF', fps=FPS)
optimize(filename + "_animated.gif")