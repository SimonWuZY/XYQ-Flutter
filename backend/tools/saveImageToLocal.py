import os
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = r'\www\wwwroot\xyq\tmpFile'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def saveImageToLocal(image):
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        local_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(local_path)
        return local_path
