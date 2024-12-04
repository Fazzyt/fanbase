import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-8s] - (%(funcName)s@%(filename)s:%(lineno)d): %(message)s",
    filename="fanbase.log",
    filemode="a",
)
