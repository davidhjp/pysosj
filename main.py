import pysosj


if __name__ == "__main__":
    sss = pysosj.SJChannel("127.0.0.1", 1200, "127.0.0.1", 1100);
    while 1:
    	val = sss.receive("CD2.I", "CD.I")
    	print "received " + val
    	sss.send("CD2.I2", "CD.I2", "hallo")
    	print "sent"
    sss.close()
    while(1):
        pass
    
