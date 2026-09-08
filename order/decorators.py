def logger(func):
    def wrapper(*args, **kwargs):
        print("[LOG] 시작")

        result = func(*args, **kwargs)

        print("[LOG] 종료")
        return result  

    return wrapper   

