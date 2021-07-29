import qrcode
import cv2 as cv
from io import BytesIO
from os import remove


class QRCodeDoesNotExist(Exception):
    ...


def get_qr_code_data(file: str) -> str:
    img = cv.imread(file)
    # Convert image to black&white
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray_image = cv.bitwise_not(gray)

    blur = cv.GaussianBlur(gray_image, (9, 9), 0)
    thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    # Morph close
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
    close = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel, iterations=2)
    # Find contours and filter for QR code
    contours = cv.findContours(close, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    for cnt in contours:
        peri = cv.arcLength(cnt, True)
        approx = cv.approxPolyDP(cnt, 0.04 * peri, True)
        x, y, w, h = cv.boundingRect(approx)
        area = cv.contourArea(cnt)
        ar = w / float(h)
        # Crop image
        if len(approx) == 4 and area > 10000 and (ar > 0.85 and ar < 1.3):
            cv.rectangle(close, (x, y), (x + w, y + h), (36, 255, 12), 3)
            ROI = close[y : y + h, x : x + w]

    detector = cv.QRCodeDetector()
    try:
        data, points, _ = detector.detectAndDecode(ROI)
    except cv.error:
        raise TypeError("File is invalid")
    if points is None:
        raise QRCodeDoesNotExist("QR Code does not exist or hasn't been recognized")
    return data


def new_qr_code(
    data_,
    filename,
    ver=1,
    err_cor=qrcode.constants.ERROR_CORRECT_H,
    size=1,
    border=4,
    fg_color="black",
    bg_color="white",
    space="RGB",
) -> str:
    qr = qrcode.QRCode(
        version=ver, error_correction=err_cor, box_size=size, border=border
    )
    qr.add_data(data_)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert(space)
    img.save(f"./images/qr_codes/{filename}")
    return filename


def save_photo(file: BytesIO, filename: str):
    with open(get_file_path(filename), "wb") as out:
        out.write(file.getbuffer())


get_file_path = lambda filename: f"./images/{filename}.jpg"


delete_file = lambda filename: remove(filename)


if __name__ == "__main__":
    control = [
        "asdasAD123134FGSD",
        "asdas4FGSD",
        "52352SD",
        "52352342342SD",
        "524562111SD",
        "52352678678SD",
        "367721Fasdf",
    ]
    for index, element in enumerate(control):
        new_qr_code(f"{index+1} {element}", f"data{index}.png", ver=4, size=3)
    # get_qr_code_data('1.jpg')
    # get_qr_code_data('2.jpg')
    # print(get_qr_code_data('data0.png'))
