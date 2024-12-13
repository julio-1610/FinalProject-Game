import cv2 as cv
import numpy as np
import os


def plaza_ra():
    # Ruta de las imágenes
    image_folder = "assets/"
    images = [
        "pa_1.jpg",
        "pa_2.jpg",
        "pa_3.jpg",
        "pa_4.jpg"
    ]

    # Cargar imágenes
    loaded_images = [cv.imread(os.path.join(image_folder, img)) for img in images]
    if any(img is None for img in loaded_images):
        print("Error: No se pudieron cargar todas las imágenes. Verifica las rutas.")
        return False  # Retornar nivel no completado

    # Configuración de la cámara
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return False

    current_image_index = 0
    cooldown_active = False

    def detect_white_sheet(frame):
        """Detecta si hay una hoja en blanco en el marco."""
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        _, thresh = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            epsilon = 0.02 * cv.arcLength(cnt, True)
            approx = cv.approxPolyDP(cnt, epsilon, True)
            area = cv.contourArea(cnt)
            if len(approx) == 4 and area > 5000:  # Detecta un área grande con 4 lados
                return approx
        return None

    def detect_hand(frame):
        """Detecta si hay una mano en el marco usando el rango de color de piel."""
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv.inRange(hsv, lower_skin, upper_skin)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)
        contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv.contourArea(cnt)
            if area > 3000:  # Detectar áreas significativas de una mano
                return True
        return False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo capturar el cuadro de la cámara.")
            break

        # Detectar hoja blanca
        sheet_corners = detect_white_sheet(frame)
        if sheet_corners is not None:
            sheet_corners = np.array(sorted(sheet_corners[:, 0], key=lambda x: (x[1], x[0])), dtype=np.float32)
            if len(sheet_corners) == 4:
                src_points = np.array([[0, 0], [0, loaded_images[0].shape[0]],
                                       [loaded_images[0].shape[1], loaded_images[0].shape[0]],
                                       [loaded_images[0].shape[1], 0]], dtype=np.float32)
                dst_points = sheet_corners.reshape(4, 2).astype(np.float32)
                H, status = cv.findHomography(src_points, dst_points)
                if H is not None:
                    warped_image = cv.warpPerspective(loaded_images[current_image_index], H,
                                                      (frame.shape[1], frame.shape[0]))
                    mask = np.zeros_like(frame, dtype=np.uint8)
                    cv.fillConvexPoly(mask, dst_points.astype(int), (255, 255, 255))
                    inverse_mask = cv.bitwise_not(mask)
                    frame = cv.bitwise_and(frame, inverse_mask)
                    frame = cv.add(frame, warped_image)

        # Detectar mano para cambiar de imagen
        elif detect_hand(frame):
            if not cooldown_active:  # Solo cambiar si no está en enfriamiento
                cooldown_active = True
                current_image_index = (current_image_index + 1) % len(loaded_images)
        else:
            cooldown_active = False

        cv.imshow("AR Plaza", frame)

        # Detectar la tecla 'Esc' para salir de la cámara sin cerrar el juego
        if cv.waitKey(1) & 0xFF == 27:  # 27 es el código ASCII de 'Esc'
            cap.release()
            cv.destroyAllWindows()
            return True  # Indicar que el nivel terminó correctamente

    cap.release()
    cv.destroyAllWindows()
    return True  # Indicar que el nivel se completó correctamente