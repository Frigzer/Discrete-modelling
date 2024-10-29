from PIL import Image, ImageEnhance

def load_image(file_path):
    image = Image.open(file_path).convert('L')
    return image

def save_image(image, file_path):
    image.save(file_path)

def darken_image(image, percent):
    value = 1 - (percent / 100.0)
    enchaner = ImageEnhance.Brightness(image)
    img_enhanced = enchaner.enhance(value)
    return img_enhanced

def brighten_image(image, percent):
    value = 1 + (percent / 100.0)
    enchaner = ImageEnhance.Brightness(image)
    img_enhanced = enchaner.enhance(value)
    return img_enhanced

def binary_threshold(image, threshold_percent=50):
    threshold = threshold_percent / 100.0 * 256
    binary_image = image.point(lambda p: 255 if p > threshold else 0)
    return binary_image

def main():
    image = load_image('Mapa_MD_no_terrain_low_res_Gray.bmp')

    darkened_value = int(input("Podaj wartość % z zakresu 1-99 o którą chcesz ściemnić obraz: "))
    if darkened_value in range(1, 100):
        darkened_image = darken_image(image, darkened_value)
        save_image(darkened_image, f'darkened_image_by_{darkened_value}%.bmp')
        print(f"Obraz ściemniony zapisany jako 'darkened_image_by_{darkened_value}%.bmp'.\n")
    else:
        print("Podano złą wartość\n")

    brightened_value = int(input("Podaj wartość % z zakresu 10-20 o którą chcesz rozjaśnić obraz: "))
    if brightened_value in range(10, 21):
        for i in range(3):
            brightened_image = brighten_image(image, brightened_value * (i + 1))
            save_image(brightened_image, f'brightened_image_step_{i + 1}.bmp')
            print(f"Obraz rozjaśniony krok {i + 1} zapisany jako 'brightened_image_step_{i + 1}.bmp'.")
        print("\n")
    else:
        print("Podano złą wartość\n")

    binary_image_50 = binary_threshold(image)
    save_image(binary_image_50, 'binary_image_50%.bmp')
    print("Obraz po binaryzacji 50% zapisany jako 'binary_image_50.bmp'.\n")

    treshhold = int(input("Podaj próg binaryzacji w %: "))
    if treshhold in range(0, 101):
        binary_image_custom = binary_threshold(image, treshhold)
        save_image(binary_image_custom, 'binary_image_custom.bmp')
        print(f"Obraz po binaryzacji {treshhold}% zapisany jako 'binary_image_custom.bmp'.\n")
    else:
        print("Podano złą wartość\n")

if __name__ == "__main__":
    main()
