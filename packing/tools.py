# encoding=utf8


def handle_uploaded_file(file, path):
    try:
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return True
    except:
        return False
