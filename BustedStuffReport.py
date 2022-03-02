#Importing required libraries
import urllib2
import logging
import re
import datetime
from xmlrpclib import ServerProxy as Server

# Setting up logging format to set log file AND HTML report filename, time stamping ON
logfilename = "BustedStuffLogFile.log"
logging.basicConfig(filename=logfilename,filemode='w',level=logging.INFO,format='%(asctime)s %(message)s')
htmlreportname = "Busted_Stuff_Report.html"

print " "
print "############################################"
print "#                                          #"
print "#   Welcome to the Busted Stuff Report!    #"
print "#'             A robot for                 #"
print "#'    finding Errors in Confluence pages.  #"
print "#                                          #"
print "#    Let's begin scanning your pages!      #"
print "#                                          #"
print "############################################"
print " "
print "Scanning begins!"
print " "

# Setting up HTML report header and footer
# HTML header content:
header = """
<html>
<head><title>Busted Stuff Report</title></head>
<body>
<h1>Busted Stuff Report</h1>
<i>Compiled on: """

# Setting up timestamp for HTML report
datestamp = datetime.date.today().strftime("%d-%m-%y")
#timestamp = datetime.date.today().strftime("%d-%m-%y") -- for future development.

# Writing HTML header to file:
with open(htmlreportname, 'w') as f:
    f.write(header)
    f.write(datestamp)
    f.write("""</i>""")

# HTML footer content:
footer = """<br><br><b>Ending Busted Stuff testing. 
<br><br>Thanks for using the Busted Stuff Report!</b></body></html>"""

# Setting up variables for URL retrieval
# response = "A string to catch the HTML data from the URL location"
# html = "Another string to store the HTML data" 
# sessionduration = "A count of the hours and minutes the session ran for."
# linktesttotal = 0  # "A counter of the number of links tested."
# errorcount = 0  # "A counter of the number of errors found."

# List of general varables in use
# e is a variable that catches HTTP error codes that come back
response = "A string to catch the HTML data from the URL location"
html = "."
sessionduration = 0
linktesttotal = 0
errorcount = 0

# Setting up the regex strings that will be scanned on each page. 
# These are specific text strings found in Confluence errors, that show up in the source of the page. 
bustedlinkregex = re.compile("error\">&#91;")
createlinkregex = re.compile("class=\"unresolved\"")
bustedimageregex = re.compile("Unable to render embedded object")
bustedmacroregex = re.compile("Unknown macro")
bustedjiraissuesregex = re.compile("error\">jiraissues\:")
bustedloginregex = re.compile("<title>Log In")

# Setting Confluence URL, Space, username and password.
server = 'http://confluence.atlassian.com'
conf_user = 'username'
conf_pwd = 'password'
conf_space = 'SPACENAME'
with open(htmlreportname, 'a') as f:
    f.write("<br><i>Scanning URL:<b> ")
    f.write(server)
    f.write("</b> and SPACE:<b> ")
    f.write(conf_space)
    f.write("</b></i><br>")
    f.write("<br><b>The following stuff is busted.</b> ;-)<br>")

# Access the site via XML-RPC to retrieve the list of all pages in the space (once-off action)
s = Server(server + "/rpc/xmlrpc")
s = s.confluence1
token = s.login(conf_user,conf_pwd)
# this is a "dictionary" (spaceindex)
spaceindex = s.getPages(token, conf_space)

# MAIN PROGRAM LOOP

