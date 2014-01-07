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
#	result = value.replace("\xc2", "&pound;")
#	result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') for p in _paragraph_re.split(jinja2.escape(value)))

	#value = jinja2.escape(value)
	paras = value.split("\n")
	result = "<p>" + "</p>\n<p>".join(paras) + "</p>"

	# Get correct coding before making replacements for html entities
	result = result.encode("utf-8")
	result = result.replace("£", "&pound;")
	result = result.replace(u'\xa0', " ")
	result = EMAILS.sub(r'<a href="mailto:\1">\1</a>', result)

	if eval_ctx.autoescape:
		result = jinja2.Markup(result)
	return result

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
			import pprint
			pprint.pprint("Path: %r, content: %r" % (contentPath, content))
		else:
			content = {}

		pageContent = template.render(**content)

		try:
			destFile = os.path.join(parentDir, siteDir, pageFile)
			with open(destFile, 'w') as fileOut:
				fileOut.write(pageContent)
		except:
			print "Error writing: %s" % (destFile,)
			raise

if __name__ == "__main__":

	workingDir = os.path.dirname(__file__)
	generateSite(workingDir, 'templates', 'pages', 'content', 'site')
