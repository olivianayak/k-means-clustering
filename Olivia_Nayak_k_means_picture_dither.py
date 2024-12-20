# Olivia Nayak
# This code takes an image and uses the k-means algorithm to compress it. 


from PIL import Image
import random
import math
import statistics
import sys


# adds the color bar of all the colors used in the image to the bottom of the image
def add_color_bar(pix, image_size, num_colors, all_colors):
    width = image_size[0]
    height = image_size[1]
    box_width = width // num_colors
    leftover_space = width - box_width*num_colors
    new_image = Image.new("RGB", (width, height + box_width))
    new_pix = new_image.load()
    for i in range(width):
        for j in range(height):
            new_pix[i, j] = pix[i, j]
    starting_x = 0
    for i in range(num_colors):
        color = all_colors[i]
        box_width_loop = box_width
        if i < leftover_space:
            box_width_loop += 1
        for x in range(box_width_loop):
            for y in range(box_width_loop-1):
                new_pix[starting_x+x, height+y] = color
        starting_x += box_width_loop
    return new_image


# restricts R, B, and G to 3 values each -- 0, 127, or 255
def naive_27(image_name, dither):
    img = Image.open(image_name)
    pix = img.load()
    size = img.size
    width = size[0]
    height = size[1]
    colors = set()
    # loop through every pixel and for R, G, and B of every pixel, set it to either 0, 127, or 255
    for i in range(width):
        for j in range(height):
            pixel_list = []
            for k in range(3):
                temp_pixel = pix[i, j][k]
                if temp_pixel < 255//3:
                    pixel_list.append(0)
                elif temp_pixel > (255*2)//3:
                    pixel_list.append(255)
                else:
                    pixel_list.append(127)
            pix[i, j] = tuple(pixel_list)
            colors.add(tuple(pixel_list))
    if dither:
        pix = dithering(height, width, pix, list(colors))
    # adds the color bar to the bottom of the image
    bar_colors = [(0, 0, 0), (0, 0, 255), (0, 0, 127), (0, 255, 0), (0, 255, 255), (0, 155, 127), (0, 127, 0), (0, 127, 255), (0, 127, 127), (255, 0, 0), (255, 0, 255), (255, 0, 127), (255, 255, 0), (255, 255, 255), (255, 255, 127), (255, 127, 0), (255, 127, 255), (255, 127, 127), (127, 0, 0), (127, 0, 255), (127, 0, 127), (127, 255, 0), (127, 255, 255), (127, 255, 127), (127, 127, 0), (127, 127, 255), (127, 127, 127)]
    new_image = add_color_bar(pix, size, 27, bar_colors)
    # show and save the image
    new_image.show()
    new_image.save("naive_27.png")


# restricts R, B, and G to 2 values each -- 0 or 255
def naive_8(image_name, dither):
    img = Image.open(image_name)
    pix = img.load()
    size = img.size
    width = size[0]
    height = size[1]
    colors = set()
    # loop through every pixel and for R, G, and B of every pixel, set it to either 0 or 255
    for i in range(width):
        for j in range(height):
            pixel_list = []
            for k in range(3):
                temp_pixel = pix[i, j][k]
                if temp_pixel < 128:
                    pixel_list.append(0)
                else:
                    pixel_list.append(255)
            pix[i, j] = tuple(pixel_list)
            colors.add(tuple(pixel_list))
    if dither:
        pix = dithering(height, width, pix, list(colors))
    # adds the color bar to the bottom of the image
    bar_colors = [(0, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 0), (255, 255, 255)]
    new_image = add_color_bar(pix, size, 8, bar_colors)
    # show and save the image
    new_image.show()
    new_image.save("naive_8.png")


