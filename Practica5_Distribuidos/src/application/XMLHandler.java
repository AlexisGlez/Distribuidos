package application;

import java.io.IOException;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.HashMap;
import java.util.Map;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

public class XMLHandler {

	private static final String XML_ROOT = "message";
	private static final String CLOSING_ROOT = "/message>";

	public static final String XML_MESSAGE_CONTENT = "content";
	public static final String XML_MESSAGE_FROM = "from";
	public static final String XML_MESSAGE_TO = "to";
	public static final String XML_MESSAGE_ACTION = "action";
	public static final String XML_MESSAGE_ID = "id";

	public static Document createXMLDocument(HashMap<String, String> tags){
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder;
		try {
			builder = factory.newDocumentBuilder();
			Document doc = builder.newDocument();

	        Element root = doc.createElement(XML_ROOT);
	        doc.appendChild(root);

	        Element element;
	        for (Map.Entry<String, String> tag : tags.entrySet()) {
	        	element = doc.createElement(tag.getKey());
	        	element.appendChild(doc.createTextNode(tag.getValue()));
	        	root.appendChild(element);
	        }
	        return doc;
		} catch (ParserConfigurationException e) {
			e.printStackTrace();
		}
		return null;
    }

	public static String parseXMLToString(Document document) {
		TransformerFactory transformerFactory = TransformerFactory.newInstance();
		try {
	        Transformer transformer = transformerFactory.newTransformer();
	        transformer.setOutputProperty(OutputKeys.METHOD, "xml");
	        transformer.setOutputProperty(OutputKeys.ENCODING, "UTF-8");
	        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
	        DOMSource domSource = new DOMSource(document);
	        StringWriter stringWriter = new StringWriter();
	        transformer.transform(domSource, new StreamResult(stringWriter));
	        return stringWriter.toString();
		} catch (TransformerConfigurationException e) {
			e.printStackTrace();
		} catch (TransformerException e) {
			e.printStackTrace();
		}
		return "";
	}

	public static Element parseStringToXML(String xml) {
		Element root = null;

        try {
            DocumentBuilderFactory documentBuilderFactory = DocumentBuilderFactory.newInstance();
            DocumentBuilder documentBuilder = documentBuilderFactory.newDocumentBuilder();
            String xmlSanitized = "<?xml version=\"1.0\"?>" + xml.substring(xml.indexOf(XML_ROOT) - 1, xml.lastIndexOf(CLOSING_ROOT) + CLOSING_ROOT.length());
            Document document = documentBuilder.parse(new InputSource(new StringReader(xmlSanitized)));
            document.getDocumentElement().normalize();
            NodeList nodeList = document.getElementsByTagName(XML_ROOT);
            root = (Element) nodeList.item(0);
        } catch (ParserConfigurationException e) {
			e.printStackTrace();
		} catch (SAXException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}

        return root;
	}

	public static String getElementByTagName(Element element, String tagName) {
		return element.getElementsByTagName(tagName).item(0).getTextContent();
	}

}
