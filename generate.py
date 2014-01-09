#!/usr/bin/env python
# coding: utf-8

""" Very quick script to combine elements of the site together

	templates/
		contains templates for the header and footer
	pages/	
		contains the content of each page
	site/
		the target into which the site is created

"""
import glob
import jinja2
import os
import re
import yaml

def construct_yaml_str(self, node):
    # Override the default string handling function 
    # to always return unicode objects
    return self.construct_scalar(node)
yaml.Loader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)


EMAILS = re.compile(r'\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})\b', re.I)
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@jinja2.evalcontextfilter
def paraText(eval_ctx, value):
	value = jinja2.escape(value)
	paras = value.split("\n")
	result = "</p>\n<p>".join(paras)

	# Get correct coding before making replacements for html entities
	try:
		result = result.replace(u"\u00A3", "&pound;")
		result = result.replace(u'\u2013', "-")
		result = result.replace(u'\u2019', "'")
		result = result.replace(u'\u0159', "&#x159;")
		result = result.replace(u'\xa0', " ")
		result = result.replace(u"\xe1", "&aacute;")
		result = EMAILS.sub(r'<a href="mailto:\1">\1</a>', result)
		result_enc = result.decode("utf-8")
	except Exception, exc:
		import pdb; pdb.set_trace()

	if eval_ctx.autoescape:
		result_enc = jinja2.Markup(result_enc)
	return result_enc

def readTemplate(parentDir, templateDir, name):
	path = os.path.join(parentDir, templateDir, name)
	with open(path) as tmplFile:
		tmpl = tmplFile.read()
	return tmpl

def getPages(parentDir, pagesDir):
	"""
	"""
	pages = {}
	pagesDir = os.path.join(parentDir, pagesDir, "*.html")
	return glob.glob(pagesDir)

def generateSite(parentDir, templateDir, pagesDir, contentDir, siteDir):
	""" Generate the site
	"""
	loader = jinja2.FileSystemLoader(['templates', 'pages'])
	env = jinja2.Environment(loader=loader)
	env.trim_blocks = True
	env.autoescape = True
	env.filters['paraText'] = paraText


	pages = getPages(parentDir, pagesDir)

	for page in pages:
		# Get the template
		pageFile = os.path.basename(page)
		template = env.get_template(pageFile)

		# Get teh content to go into the template
		contentFile = os.path.splitext(pageFile)[0] + ".yaml"
		contentPath = os.path.join(parentDir, contentDir, contentFile)

		if os.path.exists(contentPath):
			contentStream = file(contentPath, "r")
			content = yaml.load(contentStream)
#			import pprint
#			pprint.pprint("Path: %r, content: %r" % (contentPath, content))
		else:
			content = {}

		pageContent = template.render(**content)

		try:
			destFile = os.path.join(parentDir, siteDir, pageFile)
			with open(destFile, 'w') as fileOut:
				fileOut.write(pageContent)
		except Exception, exc:
			print "Error writing: %s" % (destFile,)
			print str(exc)
			import pdb; pdb.set_trace()
			raise

if __name__ == "__main__":

	workingDir = os.path.dirname(__file__)
	generateSite(workingDir, 'templates', 'pages', 'content', 'site')
