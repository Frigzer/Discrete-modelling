from PIL import Image, ImageEnhance
import numpy as np


def load_image(file_path):
    image = Image.open(file_path)

    image_array = np.array(image)
    return image_array


def save_image(image, file_path):
    result = Image.fromarray(image)
    result.save(file_path)


def load_mask(file_path):
    mask = np.genfromtxt(file_path, delimiter=', ')

    return mask


def darken_image(image, percent):
    image = Image.fromarray(image).convert('L')
    value = 1 - (percent / 100.0)
    enchaner = ImageEnhance.Brightness(image)
    img_enhanced = enchaner.enhance(value)
    img_enhanced = np.array(img_enhanced)
    return img_enhanced


def brighten_image(image, percent):
    image = Image.fromarray(image).convert('L')
    value = 1 + (percent / 100.0)
    enchaner = ImageEnhance.Brightness(image)
    img_enhanced = enchaner.enhance(value)
    img_enhanced = np.array(img_enhanced)
    return img_enhanced


def binary_threshold(image, threshold_percent=50):
    image = Image.fromarray(image)
    image = image.convert('L')
    threshold = threshold_percent / 100.0 * 256
    binary_image = image.point(lambda p: 255 if p > threshold else 0)
    binary_image = np.array(binary_image)
    return binary_image


def get_pixel(image, i, j, border_type, constant_value=0):
    rows, cols = len(image), len(image[0])

    if border_type == "constant": # wartość stała dookoła obrazu
        if 0 > i or rows <= i or 0 > j or cols <= j:
            return constant_value
        else:
            return image[i][j]
    elif border_type == "replicate": # rozszerzenie skrajnego piksela
        i = max(0, min(i, rows - 1))
        j = max(0, min(j, cols - 1))
        return image[i][j]
    elif border_type == "reflect": # odbicie lustrzane skrajnych pikseli
        i = abs(i) if i < 0 else 2 * rows - i - 2 if i >= rows else i
        j = abs(j) if j < 0 else 2 * cols - j - 2 if j >= cols else j
        return image[i][j]
    elif border_type == "wrap": # kopia pikseli od drugiej strony obrazu
        i = i % rows
        j = j % cols
        return image[i][j]


def normalize_if_needed(mask):
    mask_sum = np.sum(mask)

    if mask_sum > 0:
        rows = mask.shape[0]
        cols = mask.shape[1]
        for i in range(rows):
            for j in range(cols):
                mask[i][j] /= mask_sum

    return mask


def dilatation(image, radius=1, border_type="reflect"):
    result = image.copy()
    rows = len(image)
    cols = len(image[0])

    for i in range(rows):
        for j in range(cols):
            if image[i][j] == 255:
                for di in range(-radius, radius + 1):
                    for dj in range(-radius, radius + 1):
                        ni, nj = i + di, j + dj
                        neighbor = get_pixel(image, ni, nj, border_type, 255)
                        if neighbor == 0:
                            result[i][j] = 0
                            break
    return result


def erosion(image, radius=1, border_type="reflect"):
    result = image.copy()
    rows = len(image)
    cols = len(image[0])

    for i in range(rows):
        for j in range(cols):
            if image[i][j] == 0:
                for di in range(-radius, radius + 1):
                    for dj in range(-radius, radius + 1):
                        ni, nj = i + di, j + dj
                        neighbor = get_pixel(image, ni, nj, border_type, 0)
                        if neighbor == 255:
                            result[i][j] = 255
                            break
    return result


def morphological_opening(image, radius=1):
    eroded_image = erosion(image, radius=radius)
    opened_image = dilatation(eroded_image, radius=radius)
    return opened_image


def morphological_closing(image, radius=1):
    dilated_image = dilatation(image, radius=radius)
    closed_image = erosion(dilated_image, radius=radius)
    return closed_image


def convolution(image, mask, border_type="reflect", constant_value=0):

    channels = len(image[0][0]) if len(image.shape) == 3 else 1
    rows, cols = len(image), len(image[0])
    krows, kcols = len(mask), len(mask[0])
    k_center_x, k_center_y = krows // 2, kcols // 2

    kernel = normalize_if_needed(mask)
    kernel_sum = np.sum(mask)
    print(kernel_sum)
    if kernel_sum == 0:
        kernel_sum = 1

    result = np.zeros_like(image, dtype=np.float32)

    for color in range(channels):
        for i in range(rows):
            for j in range(cols):
                value = 0
                for m in range(krows):
                    for n in range(kcols):
                        ni, nj = i + (m - k_center_x), j + (n - k_center_y)
                        pixel = get_pixel(image, ni, nj, border_type, constant_value)
                        if channels > 1:
                            value += pixel[color] * kernel[m, n]
                        else:
                            value += pixel * kernel[m, n]

                if kernel_sum <= 0:
                    value += 255

                if channels > 1:
                    result[i][j][color] = value / kernel_sum
                else:
                    result[i][j] = value / kernel_sum

    result = np.clip(result, 0, 255).astype(np.uint8)

    return result


def main():
    image_1 = load_image("cat.bmp")
    image_2 = load_image("Mapa_MD_no_terrain_low_res_Gray.bmp")

    gauss = load_mask("gauss.txt")
    upper_pass = load_mask("simple_upper_pass.txt")

    image_1_1 = binary_threshold(image_1)
    zad_1_1 = dilatation(image_1_1, 3)
    zad_1_2 = erosion(image_1_1, radius=1)
    zad_1_3 = morphological_opening(image_1_1, radius=3)

    zad_2_1_1 = convolution(image_1, gauss)
    zad_2_1_2 = convolution(image_2, gauss)
    zad_2_2_1 = convolution(image_1, upper_pass)
    zad_2_2_2 = convolution(image_2, upper_pass)

    save_image(image_1_1, "binary.bmp")

    save_image(zad_1_1, "zad_1_1.bmp")
    save_image(zad_1_2, "zad_1_2.bmp")
    save_image(zad_1_3, "zad_1_3.bmp")

    save_image(zad_2_1_1, "zad_2_1_1.bmp")
    save_image(zad_2_1_2, "zad_2_1_2.bmp")
    save_image(zad_2_2_1, "zad_2_2_1.bmp")
    save_image(zad_2_2_2, "zad_2_2_2.bmp")


if __name__ == "__main__":
    main()
