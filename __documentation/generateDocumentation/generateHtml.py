#!C:\Python27\py2.exe
import os
import sys
from typing import Dict
from mako.template import Template
import pdoc
import yaml
import pygments as pig
from pygments.formatters import HtmlFormatter

path_cur_dir = os.path.dirname(__file__)
path_to_documentation = os.path.dirname(path_cur_dir)
path_to_mm_python_api = os.path.dirname(path_to_documentation)
print(path_to_mm_python_api)
   
class MyFunction:
    '''
    parses function docstring data into attributes and methods which are then used by the html templates
    '''
    def _get_docstring_param(self, paramName):
        try:
            return self.docstringObj[paramName]
        except KeyError:
            return None
    
    def __init__(self, func):
        '''initialize the object from docstring, including example code mapping and source code mapping'''
        self.docstringObj = self.getDocStringObject(func.docstring)
        self.name= func.name
        self.desc = self.getValue('desc')
        self.functionType = self.getValue('functionType')
        self.parameters = []
        self.parametersExist = False
        self.className = "mm"
        self.sourceCode = func.source
        self.note = None
        self.noteExists = False
        self.V1_exampleCodePath=None
        self.V1_exampleCodeExists=False        
        self.V2_exampleCodePath=None
        self.V2_exampleCodeExists=False
        

        #sets up the source code html
        self.sourceCodeHtml = self.getSourceCode()

        self.note= self._get_docstring_param("note")
        self.noteExists = (self.note != None)
        self.returnValue = self._get_docstring_param("returnValue")
         
        self.parameterObj = self._get_docstring_param("params")
        self.parametersExist = (self.parameterObj != None)
            
        # Example Code parsing
        self.exampleCodePath =self._get_docstring_param('exampleCodePath')
        if self.exampleCodePath != None:
            V1_exampleCodeFullPath = os.path.join(path_to_mm_python_api, "examples", "MachineMotionV1", self.exampleCodePath)
            self.V1_exampleCodeHtml = self.getExampleCode(V1_exampleCodeFullPath)
            self.V1_exampleCodeExists = (self.V1_exampleCodeHtml is not None) 
        
            V2_exampleCodeFullPath = os.path.join(path_to_mm_python_api,"examples", "MachineMotionV2", self.exampleCodePath)
            self.V2_exampleCodeHtml = self.getExampleCode(V2_exampleCodeFullPath)
            self.V2_exampleCodeExists = (self.V2_exampleCodeHtml is not None)
        else:
            self.exampleCodeExists = False



        #Parameter parsing
        if self.parametersExist:
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
   
    def getValue(self, paramName):
        try:
            return self.docstringObj[paramName]
        except KeyError:
            return 'No value given for ' + paramName
    
    def addParameter(self, param):
        self.parameters.append(param)

    def listParameters(self):
        if not self.parametersExist:
            return ''

        paramStr = ''
        params = [param for param in self.parameters[::-1]]
        for idx, p in enumerate(params):
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
            print("APPLICATION ERROR: " + self.name + " has an incorrectly formatted Example code path")
            print("\t\t Could not locate path:\t" + exampleCodePath)
            return None


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

def get_functions_from_module(_module, _instance):
    print("-"*20+"\nParsing functions from " + _module.__name__)
    mmDocModule = pdoc.Module(_module)
    mmObject = _instance
    mmDocClass = pdoc.Class(name = "MachineMotion", module = mmDocModule, class_obj= mmObject)

    moduleFunctions = []
    for func in mmDocClass.doc:
        
        if func == "__init__":#skip the __init__ function
            continue
        
        #We only want to document a function if it has a docstring
        if mmDocClass.doc[func].docstring:
            newFunction = MyFunction(func=mmDocClass.doc[func])
        else:
            continue
        moduleFunctions.append(newFunction)
    
    # We sort this list so the final html shows functions in alphabetical order
    moduleFunctions = sorted(moduleFunctions, key=lambda k: k.name) 
    print("found " + str(len(moduleFunctions)) + " functions to document\n"+"-"*20+"\n\n")
    return moduleFunctions

def generate_html(module_functions, output_file="documentation.html"):
    print("-"*20+"\nloading functions into file " + output_file)

    functionTemplate = Template(filename=os.path.join(path_cur_dir, "function.mako"))
    indexTemplate = Template(filename=os.path.join(path_cur_dir, "index.mako"))


    # Use the templates to functions html and append to 'functionHtml'
    functionHtml = ''
    for apiFunction in module_functions:
        functionHtml += (functionTemplate.render(func = apiFunction))

    savePath = os.path.join(path_cur_dir,output_file) 
    # Save the output html in the modules location

    # deletes and overrides the previous html file if it exists, otherwise it just creates it
    try:
        f= open(savePath,"w")
    except AttributeError:
        os.remove(savePath)
        f= open(savePath,"w+")
    finally:
        f.write(indexTemplate.render(content = functionHtml))
        f.close()
    print("done!\n" + "-"*20+"\n")

if __name__ == '__main__':
    path_cur_dir = os.path.dirname(__file__)
    print(path_cur_dir)
    path_to_documentation = os.path.dirname(path_cur_dir)
    print(path_to_documentation)
    path_to_mm_python_api = os.path.dirname(path_to_documentation)
    print(path_to_mm_python_api)
    sys.path.append(path_to_mm_python_api)
    print(sys.path)
    import MachineMotion as mm_module
 

    mm_instance = mm_module.MachineMotion("192.168.137.5")
    functions = get_functions_from_module(_module = mm_module, _instance = mm_instance)

    filename = "documentation.html"
    generate_html(functions, output_file=filename)
    