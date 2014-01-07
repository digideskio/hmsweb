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
import os

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

def generateSite(parentDir, templateDir, pagesDir, siteDir):
	""" Generate the site
	"""
	from jinja2 import Environment, FileSystemLoader
	loader = FileSystemLoader(['templates', 'pages'])
	env = Environment(loader=loader)

	pages = getPages(parentDir, pagesDir)

	for page in pages:
		pageFile = os.path.basename(page)
		template = env.get_template(pageFile)
		pageContent = template.render()

		try:
			destFile = os.path.join(parentDir, siteDir, pageFile)
			with open(destFile, 'w') as fileOut:
				fileOut.write(pageContent)
		except:
			print "Error writing: %s" % (destFile,)
			raise

if __name__ == "__main__":

	workingDir = os.path.dirname(__file__)
	generateSite(workingDir, 'templates', 'pages', 'site')
