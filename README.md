# pysosj
A Python library for communicating with SOSJ CDs via channels

This python library can be used to exchange String data between SOSJ and a Python program. 

To run the test program (`test/a.sysj`) build everything using `make`. It is a simple clock-domain that receives and sends data continuously to the python program `main.py`:

```java
// test/a.sysj file
CD(output String channel I; input String channel I2;)->{
	String signal S;
	signal done;
	{
		while(true){
			emit S("okay");
			await(done);
			emit S("ha");
			await(done);
		}
	}
	||
	{
		while(true){
			await(S);
			send I(#S);
			emit done;
		}
	}
	||
	{
		while(true){
			receive I2;
			System.out.println("Received "+#I2);
			pause;
		}
	}
}
```

## Using pysosj library
* _class_ `pysosj.SJChannel(local_ip,local_port,dest_ip,dest_port)`

  This uses TCP protocol to exchange channel data with SOSJ CD. It requires ip and port numbers of a local machine as well as a remote SOSJ subsystem.
 
  `settimeout(time)`
  This function sets the timeout value in seconds. `send()` and `receive()` will only block for the amount of time specified using this function

  `close()`
  This function terminates any thread invoked by `pysosj.SJChannel`
  
  `send(fromChan,toChan,value)`
  This function sends data `value` from `fromChan` to `toChan`. Naming convention for channels is `<CDname>.<ChanName>`
  
  `receive(toChan, fromChan)`
  This function receives data from `fromChan`. It returns a received string if the operation is successful, otherwise returns `None`.

An example of using this library is shown in `main.py`

