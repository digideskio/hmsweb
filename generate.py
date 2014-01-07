#!/usr/bin/env python
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
import yaml

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
