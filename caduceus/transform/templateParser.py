import sys
if sys.version_info < (3, 0):
    from HTMLParser import HTMLParser, HTMLParseError
else:
    from html.parser import HTMLParser, HTMLParseError
from caduceus.transform.template import CaduceusTemplate
from caduceus.transform.templateHtmlComment import CaduceusTemplateHtmlComment
from caduceus.transform.templateHtmlTag import CaduceusTemplateHtmlTag
from caduceus.transform.templateHtmlText import CaduceusTemplateHtmlText
from caduceus.transform.templatePython import CaduceusTemplatePython
import os

class CaduceusTemplateParser(HTMLParser):
    def __init__(self, filePath, rootPath, caduceusPath = None):
        HTMLParser.__init__(self)
        if os.path.isfile(filePath):
            self._path, _filename = os.path.split(filePath)
        else:
            self._path = filePath
        self._rootPath = rootPath
        self._caduceusPath = caduceusPath
        
        # print("#### %s - %s" % (self.__class__.__name__, filePath))
        
        self._templateRoot = CaduceusTemplate(self._path, self._rootPath, self._caduceusPath)
        self._curToken = self._templateRoot
        
    def _concordionCompatibility(self, tag, attrs):
        # Concordion compatibility
        fixedAttrs = []
        pythonToken = None
        for attr in attrs:
            if attr[0] == "concordion:assertequals":
                #print attr[0]
                pythonToken = CaduceusTemplatePython("assertEqual %s" % attr[1].replace("#", "_"), self._path, self._rootPath)
            elif attr[0] == "concordion:set":
                #print attr[0]
                pythonToken = CaduceusTemplatePython("set %s" % attr[1].replace("#", "_"), self._path, self._rootPath)
            elif attr[0] == "concordion:execute":
                #print attr[0]
                statment = attr[1].replace("#TEXT", "@")
                statment = statment.replace("#", "_")
                pythonToken = CaduceusTemplatePython("exec %s" % statment, self._path, self._rootPath)
            else:
                #print attr[0]
                fixedAttrs.append(attr)
                
        return (fixedAttrs, pythonToken)
    
    def handle_starttag(self, tag, attrs):
        #print "Encountered a start tag: %s attrib %s" % (tag, attrs)
        
        attrs, pythonToken = self._concordionCompatibility(tag, attrs)
        
        token = CaduceusTemplateHtmlTag(tag, attrs)
        self._curToken = self._curToken.addToken(token)
        
        if tag == "head":
            self._templateRoot.setHeadTagRef(token)
        elif tag == "html":
            self._templateRoot.setHtmlTagRef(token)

        if pythonToken:
            self._curToken = self._curToken.addToken(pythonToken)
        
    def handle_endtag(self, tag):
        #print "Encountered  an end tag: %s" % tag
        nextToken = self._curToken.endTag(tag)
        if nextToken:
            self._curToken = nextToken
        else:
            token = CaduceusTemplateHtmlTag(tag, [], False, True)
            self._curToken.addToken(token)
        
    def handle_startendtag(self, tag, attrs):
        #print "Encountered a start end tag: %s attrib %s" % (tag, attrs)
        attrs, pythonToken = self._concordionCompatibility(tag, attrs)

        if pythonToken:
            token = CaduceusTemplateHtmlTag(tag, attrs)
            self._curToken = self._curToken.addToken(token)
            self._curToken = self._curToken.addToken(pythonToken)
            self._curToken = self._curToken.endTag(tag)
        else:
            token = CaduceusTemplateHtmlTag(tag, attrs, True)
            self._curToken = self._curToken.addToken(token)
            self._curToken = self._curToken.endTag(tag)
        
    def get_starttag_text(self, text):
        #print "Encountered  an start text:", text
        pass
    
    def handle_data(self, data):
        #print "Encountered   some data:", data
        token = CaduceusTemplateHtmlText(data)
        self._curToken = self._curToken.addToken(token)
        
    def handle_comment(self, data):
        token = CaduceusTemplateHtmlComment(data)
        self._curToken = self._curToken.addToken(token)		
    
    def handle_pi(self, data):
        #print "Encountered   pi:", data
        token = CaduceusTemplatePython(data, self._path, self._rootPath)
        self._curToken = self._curToken.addToken(token)
    
    @staticmethod
    def _getTemplateFileContent(filePath):
        content = None
        file = open(filePath, 'r')
        if file:
            try:
                content = file.read()
            finally:
                file.close()
                
        return content
    
    @staticmethod
    def parseTemplateFile(filePath, rootPath, caduceusPath):
        content = CaduceusTemplateParser._getTemplateFileContent(filePath)	
        if content:
            
            parser = CaduceusTemplateParser(filePath, rootPath, caduceusPath)
            parser.feed(content)
            
            return parser._templateRoot
        
        return None
    
    @staticmethod
    def _findPartialFile(partialName, filePath, rootPath, _checkRootPartials = True):
        # Check if partial is in current path		
        partialFullPath = os.path.join(filePath, "_%s.html" % partialName)
        if os.path.exists(partialFullPath):
            return partialFullPath
        
        # Check if partial is in a parent path (till root)
        if filePath != rootPath:
            parentDir = os.path.abspath(os.path.join(filePath, ".."))
            partialFullPath = CaduceusTemplateParser._findPartialFile(partialName, parentDir, rootPath, False)
            if partialFullPath:
                return partialFullPath
        
        if _checkRootPartials:
            # Check if partial is in subdirectories 'partial' from root path
            for root, dirs, files in os.walk(os.path.join(rootPath, "partials")):
                for file in files:
                    if file == ("_%s.html" % partialName):
                        return os.path.join(root, file)
                        
        return None
    
    @staticmethod
    def parsePartialFile(partialName, filePath, rootPath):		
        partialFullPath = CaduceusTemplateParser._findPartialFile(partialName, filePath, rootPath)
        if not partialFullPath:
            print("Can't find partial file '_%s.html' from %s" % (partialName, rootPath))
            return None
            
        content = CaduceusTemplateParser._getTemplateFileContent(partialFullPath)	
        if content:
            parser = CaduceusTemplateParser(filePath, rootPath)
            parser.feed(content)
            
            return parser._templateRoot

        print("Can't read partial file '%s'" % partialFullPath)   
        return None	
