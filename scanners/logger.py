import logging

def setup_logger(log_file):
    # 创建日志记录器
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    # 创建文件处理程序
    file_handler = logging.FileHandler(log_file)

    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 设置文件处理程序的格式化器
    file_handler.setFormatter(formatter)

    # 将文件处理程序添加到日志记录器
    logger.addHandler(file_handler)

    return logger