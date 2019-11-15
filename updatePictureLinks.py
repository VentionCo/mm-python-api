from bs4 import BeautifulSoup

inputFileName = "README-mdto.html"

ventionCMSHtml = open("VentionCMS.html", 'r')
ventionCMS = BeautifulSoup(ventionCMSHtml, 'html.parser')
ventionCMSHtml.close()

techDocHtml = open(inputFileName, 'r')
techDoc = BeautifulSoup(techDocHtml, 'html.parser')
techDocHtml.close()

for techDocImage in techDoc.find_all('img'):
    
    #find the image tag in the tech docc
    techDocSearchKey = techDocImage['src']
    techDocSearchKey = techDocSearchKey.split("/")[-1]

    #find the amazon Link from the downloaded CMS webpage
    try:
        amazonUrl = ventionCMS.find('p', text=techDocSearchKey)
        amazonUrl = amazonUrl.parent.find('button')['data-link']
        amazonUrl = str(amazonUrl)
        techDocImage['src'] = amazonUrl
    except AttributeError:
        print("could not auto update link for" + techDocSearchKey)


outputFileName = inputFileName[:-5] + "-updatedPicLinks.html"
techDocHtml = open("outputFileName", 'wb+')
techDocHtml.write(techDoc.prettify("utf-8"))
techDocHtml.close()

print("saved output to " + outputFileName)


