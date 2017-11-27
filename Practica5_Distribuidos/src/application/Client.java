package application;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

import org.w3c.dom.Element;

public class Client {

	private static final int RETRY_TIMES = 10;
	private static final int RETRY_WAIT_TIME = 3500;

	private static final int MESSAGE_ACTION_ACK = 0;
	private static final int MESSAGE_ACTION_PRIVATE = 1;
	private static final int MESSAGE_ACTION_ALL = 2;
	private static final int MESSAGE_ACTION_BYE = 3;
	private static final int MESSAGE_ACTION_NEW = 4;
	private static final int MESSAGE_ACTION_USERS = 5;

	private static final String MESSAGE_LIST_USERS = "@users";
	private static final String MESSAGE_PRIVATE_MESSAGE = "@to";
	private static final String MESSAGE_EXIT = "exit";

	private static BufferedReader bufferedReader;
	private static SocketHandler socketHandler;

	private static ConcurrentHashMap<Integer, String> messages;
	private static AtomicInteger messageId;
	private static String clientName;

	public static void main(String[] args) {
		bufferedReader = new BufferedReader(new InputStreamReader(System.in));
		socketHandler = new SocketHandler();
		messageId = new AtomicInteger();
		messages = new ConcurrentHashMap<>();

        System.out.print("What is your name?: ");
        clientName = readLine();
        while (clientName.length() == 0 || clientName.contains(" ")) {
        	System.out.println("Spaces are not allowed, Please give me your name: ");
        	clientName = readLine();
        }
        Receiver receiver = new Receiver(socketHandler);

        Sender sender = new Sender(socketHandler);
        sender.setAction(MESSAGE_ACTION_NEW).setMessage(clientName).setMessageId(messageId.getAndIncrement());
        sender.send();

        receiver.start();
        sender.start();
        try {
			receiver.join();
			sender.join();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}

	private static String readLine() {
		try {
			return bufferedReader.readLine();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return null;
	}

	static class Receiver extends Thread {

		private SocketHandler socketHandler;

		private String message;
		private Element root;
		private int action;

		public Receiver(SocketHandler socketHandler) {
			this.socketHandler = socketHandler;
		}

		@Override
		public void run() {
			while (true) {
				message = socketHandler.getMessage();
				root = XMLHandler.parseStringToXML(message);
				action = Integer.parseInt(XMLHandler.getElementByTagName(root, XMLHandler.XML_MESSAGE_ACTION));
				switch (action) {
					case MESSAGE_ACTION_ACK:
						messages.remove(Integer.parseInt(XMLHandler.getElementByTagName(root, XMLHandler.XML_MESSAGE_ID)));
						break;
					case MESSAGE_ACTION_PRIVATE:
					case MESSAGE_ACTION_ALL:
						System.out.println(
								XMLHandler.getElementByTagName(root, XMLHandler.XML_MESSAGE_FROM) +
								": " +
								XMLHandler.getElementByTagName(root, XMLHandler.XML_MESSAGE_CONTENT)
						);
						break;
					case MESSAGE_ACTION_BYE:
						System.out.println("Client disconnected successfully.");
						return;
					case MESSAGE_ACTION_NEW:
						System.out.println("Client is now connected to server.");
						break;
					case MESSAGE_ACTION_USERS:
						System.out.println(XMLHandler.getElementByTagName(root, XMLHandler.XML_MESSAGE_CONTENT));
						break;
					default:
						System.out.println("Invalid message received.");
						break;
				}
			}
		}
	}

	static class Sender extends Thread {

		private SocketHandler socketHandler;

		private String message;
		private int id;
		private int action;
		private HashMap<String, String> tags;

		public Sender(SocketHandler socketHandler) {
			this.socketHandler = socketHandler;
			tags = new HashMap<>();
		}

		public Sender setAction(int action) {
			this.action = action;
			return this;
		}

		public Sender setMessage(String message) {
			this.message = message;
			return this;
		}

		public Sender setMessageId(int messageId) {
			this.id = messageId;
			return this;
		}

		@Override
		public void run() {
			while (true) {
				message = readLine();
				if (message.length() <= 0) continue;

				id = messageId.getAndIncrement();

				if (message.startsWith(MESSAGE_LIST_USERS)) {
					action = MESSAGE_ACTION_USERS;
					message = message.substring(MESSAGE_LIST_USERS.length());
				} else if (message.startsWith(MESSAGE_PRIVATE_MESSAGE)) {
					action = MESSAGE_ACTION_PRIVATE;
					String[] parts = message.split(" ");
					message = message.substring(MESSAGE_PRIVATE_MESSAGE.length() + 2 + parts[1].length());
					tags.put(XMLHandler.XML_MESSAGE_TO, parts[1]);
				} else if (message.equals(MESSAGE_EXIT)) {
					action = MESSAGE_ACTION_BYE;
				} else {
					action = MESSAGE_ACTION_ALL;
				}
				send();
				if (action == MESSAGE_ACTION_BYE) return;
			}
		}

		public void send() {
			if (!tags.containsKey(XMLHandler.XML_MESSAGE_TO)) {
				tags.put(XMLHandler.XML_MESSAGE_TO, "");
			}
			tags.put(XMLHandler.XML_MESSAGE_ACTION, String.valueOf(action));
			tags.put(XMLHandler.XML_MESSAGE_ID, String.valueOf(id));
			tags.put(XMLHandler.XML_MESSAGE_FROM, clientName);
			tags.put(XMLHandler.XML_MESSAGE_CONTENT, message);
			String xmlMessage = XMLHandler.parseXMLToString(XMLHandler.createXMLDocument(tags));
			new Retrier(socketHandler, xmlMessage, id).start();
			tags.clear();
		}

	}

	static class Retrier extends Thread {

		private SocketHandler socketHandler;

		private String message;

		private int messageId;

		public Retrier(SocketHandler socketHandler, String message, int messageId) {
			this.socketHandler = socketHandler;
			this.message = message;
			this.messageId = messageId;
			messages.put(messageId, message);
		}

		@Override
		public void run() {
			for (int i = 0; i < RETRY_TIMES; i++) {
				try {
					if (!messages.containsKey(messageId)) return;
					socketHandler.sendMessage(message.trim());
					Thread.sleep(RETRY_WAIT_TIME);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
			System.out.println("Unable to send message.");
		}

	}

}
