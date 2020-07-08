#!C:\Python27\py2.exe
import os
import sys
import importlib
import webbrowser
from shutil import copyfile
from typing import Dict
import webbrowser
from mako.template import Template
import pdoc
import yaml
import pygments as pig
from pygments.formatters import HtmlFormatter



    
class MyFunction:

    def __init__(self, func):

        self.docstringObj = self.getDocStringObject(func.docstring)
        self.name= func.name
        self.desc = self.getValue(self.docstringObj, 'desc')
        self.parameters = []
        self.parametersExist = False
        self.className = "mm"
        self.sourceCode = func.source
        self.note = None
        self.noteExists = False
        

        #sets up the source code html
        self.sourceCodeHtml = self.getSourceCode()

        try:
            self.note = self.docstringObj["note"]
            self.noteExists = True
        except KeyError:
            pass

        try: 
            self.returnValue = self.docstringObj["returnValue"]
        except KeyError:
            self.returnValue = None
            
        # Sets up the example code path if it exists
        self.exampleCodePath = self.getValue(self.docstringObj, 'exampleCodePath')
        if(self.exampleCodePath) != "No value given for exampleCodePath":

            exampleCodeFullPath = os.path.join("C:\\Python36\\Scripts\\autodocgen\\mm-python-api\\examples",self.exampleCodePath)


            self.exampleCodeExists = True
            self.exampleCodeHtml = self.getExampleCode(exampleCodeFullPath)
        else:
            self.exampleCodeExists = False

        # Changes value of parameters to keyword None if no parameters exist
        try:
            self.parameterObj = self.docstringObj["params"]
            self.parametersExist = True
        except KeyError:
            self.parameterObj = None
            self.parameters = False
            return

        #Parameter only intializations from here on down!
        for p in self.parameterObj:
            try:
                newParam = Parameter(paramName = p, paramDict = self.parameterObj[p])
            except ValueError:
                if not hasattr(self.parameterObj[p], "desc"):
                    print("APPLICATION ERROR: Parameter " + p + " of function " + self.name + " has no description" )
                if not hasattr(self.parameterObj[p], "type"):
                    print("APPLICATION ERROR: Parameter " + p + " of function " + self.name + " has no type" )
                raise ValueError
            self.addParameter(newParam)


    def __tostr__(self):
        return self.name
   
   
    def getValue(self, paramObj, paramName):
        try:
            return paramObj[paramName]
        except KeyError:
            return 'No value given for ' + paramName
    
    def addParameter(self, param):
        self.parameters.append(param)

    def listParameters(self):
        if not self.parametersExist:
            return ''

        paramStr = ''

        for idx, p in enumerate(self.parameters):
            paramStr += p.paramName
            if(idx < len(self.parameters)-1):
                paramStr += ", "
        
        return paramStr

    def getExampleCode(self, exampleCodePath):

        def getCode(path):
            codeFile = open(path, 'r')
            exampleCode = codeFile.read()
            codeFile.close()
            pyLexer = pig.lexers.python.Python3Lexer()
            return  pig.highlight(exampleCode, pyLexer, HtmlFormatter())

        try:
            return getCode(exampleCodePath)
        except IOError:
            print("APPLICATION ERROR: " + self.name + " has an incorrectly formatted Example code path. Please check.")


    def getSourceCode(self):
        pyLexer = pig.lexers.python.Python3Lexer()
        
        docstringIndex = []
        for i,line in enumerate(self.sourceCode):
            if("'''\n" in line):
                docstringIndex.append(i)

        del self.sourceCode[docstringIndex[0]:docstringIndex[1]+1]
        self.sourceCode = "".join(self.sourceCode)
        return pig.highlight(self.sourceCode, pyLexer, HtmlFormatter())

    def getDocStringObject(self, docstring):
        docObject = yaml.safe_load(docstring)
        if hasattr(docObject, "params"):
            try:
                docObject["params"]["desc"]
                docObject["params"]["type"]
            except KeyError:
                print("Error processing parameters for function" + self.name + ", please ensure each docstring parameter has both 'desc' and 'type'")
                raise KeyError
        return docObject

        




class Parameter():
    def __init__(self, paramName, paramDict):
        self.paramName = paramName
        self.paramDict = dict(paramDict)
        self.typeName = self.getValue("type")
        self.desc = self.getValue("desc")

        try:
            self.defaultValue = self.paramDict["defaultValue"]
            self.optional = True
        except KeyError:
            self.optional = False

    def getValue(self, paramName):
        try:
            return self.paramDict[paramName]
        except KeyError:
            return 'No value given for' + paramName

