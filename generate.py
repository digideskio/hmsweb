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
from docutils.core import publish_parts
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
MAILTO = re.compile(r'mailto:([^|]+)\|([^|]+)\|')
LINK = re.compile(r'link:([^|]+)\|([^|]+)\|')
BOLD = re.compile(r'bold:([^|]+)\|')
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@jinja2.evalcontextfilter
def paraText(eval_ctx, value):
	value = jinja2.escape(value)
	value = value.replace("::\n", jinja2.Markup(":<br/>"))
	paras = value.split("\n")
	result = "</p>\n<p>".join(paras)

#	rst = publish_parts(source=unicode(value), writer_name='html')['body']
#	result = jinja2.Markup(rst)

	# Get correct coding before making replacements for html entities
	try:
		result = result.replace(u"\u00A3", jinja2.Markup("&pound;"))
		result = result.replace(u'\u2013', jinja2.Markup("-"))
		result = result.replace(u'\u2019', jinja2.Markup("'"))
		result = result.replace(u'\u0159', jinja2.Markup("&#x159;"))
		result = result.replace(u'\xa0',   jinja2.Markup(" "))
		result = result.replace(u"\xe1",   jinja2.Markup("&aacute;"))
		result = result.replace( u'\xe9',  jinja2.Markup("&eacute;"))
		result = result.replace(u'\u2018', jinja2.Markup("&#x2018;")) # ‘
		result = result.replace(u'\u2019', jinja2.Markup("&#x2019;")) # ‘
		result = result.replace(u'\u201c', jinja2.Markup("&#x201c;")) # “
		result = result.replace(u'\u201d', jinja2.Markup("&#x201d;")) # ”
		result = result.replace(u"\xfc",   jinja2.Markup("&uuml;")) # ü
		result = result.replace(u'\xec',   jinja2.Markup("i")) # ì
		result = result.replace(u"\u1e59",   jinja2.Markup("&#x1E59;"))
		result = result.replace(u"\u1eaf",   jinja2.Markup("&#x1EAF;"))
		result = result.replace(u"\u2019",   jinja2.Markup("&#x2019;"))

		if MAILTO.search(result):
			result = MAILTO.sub(r'<a href="mailto:\1">\2</a>', result)
		else:
			result = EMAILS.sub(r'<a href="mailto:\1">\1</a>', result)

		result = LINK.sub(r'<a href="\1">\2</a>', result)
		result = BOLD.sub(r'<b>\1</b>', result)
		result_enc = result.decode("utf-8")
	except Exception, exc:
		print unicode(exc)
		import pdb; pdb.set_trace()
		raise

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
	env = jinja2.Environment(loader=loader, extensions=['jinja2.ext.loopcontrols'])
	env.trim_blocks = True
	env.autoescape = True
	env.filters['paraText'] = paraText

	pages = getPages(parentDir, pagesDir)


	all_content = {}

	for page in pages:

		# Get the template
		pageFile = os.path.basename(page)
		template = env.get_template(pageFile)

		# Get the content to go into the template
		pageName = os.path.splitext(pageFile)[0]
		contentFile = pageName + ".yaml"
		contentPath = os.path.join(parentDir, contentDir, contentFile)

		if os.path.exists(contentPath):
			contentStream = file(contentPath, "r")
			all_content[pageName] = yaml.load(contentStream)


	for page in pages:
		multiPage = False

		# Get the template
		pageFile = os.path.basename(page)
		pageName = os.path.splitext(pageFile)[0]

		content = all_content.get(pageName, {}).copy()
		content['__all__'] = all_content

		template = env.get_template(pageFile)

		if 'multipage' in content:
			multiPage = True
			# Might want to pop off the pages and combine it with contents each time..
			# but not today
			pages = content[content['multipage']['pages']]
			pageKey = content['multipage']['page_key']

			content = sorted(pages, key=lambda pg: pg[pageKey])
		else:
			content = [content]

		for pgContent in content:

			rendered = template.render(**pgContent)

			if multiPage:
				key = pgContent[pageKey]
				key = key.replace("/", "_")
				name, ext = os.path.splitext(pageFile)
				destFile = os.path.join(parentDir, siteDir, name + "_" + key + ext)
			else:
				destFile = os.path.join(parentDir, siteDir, pageFile)

			try:
				with open(destFile, 'w') as fileOut:
					fileOut.write(rendered)
			except Exception, exc:
				print "Error writing: %s" % (destFile,)
				print str(exc)
				import pdb; pdb.set_trace()
				raise

if __name__ == "__main__":

	workingDir = os.path.dirname(__file__)
	generateSite(workingDir, 'templates', 'pages', 'content', 'site')
