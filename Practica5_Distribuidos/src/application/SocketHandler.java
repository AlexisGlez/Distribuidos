package application;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

public class SocketHandler {

	public static final int PORT = 6001;
	public static final String IP_ADDRESS = "localhost";
	public static final int BUFFER_LENGTH = 4096;

	private InetAddress address;
	private DatagramSocket datagramSocket;
	private byte[] buffer;

	public SocketHandler() {
		try {
			datagramSocket = new DatagramSocket();
			address = InetAddress.getByName(IP_ADDRESS);
		} catch (SocketException e) {
			e.printStackTrace();
		} catch (UnknownHostException e) {
			e.printStackTrace();
		}
	}

	public void sendMessage(String message) {
		buffer = message.getBytes();
        DatagramPacket packet = new DatagramPacket(buffer, buffer.length > BUFFER_LENGTH ? BUFFER_LENGTH : buffer.length, address, PORT);
        try {
			datagramSocket.send(packet);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public String getMessage() {
		buffer = new byte[BUFFER_LENGTH];
		DatagramPacket datagramPacket = new DatagramPacket(buffer, buffer.length, address, PORT);
		try {
			datagramSocket.receive(datagramPacket);
			return new String(datagramPacket.getData(), 0, datagramPacket.getLength());
		} catch (IOException e) {
			e.printStackTrace();
		}
		return null;
	}

}