# Loop to print every url in the spaceindex
for page_summary in spaceindex:
    site_address = page_summary['url']
    #Putting in an initial log entry to show that we're trying the given URL.
    initloggystring = "Accessing", site_address
    logging.info(initloggystring)
    print "Accessing", site_address
    # PINGING FUNCTION
    # Conditional block that tries to access the URL and catches HTTP Error codes sent back.
    linktesttotal = linktesttotal + 1
    try: 
        response = urllib2.urlopen(site_address)
        html = response.read()
    #BEGIN HTTP error finder block
    except urllib2.HTTPError, e:
    # e.code is just the numerical HTTP error code from the server. i.e. 404
        print "Error", e.code, "was detected."
	with open(htmlreportname, 'a') as f:
	    f.write('For page:')
	    f.write('<a href=\"')
	    f.write(site_address)
	    f.write('\" </a>')
            f.write("Error", e.code, "was detected.")
        errorcode = e.code
        errorloggystring = 'Error', errorcode, 'from', site_address
        logging.info(errorloggystring)
        errorcount = errorcount + 1
    # e.read is the HTML source of the 404 page. Line below prints that to console.
        print e.read() 
    #END HTTP error finder block
    # OPTIONAL -- spit the retrieved HTML into the console window or feed it into the log file
    #print html
    #logging.info(html)
    # REGEX FUNCTION
    # These actions process the HTML retrieved and searches for the Confluence Error CSS.
    print "Testing for signs of errors..."
    # Search for Failed Login Error 
    print "Testing for failed login."
    errormatch = bustedloginregex.search(html)
    if errormatch: # This shows a list of the characters that matched.
        print 'LOGIN ERROR FOUND: ', errormatch.group(), 'SKIPPING THIS FILE.'
        errorloggystring = 'LOGIN ERROR, SKIPPING THIS FILE', errormatch.group(), 'found.'
        logging.info(errorloggystring)
	with open(htmlreportname, 'a') as f:
            f.write('<br>For page:')
	    f.write('<a href=\"')
	    f.write(site_address)
	    f.write("\" </a>")
            f.write('<br>Login error found: ')
	    f.write(errormatch.group())
	    f.write(' was detected. Skipping this file.')
        errorcount = errorcount + 1
	#break
    else:
        print 'Passed login test.'
        errorloggystring = 'Passed login test.'
        logging.info(errorloggystring)
    # Search for Broken Red Link Errors (internal Confluence links)
    print "Testing for broken links."
    errormatch = bustedlinkregex.search(html)
    if errormatch: # This shows a list of the characters that matched.
        print 'Broken internal link found: ', errormatch.group()
        errorloggystring = 'Sign of Error: Broken Internal Link', errormatch.group(), 'found.'
        logging.info(errorloggystring)
	with open(htmlreportname, 'a') as f:
	    f.write("<br>For page: ") 
	    f.write("<a href=\"")
	    f.write(site_address)
	    f.write('\">')
	    f.write(site_address)
	    f.write('</a>')
            f.write(' a broken internal link was found.')
        errorcount = errorcount + 1
    else:
        print 'Passed broken links test.'
        errorloggystring = 'Passed broken links test.'
        logging.info(errorloggystring)
    # Search for Unresolved Link or CreateLink Errors (internal Confluence links)
    print "Testing for grey unresolved or red create links."
    errormatch = createlinkregex.search(html)
    if errormatch: # This shows a list of the characters that matched.
        print 'Grey unresolved or red create link found: ', errormatch.group()
        errorloggystring = 'Sign of Error: Grey Unresolved or Red Create Link', errormatch.group(), 'found.'
        logging.info(errorloggystring)
	with open(htmlreportname, 'a') as f:
	    f.write("<br>For page: ") 
	    f.write("<a href=\"")
	    f.write(site_address)
	    f.write('\">')
	    f.write(site_address)
	    f.write('</a>')
            f.write(' a grey unresolved or red create link was found.')
        errorcount = errorcount + 1
    else:
        print 'Passed create links test.'
        errorloggystring = 'Passed unresolved links / create links test.'
        logging.info(errorloggystring)    
        # Search for Broken Graphics Errors
    print "Testing for broken graphics."
    errormatch = bustedimageregex.search(html)
    if errormatch: # This shows a list of the characters that matched.
        print 'Broken graphic found: ', errormatch.group()
        errorloggystring = 'Sign of Error: Broken Graphic', errormatch.group(), 'found.'
        logging.info(errorloggystring)
	with open(htmlreportname, 'a') as f:
	    f.write("<br>For page: ") 
	    f.write("<a href=\"")
	    f.write(site_address)
	    f.write('\">')
	    f.write(site_address)
	    f.write('</a>')
            f.write(' a broken graphic was found.')
        errorcount = errorcount + 1
    else:
        print 'Passed broken graphics test.'
        errorloggystring = 'Passed broken graphics test.'
        logging.info(errorloggystring)
    # Search for Uninstalled Macro Errors
    print "Testing for uninstalled macros."
    errormatch = bustedmacroregex.search(html)
    if errormatch: # This shows a list of the characters that matched.
        print 'Unknown macro found: ', errormatch.group()
        errorloggystring = 'Sign of Error: Unknown Macro', errormatch.group(), 'found.'
        logging.info(errorloggystring)
	with open(htmlreportname, 'a') as f:
	    f.write("<br>For page: ") 
	    f.write("<a href=\"")
	    f.write(site_address)
	    f.write('\">')
	    f.write(site_address)
	    f.write('</a>')
            f.write(' an uninstalled macro reference was found.')
        errorcount = errorcount + 1
    else:
        print 'Passed unknown macro test.'
        errorloggystring = 'Passed unknown macro test.'
        logging.info(errorloggystring)
    # Search for JIRA Issues Macro Errors
    print "Testing for JIRA Issues Macro errors."
    errormatch = bustedjiraissuesregex.search(html)
    if errormatch: # This shows a list of the characters that matched.
        print 'JIRA Issues Macro Error found: ', errormatch.group()
        errorloggystring = 'Sign of Error: JIRA Issues Macro', errormatch.group(), 'found.'
        logging.info(errorloggystring)
	with open(htmlreportname, 'a') as f:
	    f.write("<br>For page: ") 
	    f.write("<a href=\"")
	    f.write(site_address)
	    f.write('\">')
	    f.write(site_address)
	    f.write('</a>')
            f.write(' a JIRA Issues Macro error was found.')
        errorcount = errorcount + 1
    else:
        print 'Passed JIRA Issues Macro test.'
        errorloggystring = 'Passed JIRA Issues Macro test.'
        logging.info(errorloggystring)
    # WINDUP FUNCTION 
    # This records the outcome of the ping to the log, if it seemed succesful.
    if html == ".": winduploggystring = "Page content was not retrieved for", site_address
    if html != ".": winduploggystring = "Actions completed on", site_address  
    logging.info(winduploggystring)
    print "Actions completed on", site_address
    html = "."

# (end FOR MAIN PROGRAM)

# This sends summary information to the console and seals off entries in the log file.

print " "
print "Ending Busted Stuff testing. Thanks for using the Busted Stuff Report!\n"
scansummary = linktesttotal, "link(s) were tested.", errorcount, "error(s) were found."
print linktesttotal, "link(s) were tested.", errorcount, "error(s) were found."
print "Busted Stuff was recorded in the HTML report:", htmlreportname
print "And in the logfile:", logfilename
summarytotal = (linktesttotal, "link(s) were tested.", errorcount, "error(s) were found.")
#errortotal = " ", errorcount, " "

#if errorcount < 1
#    scansummary = "Incredibly, no errors were found!"

with open(htmlreportname, 'a') as f:
    f.write("<br><i>If there's no links above, then no errors were found! See the .log file for a detailed record of the scan.")
    f.write(footer)
    #f.write(scansummary)
    #f.write(summarytotal)
    #f.write("link(s) were tested and")
    #f.write(errortotal)
    #f.write("error(s) were found.")
