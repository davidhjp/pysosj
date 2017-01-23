import pysosj


if __name__ == "__main__":
    sss = pysosj.SJChannel("127.0.0.1",1200)
    sss.receive()
    while(1):
        pass
    
