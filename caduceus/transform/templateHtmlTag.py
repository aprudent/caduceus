from caduceus.transform.templateEntity import CaduceusTemplateEntity

class CaduceusTemplateHtmlTag(CaduceusTemplateEntity):
	def __init__(self, tag, attribs, isEmptyTag = False, isCloseOnlyTag = False):
		CaduceusTemplateEntity.__init__(self)
		self._tag = tag
		self._attribs = attribs
		self._isEmptyTag = isEmptyTag
		self._isCloseOnlyTag = isCloseOnlyTag
		self._isClosedTag = False
	
	def render(self, dictGlob, dictLoc, results):
		htmlAttribs = ""
		for attr in self._attribs:
			htmlAttribs += ' %s="%s"' % (attr[0], attr[1])
		
		if self._isCloseOnlyTag:
			return "</%s>" % (self._tag)
		
		if self._isEmptyTag:
			return "<%s%s />" % (self._tag, htmlAttribs)

		content = CaduceusTemplateEntity.render(self, dictGlob, dictLoc, results)

		if self._tag == "title":
			results.setTitle(content)			
			
		if self._isClosedTag:
			return "<%s%s>%s</%s>" % (self._tag, htmlAttribs,
								   content, self._tag)
		
		return "<%s%s>%s" % (self._tag, htmlAttribs, content)

	def _matchTag(self, tag):
		return tag == self._tag