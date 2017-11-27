import xml.etree.ElementTree as XML

def createXML(action, source, to, id, content):
	xmlRoot = XML.Element('message')
	actionTag = XML.Element('action')
	actionTag.text = action
	xmlRoot.append(actionTag)
	sourceTag = XML.Element('source')
	sourceTag.text = source
	xmlRoot.append(sourceTag)
	toTag = XML.Element('to')
	toTag.text = to
	xmlRoot.append(toTag)
	contentTag = XML.Element('content')
	contentTag.text = content
	xmlRoot.append(contentTag)
	idTag = XML.Element('id')
	idTag.text = str(id)
	xmlRoot.append(idTag)
	return XML.tostring(xmlRoot)
