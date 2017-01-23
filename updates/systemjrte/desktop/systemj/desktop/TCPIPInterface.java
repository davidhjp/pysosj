package systemj.desktop;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;

import systemj.common.InterfaceManager;
import systemj.interfaces.GenericInterface;
import systemj.interfaces.GenericChannel;
import com.google.gson.*;
import java.util.*;
import java.io.*;
import java.util.stream.*;

public class TCPIPInterface extends GenericInterface implements Runnable {
	private String ip;
	private int port;
	private String ssname; // May be used later? Not ATM
	private Object[] buffer;
	
	@Override
	public void configure(Hashtable ht) {
		if(ht.containsKey("Interface")){
			// This can be used later..
		}
		if(ht.containsKey("Args")){
			String[] args = ((String)ht.get("Args")).trim().split(":");
			if(args.length != 2)
				throw new RuntimeException("Incorrect Args for TCP/IP interface : must be <IP>:<Port>");
			ip = args[0];
			port = new Integer(args[1]).intValue();
		}
		else
			throw new RuntimeException("Missing Args");
		
		if(ht.containsKey("SubSystem")){
			ssname = ((String)ht.get("SubSystem")).trim();
		}
	}

	@Override
	public void invokeReceivingThread() {
		new Thread(this).start();
	}

	@Override
	public void setup(Object[] o) {
		buffer = o;
	}

	Gson gson = new Gson();

	@Override
	public boolean transmitData() {
		try {
			Socket client = new Socket(ip, port);
			// Uses simple object output stream. no hassle.
			DataOutputStream out = new DataOutputStream(client.getOutputStream());
			String d = gson.toJson(buffer);
			byte[] b = d.getBytes();
			out.write(b,0,b.length);
			client.close();
		}
		catch(java.net.ConnectException e){
			System.out.println("Could not reach server "+ip+":"+port);
			return false;
		}
		catch(Exception e){
			e.printStackTrace();
			return false;
		}
		
		return true;
	}

	@Override
	public void receiveData() {/* empty */}

	@Override
	public void run() {
		// This replace receive data for TCP case
		try {
			ServerSocket serverSocket = new ServerSocket(port, 50, InetAddress.getByName(ip));
			while(true){
				//System.out.println("Listening on "+ip+" "+port);
				Socket socket = serverSocket.accept();
				String s = "";
				try (BufferedReader buffer = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {
					s = buffer.lines().collect(Collectors.joining("\n"));
				}
				Object[] o = new Object[5];
				JsonElement je = new JsonParser().parse(s);
				JsonArray ja = je.getAsJsonArray();
				o[0] = (Object)ja.get(0).getAsString();
				o[1] = (Object)ja.get(1).getAsInt();
				o[2] = (Object)ja.get(2).getAsInt();
				o[3] = (Object)ja.get(3).getAsInt();
				if(ja.size() == 5)
					o[4] = (Object)ja.get(4).getAsString();
			
				System.out.println("received "+Arrays.toString(o));
				super.forwardChannelData(o);
				// socket.setSoLinger(true, 0);
				socket.close();
			}
		}
		catch(RuntimeException e){
			e.printStackTrace();
		}
		catch(IOException e){
			System.err.println("Error occured in TCPIPInterface, check the TCP/IP setting in the XML Interface");
			e.printStackTrace();
		}
		finally{
			System.exit(1);
		}

	}

}
