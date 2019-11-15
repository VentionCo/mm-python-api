from bs4 import BeautifulSoup
import os


techDocHtml = open("temp/README-newImgLink.html", 'r')
techDoc = BeautifulSoup(techDocHtml, 'html.parser')
techDocHtml.close()

for table in techDoc.find_all('table'):
    table['class'] = "table"
    table['style'] = "width:95%; margin: auto"
    div = techDoc.new_tag('div')
    div['style'] = "border: 2px solid #E9ECEF;padding: 5px;width:80%; margin: auto; font-size:90%"
    table.wrap(div)

for row in techDoc.find_all('tr'):
    row['style'] = 'line-height: 120%'

for anchor in techDoc.find_all('a'):
    anchor['class'] = "anchor"

for code in techDoc.find_all('code'):
    code['style'] = "font-size: 12px"

for image in techDoc.find_all('img'):
    image['style'] = "margin:20px; width: 80%; border: 2px solid rgb(233, 236, 239); outline: none; "

for header in techDoc.find_all('h3'):
    blankP = techDoc.new_tag('p')
    blankP['text'] = " "
    header.insert_before(blankP)
    header.insert_before(blankP)

techDoc = techDoc.find('article')

saveFileName = "README-output.html"

if os.path.exists(saveFileName):
    os.remove(saveFileName)


techDocHtml = open(saveFileName, 'wb+')
techDocHtml.write(techDoc.prettify("utf-8"))
techDocHtml.close()

print("output saved to " + saveFileName)