def templateCallback(data):
   pass

def generateHtml(fileName, module, bypassClass):
    mmDocModule = pdoc.Module(module)
    mmObject = bypassClass
    mmDocClass = pdoc.Class(name = "MachineMotion", module = mmDocModule, class_obj= mmObject)
    moduleLocation = os.path.dirname(module.__file__)
    thisScriptLocation = os.path.dirname(os.path.abspath(__file__))
    
    moduleFunctions = []
    for func in mmDocClass.doc:
        
        if func == "__init__":#skip the __init__ function
            continue
        
        #We only want to document a function if it has a docstring
        if mmDocClass.doc[func].docstring:
            newFunction = MyFunction(func=mmDocClass.doc[func])
            # newFunction = MyFunction(funcName = func, docstring = func_docstring, sourceCode= func_sourceCode)
        else:
            continue
        moduleFunctions.append(newFunction)
    
    # We sort this list so the final html shows functions in alphabetical order
    moduleFunctions = sorted(moduleFunctions, key=lambda k: k.name) 
    

    # Load Templates to turn data into html
    tocPath = os.path.join(thisScriptLocation, "pdocTemplates", "toc.mako")
    tocTemplate = Template(filename= tocPath)
    functionPath = os.path.join(thisScriptLocation, "pdocTemplates", "function.mako")
    functionTemplate = Template(filename=functionPath)
    introPath = os.path.join(thisScriptLocation, "pdocTemplates", "apiIntro.mako")
    introTemplate = Template(filename = introPath)

    # Use the templates to functions html and append to 'functionHtml'
    functionHtml = ''
    for apiFunction in moduleFunctions:
        try:
            functionHtml += (functionTemplate.render(func = apiFunction))
        except Exception as e:
            print("APPLICATION ERROR: problem with " + apiFunction.name)
            raise e

    # Use and render the other templates
    tocHtml = tocTemplate.render(functions = moduleFunctions)
    apiIntroHtml = introTemplate.render()

    # Save the output html in the modules location
    if not os.path.exists(thisScriptLocation + "/build/"):
        os.makedirs(thisScriptLocation + "/build/")

    # deletes and overrides the previous html file if it exists, otherwise it just creates it
    print("Saving output to %s/build/%s" % (thisScriptLocation, fileName))
    try:
        f= open(thisScriptLocation + "/build/" + fileName,"w")
    except AttributeError:
        os.remove(fileName)
        f= open(thisScriptLocation + "/build/" + fileName,"w+")
    


    # if uploadToCMS then we use CMSIndex.mako instead of index.mako, and we collapse everything into a single html doc
    # if  "--uploadToCMS" in sys.argv:
    
    uploadTOCMS = True
    if(uploadTOCMS):
        indexTemplate = Template(filename= os.path.join(thisScriptLocation,"pdocTemplates", "CMSIndex.mako"))
        
        cssNative = open(os.path.join(thisScriptLocation, "build","native.css"), "r")
        cssNativeCode = cssNative.read()
        cssNative.close()

        cssStyles = open(os.path.join(thisScriptLocation,"build", "styles.css"), "r")
        cssStylesCode = cssStyles.read()
        cssStyles.close()

        f.write(indexTemplate.render(
            content = functionHtml, 
            toc = tocHtml,  
            apiIntro= apiIntroHtml, 
            cssStyles = cssStylesCode, 
            cssNative = cssNativeCode
        ))
        f.close()

    else:
        indexTemplate = Template(filename= thisScriptLocation + '/pdocTemplates/index.mako')
        f.write(indexTemplate.render(content = functionHtml, toc = tocHtml))
        f.close()
        copyfile(thisScriptLocation + "/build/native.css", moduleLocation + "/build/" + "native.css")
        copyfile(thisScriptLocation + "/build/styles.css", moduleLocation + "/build/" + "styles.css")
        webbrowser.open_new(moduleLocation + "/build/" + outputName)
  
#overrides the actual initi function 


if __name__ == '__main__':


    pathToMachineMotion = "C:\Python36\Scripts\\autodocgen\mm-python-api"
    sys.path.insert(1,pathToMachineMotion)
    import MachineMotion as mm

    class bypassClassInitialization(mm.MachineMotion):
        def __init__(self):
            print("APPLICATION MESSAGE: Generating HTML")
            pass

 
    outputName = "documentation.html"
    generateHtml(fileName = outputName, module = mm, bypassClass = bypassClassInitialization)

