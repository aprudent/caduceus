from caduceus.transform.templateEntity import CaduceusTemplateEntity, CaduceusTemplateResults
import re
import traceback
import os
import types
import sys

class CaduceusTemplatePython(CaduceusTemplateEntity):
    def __init__(self, data, path, rootPath):
        CaduceusTemplateEntity.__init__(self)
        # Strip ? and white spaces at end of string
        self._data = data.rstrip(" ?\n")
        self._path = path
        self._rootPath = rootPath
            
    def render(self, dictGlob, dictLoc, tmplResults):
        # Render childs
        
        match = re.match("(assertEqual|assertNotEqual) (.+)", self._data, re.DOTALL)
        if match:
            return self._assert(match.group(1), match.group(2), dictGlob, dictLoc, tmplResults)
            
        match = re.match("assert (.+)", self._data, re.DOTALL)
        if match:
            return self._assertCustom(match.group(1), dictGlob, dictLoc, tmplResults)
            
        match = re.match("exec (.+)", self._data, re.DOTALL)
        if match:
            return self._exec(match.group(1), dictGlob, dictLoc, tmplResults)

        match = re.match("echo (.+)", self._data, re.DOTALL)
        if match:
            return self._echo(match.group(1), dictGlob, dictLoc, tmplResults)

        match = re.match("set (.+)", self._data, re.DOTALL)
        if match:
            return self._setVariable(match.group(1), dictGlob, dictLoc, tmplResults)				

        match = re.match("for\s+(.+)\s+in\s+(.+)", self._data, re.DOTALL)
        if match:
            return self._loopFor(match.group(1), match.group(2), dictGlob, dictLoc, tmplResults)				

        match = re.match("include (.+)", self._data, re.DOTALL)
        if match:
            return self._include(match.group(1), dictGlob, dictLoc, tmplResults)				

        # Skip entity, only render childs
        return CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
    
    def _assert(self, assertionType, pythonStmt, dictGlob, dictLoc, tmplResults):
        # Get comparaison text (ie: render childs)
        content = CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
        
        try:
            result = eval("str(%s)" % pythonStmt, dictGlob, dictLoc)
            
            if assertionType == "assertEqual":
                comparaison = '"%s" == "%s"' % (result, content)
            else:
                comparaison = '"%s" != "%s"' % (result, content)
                
            if eval(comparaison, dictGlob, dictLoc):
                tagId = tmplResults.addAssertion(CaduceusTemplateResults.SUCCESS, None)
                return '<span id="%s" class="success">%s</span>' % (tagId, content)
            else:
                tagId = tmplResults.addAssertion(CaduceusTemplateResults.FAILURE, comparaison)
                return '<span id="%s" class="failure"><span class="expected">%s</span>%s</span>' % (tagId, content, result)
        except Exception:
            traceback.print_exc()
            tagId = tmplResults.addAssertion(CaduceusTemplateResults.ERROR, traceback.format_exc())
            return '<span id="%s" class="failure"><span class="expected">%s</span><pre class="exception">%s</pre></span>' % (tagId, content, traceback.format_exc())
    
    def _assertCustom(self, pythonStmt, dictGlob, dictLoc, tmplResults):
        # Get comparaison text (ie: render childs)
        content = CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
        
        # test if @ shorcut is in use
        if '@' in pythonStmt:
            # Use content to get replacement for @
            pythonStmt = pythonStmt.replace("@", '"%s"' % content)
        else:
            pythonStmt = '%s("%s")' % (pythonStmt, content)

        try:
            result = eval(pythonStmt, dictGlob, dictLoc)

            if sys.version_info < (3, 0):
                isTuple = type(result) is types.TupleType
            else:
                isTuple = type(result) is tuple
            
            if isTuple:
                if result[0]:
                    tagId = tmplResults.addAssertion(CaduceusTemplateResults.SUCCESS, None)
                    return '<span id="%s" class="success">%s</span>' % (tagId, result[1])
                else:
                    tagId = tmplResults.addAssertion(CaduceusTemplateResults.FAILURE, pythonStmt)
                    return '<span id="%s" class="failure"><span class="expected">%s</span>%s</span>' % (tagId, result[1], result[2])	
            elif result:
                tagId = tmplResults.addAssertion(CaduceusTemplateResults.SUCCESS, None)
                return '<span id="%s" class="success">%s</span>' % (tagId, content)
            else:
                tagId = tmplResults.addAssertion(CaduceusTemplateResults.FAILURE, pythonStmt)
                return '<span id="%s" class="failure"><span class="expected">%s</span>%s</span>' % (tagId, content, result)
        except Exception:
            traceback.print_exc()
            tagId = tmplResults.addAssertion(CaduceusTemplateResults.ERROR, traceback.format_exc())
            return '<span id="%s" class="failure"><span class="expected">%s</span><pre class="exception">%s</pre></span>' % (tagId, content, traceback.format_exc())
                
    def _exec(self, pythonStmt, dictGlob, dictLoc, tmplResults):
        # We must eval python code before rendering childs,
        # except if @ shorcut is in use
        bRunChilds = True
        content = ""
        if '@' in pythonStmt:
            # Use content to get replacement for @
            bRunChilds = False
            content = CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
            pythonStmt = pythonStmt.replace("@", '"%s"' % content)
        
        try:
            # exec pythonStmt in dictGlob, dictLoc
            exec(pythonStmt, dictGlob, dictLoc)
        except Exception:
            traceback.print_exc()
            tagId = tmplResults.addExceptionsError(traceback.format_exc())
            content = '<span id="%s" class="failure"><pre class="exception">%s</pre></span>' % (tagId, traceback.format_exc())
        
        if bRunChilds:
            return content + CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
        else:
            return content

    def _echo(self, pythonStmt, dictGlob, dictLoc, tmplResults):
        content = ""
        try:
            content = eval(pythonStmt, dictGlob, dictLoc)
        except Exception:
            traceback.print_exc()
            tagId = tmplResults.addExceptionsError(traceback.format_exc())
            content = '<span id="%s" class="failure"><pre class="exception">%s</pre></span>' % (tagId, traceback.format_exc())

        return str(content) + CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
        
    def _setVariable(self, variable, dictGlob, dictLoc, tmplResults):
        # Get variable value (ie: render childs)
        content = CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
        
        pythonStmt = '%s = "%s"' % (variable, content)
        try:
            #exec pythonStmt in dictGlob, dictLoc
            exec(pythonStmt, dictGlob, dictLoc)
        except Exception:
            traceback.print_exc()
            tagId = tmplResults.addExceptionsError(traceback.format_exc())
            return '<span id="%s" class="failure"><pre class="exception">%s</pre></span>' % (tagId, traceback.format_exc())
        
        return content
    
    def _loopFor(self, varName, listName, dictGlob, dictLoc, tmplResults):
        content = ""
        listName = listName.rstrip(":")
        
        list = eval(listName, dictGlob, dictLoc)
        for i in list:
            
            try:
                exec("%s = (%s)" % (varName, i), dictGlob, dictLoc)
            except:
                dictLoc[varName] = i
                
            content += CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
    
        return content
    
    def _include(self, partialName, dictGlob, dictLoc, tmplResults):
        from caduceus.transform.templateParser import CaduceusTemplateParser
        
        # partialName may contain arguments
        #print("#### partialName : %s" % partialName)
        match = re.match("^([\S+]+)\((.+)\)$", partialName, re.DOTALL)
        if match:

            #print("#### %s =>\ngrp1=%s\ngrp2=%s" % (partialName, match.group(1), match.group(2)))
            partialName = match.group(1)
            templateDictLoc = dictLoc # dictLoc.copy()
            # Replace , by ; and evaluate arguments to pass to the partial
            try:
                args = match.group(2)
                templateDictLoc['addPartialArgs'] = CaduceusTemplatePython.addPartialArgs
                exec("addPartialArgs(globals(), locals(), %s)" % args, dictGlob, templateDictLoc)
            except IndexError:
                print("### Index error for partial %s" % partialName)
        else:
            templateDictLoc = dictLoc
        
        content = ""
        template = CaduceusTemplateParser.parsePartialFile(partialName, self._path, self._rootPath)
        if template:
            content = template.render(dictGlob, templateDictLoc, tmplResults)
    
        return content + CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)

    @staticmethod
    def addPartialArgs(dictGlob, dictLoc, **kwargs):
        # print("### addPartialArgs kwargs %s" % kwargs)
        for key, value in kwargs.items():
            dictLoc[key] = value
        
