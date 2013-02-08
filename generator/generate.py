#!/usr/bin/env python


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
	pagesDir = os.path.join(parentDir, pagesDir)
	for page in os.listdir(pagesDir):

		# Read the page	
		pagePath = os.path.join(pagesDir, page)
		with open(pagePath) as pageFile:
			pages[page] = pageFile.read()

	return pages

def generateSite(parentDir, templateDir, pagesDir, siteDir):
	""" Generate the site
	"""
	# Common parts
	header = readTemplate(parentDir, templateDir, 'header.html')
	footer = readTemplate(parentDir, templateDir, 'footer.html')

	# Pages
	pages = getPages(parentDir, 'pages')

	for page, pageContent in pages.iteritems():
		destFile = os.path.join(parentDir, siteDir, page)

		with open(destFile, 'w') as fileOut:
			fileOut.write(header)
			fileOut.write(pageContent)
			fileOut.write(footer)


if __name__ == "__main__":

	workingDir = os.path.dirname(__file__)
	generateSite(workingDir, 'templates', 'pages', 'site')