# use the k-means algorithm to find clusters of k number of colors
def k_means(image_name, k_value, plus_plus, dither):
    img = Image.open(image_name)
    pix = img.load()
    size = img.size
    width = size[0]
    height = size[1]
    pixel_points = []
    points = []
    pixel_index_dict = dict()
    for i in range(width):
        for j in range(height):
            pixel_points.append(pix[i, j])
            points.append((i, j))
            if pix[i, j] not in pixel_index_dict:
                pixel_index_dict[pix[i, j]] = [(i, j)]
            else:
                pixel_index_dict[pix[i, j]].append((i, j))
    unique_points = set(pixel_points)
    # establish the starting centroids 
    if plus_plus: # set the starting centroids based on distance in relation to each other
        means = k_means_plus_plus(unique_points, k_value)
    else: # set the starting centroids randomly 
        means = random.sample(unique_points, k=k_value)
    stable = False
    # create the stability_dict to detect the movement of pixels between groups
    stability_dict = dict.fromkeys((range(k_value)))
    for item in stability_dict:
        #length of list in previous round, mean in previous round
        stability_dict[item] = (0, (0, 0, 0))
    num_cycles = 0
    # a group is stable is the number of pixels in the group doesn't change from one cycle to another and the means of r, g, and b don't change
    while not stable:
        # a group is the collection of pixels around each centroid. there are k groups
        groups = dict.fromkeys((range(k_value)))
        for temp_group in groups:
            #r values, g values, b values, full color tuple
            groups[temp_group] = ([], [], [], [])
        for point in unique_points:
            smallest_error = math.inf
            best_group = 0
            for group, mean in enumerate(means):
                error = ((point[0] - mean[0])**2 + (point[1] - mean[1])**2 + (point[2] - mean[2])**2)
                if error < smallest_error:
                    smallest_error = error
                    best_group = group
            breakdown = groups[best_group]
            breakdown[0].append(point[0])
            breakdown[1].append(point[1])
            breakdown[2].append(point[2])
            breakdown[3].append(point)
        all_diff_zero = True
        for x in range(k_value):
            breakdown = groups[x]
            means[x] = (statistics.mean(breakdown[0]), statistics.mean(breakdown[1]), statistics.mean(breakdown[2]))
            if stability_dict[x][0] - len(breakdown[3]) != 0:
                temp_list = list(stability_dict[x])
                temp_list[0] = len(breakdown[3])
                temp_list[1] = means[x]
                stability_dict[x] = tuple(temp_list)
                all_diff_zero = False
        if all_diff_zero:
            stable = True
        else:
            stable = False
        num_cycles += 1
    # the means/centroids will be decimals, so loop through them and round to be able to use them as rbg values
    rounded_means = []
    for mean in means:
        temp_list = [0, 0, 0]
        for index, color_val in enumerate(mean):
            temp_list[index] = round(color_val)
        rounded_means.append(tuple(temp_list))
    if dither: 
        pix = dithering(height, width, pix, rounded_means)
    else: #map the original pixel to the centroid pixel
        pix_count = 0
        for counter, mean in enumerate(rounded_means):
            for pix_point in groups[counter][3]:
                    points = pixel_index_dict[pix_point]
                    for point in points:
                        pix[point[0], point[1]] = mean
                        pix_count += 1
    # add the color bar to the bottom of the image
    new_image = add_color_bar(pix, size, k_value, rounded_means)
    # show and save the image
    new_image.show()
    new_image.save("kmeansout.png")


def k_means_plus_plus(input_data, k_value):
    data = list(input_data)
    means = []
    point = random.choice(data)
    means.append(point)
    while len(means) < k_value:
        min_dist_list = []
        for point in data:
            min_distance = math.inf
            for mpoint in means:
                dist_from_mean = math.dist(point, mpoint)
                if dist_from_mean < min_distance:
                    min_distance = dist_from_mean
            min_dist_list.append(min_distance)
        distance_sum = sum(min_dist_list)
        choice_prob = [i / distance_sum for i in min_dist_list]
        next_k = None
        while next_k == None:
            next_k = random.choices(data, weights=choice_prob, k=1) 
            next_k = next_k[0] 
            if next_k in means:
                next_k = None
            else:
                means.append(next_k)
    return means


def find_closest_palette_color(old_pixel, palette_color):
    smallest_error = math.inf
    mapped_color = palette_color[0]
    for index, new_color in enumerate(palette_color):
        error = ((old_pixel[0] - new_color[0])**2 + (old_pixel[1] - new_color[1])**2 + (old_pixel[2] - new_color[2])**2)
        if error < smallest_error:
            smallest_error = error
            mapped_color = palette_color[index]
    return mapped_color


def dithering(height, width, pix, colors):
    for y in range(height):
        for x in range(width):
            oldpixel = pix[x, y]
            newpixel = find_closest_palette_color(oldpixel, colors)
            pix[x, y] = newpixel
            errR = oldpixel[0] - newpixel[0]
            errG = oldpixel[1] - newpixel[1]
            errB = oldpixel[2] - newpixel[2]

            if x > 0 and x < width-1 and y < height-1 :
                existingpixel = pix[x+1, y]
                updatedR = round(existingpixel[0] + errR * 7/16)
                updatedG = round(existingpixel[1] + errG * 7/16)
                updatedB = round(existingpixel[2] + errB * 7/16)
                pix[x+1, y] = (updatedR, updatedG, updatedB)

                existingpixel = pix[x-1, y+1]
                updatedR = round(existingpixel[0] + errR * 3/16)
                updatedG = round(existingpixel[1] + errG * 3/16)
                updatedB = round(existingpixel[2] + errB * 3/16)
                pix[x-1, y+1] = (updatedR, updatedG, updatedB)
                 
                existingpixel = pix[x, y+1]
                updatedR = round(existingpixel[0] + errR * 5/16)
                updatedG = round(existingpixel[1] + errG * 5/16)
                updatedB = round(existingpixel[2] + errB * 5/16)
                pix[x, y+1] = (updatedR, updatedG, updatedB)

                existingpixel = pix[x+1, y+1]
                updatedR = round(existingpixel[0] + errR * 1/16)
                updatedG = round(existingpixel[1] + errG * 1/16)
                updatedB = round(existingpixel[2] + errB * 1/16)
                pix[x+1, y+1] = (updatedR, updatedG, updatedB)
    return pix        


# naive_8("beagle.jpg", True)
# naive_27("beagle.jpg", True)
# k_means("beagle.jpg", 27, True, False)

# call the k-means algorithm on an image
file_name = sys.argv[1]
k_val = sys.argv[2]
k_means(file_name, int(k_val), True, True)