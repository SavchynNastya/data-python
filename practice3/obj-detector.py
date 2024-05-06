import cv2
import matplotlib.pyplot as plt

# Завантаження зображення
image = cv2.imread('C:\\Users\\Anastasia\\KPI\\Python-data\\practice3\\cookie.jpg')

# Конвертація в grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Виявлення контурів
contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Виведення зображення з контурами
cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
plt.imshow(image)
plt.show()