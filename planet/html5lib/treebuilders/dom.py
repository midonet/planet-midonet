import _base
from xml.dom import minidom, Node

import re
illegal_xml_chars = re.compile("[\x01-\x08\x0B\x0C\x0E-\x1F]")

class AttrList:
    def __init__(self, element):
        self.element = element
    def __iter__(self):
        return self.element.attributes.items().__iter__()
    def __setitem__(self, name, value):
        value=illegal_xml_chars.sub(u'\uFFFD',value)
        self.element.setAttribute(name, value)
    def items(self):
        return self.element.attributes.items()
    def keys(self):
        return self.element.attributes.keys()
    def __getitem__(self, name):
        return self.element.getAttribute(name)

class NodeBuilder(_base.Node):
    def __init__(self, element):
        _base.Node.__init__(self, element.nodeName)
        self.element = element

    def appendChild(self, node):
        node.parent = self
        self.element.appendChild(node.element)

    def insertText(self, data, insertBefore=None):
        data=illegal_xml_chars.sub(u'\uFFFD',data)
        text = self.element.ownerDocument.createTextNode(data)
        if insertBefore:
            self.element.insertBefore(text, insertBefore.element)
        else:
            self.element.appendChild(text)

    def insertBefore(self, node, refNode):
        self.element.insertBefore(node.element, refNode.element)
        node.parent = self

    def removeChild(self, node):
        self.element.removeChild(node.element)
        node.parent = None

    def reparentChildren(self, newParent):
        while self.element.hasChildNodes():
            child = self.element.firstChild
            self.element.removeChild(child)
            newParent.element.appendChild(child)
        self.childNodes = []

    def getAttributes(self):
        return AttrList(self.element)

    def setAttributes(self, attributes):
        if attributes:
            for name, value in attributes.items():
                value=illegal_xml_chars.sub(u'\uFFFD',value)
                self.element.setAttribute(name, value)

    attributes = property(getAttributes, setAttributes)

    def cloneNode(self):
        return NodeBuilder(self.element.cloneNode(False))

    def hasContent(self):
        return self.element.hasChildNodes()

class TreeBuilder(_base.TreeBuilder):
    def documentClass(self):
        self.dom = minidom.getDOMImplementation().createDocument(None,None,None)
        return self

    def doctypeClass(self,name):
        domimpl = minidom.getDOMImplementation()
        return NodeBuilder(domimpl.createDocumentType(name,None,None))

    def elementClass(self, name):
        return NodeBuilder(self.dom.createElement(name))
        
    def commentClass(self, data):
        return NodeBuilder(self.dom.createComment(data))

    def appendChild(self, node):
        self.dom.appendChild(node.element)

    def testSerializer(self, element):
        return testSerializer(element)

    def getDocument(self):
        return self.dom

    def insertText(self, data, parent=None):
        data=illegal_xml_chars.sub(u'\uFFFD',data)
        if parent <> self:
            _base.TreeBuilder.insertText(self, data, parent)
        else:
            # HACK: allow text nodes as children of the document node
            if hasattr(self.dom, '_child_node_types'):
                if not Node.TEXT_NODE in self.dom._child_node_types:
                    self.dom._child_node_types=list(self.dom._child_node_types)
                    self.dom._child_node_types.append(Node.TEXT_NODE)
            self.dom.appendChild(self.dom.createTextNode(data))

    name = None

def testSerializer(element):
    element.normalize()
    rv = []
    def serializeElement(element, indent=0):
        if element.nodeType == Node.DOCUMENT_TYPE_NODE:
            rv.append("|%s<!DOCTYPE %s>"%(' '*indent, element.name))
        elif element.nodeType == Node.DOCUMENT_NODE:
            rv.append("#document")
        elif element.nodeType == Node.COMMENT_NODE:
            rv.append("|%s<!-- %s -->"%(' '*indent, element.nodeValue))
        elif element.nodeType == Node.TEXT_NODE:
            rv.append("|%s\"%s\"" %(' '*indent, element.nodeValue))
        else:
            rv.append("|%s<%s>"%(' '*indent, element.nodeName))
            if element.hasAttributes():
                for name, value in element.attributes.items():
                    rv.append('|%s%s="%s"' % (' '*(indent+2), name, value))
        indent += 2
        for child in element.childNodes:
            serializeElement(child, indent)
    serializeElement(element, 0)

    return "\n".join(rv)