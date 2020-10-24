
import os
import sys
import glob
import fnmatch

import json

from mako.template import Template

class Utils():
    class String():
        def ToLowerCase(string):
            return string.lower()

        def ToPascalCase(string):
            return Utils.String.RemoveSpaces(string.title())

        def RemoveSpaces(string):
            return ''.join(x for x in string if not x.isspace())
        
    class Ext():
        def MatchesExtensions(name,extensions=["*"]):
            for pattern in extensions:
                if fnmatch.fnmatch(name, pattern):
                    return True
            return False

    class Path():
        def RecurseFilenames(folder, extensions=['*']):
            for folder, subs, files in os.walk(folder):
                files = filter(lambda file: Utils.Ext.MatchesExtensions( extensions ), files)
                for filename in files:
                    yield folder, filename
        
class FileData():
    def __init__(self):
        self.data = {}
        self.filename = 'file.dat'
        self.folder = ''

    def SetFolder(self, folder):
        self.folder = folder

    def GetFolder(self):
        return self.folder

    def GetFilename(self):
        return self.filename
        
    def Save(self):
        folder = self.GetFolder()
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(os.path.join(folder, self.GetFilename()), 'w') as f:
            json.dump(self.data, f)

    def Load(self, overwrite = False):
        folder = self.GetFolder()
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.GetFilename())

        if not os.path.exists(filename):
            return

        with open(filename, 'r') as f:
            json_data = json.load(f)

            if overwrite:
                self.data = json_data
            else:
                self.data.update(json_data)

class UHG():
    settings = None
    templates = {}

    def GetTemplate(templateType):
        return UHG.templates[UHG.TemplateDef.NormalizeType(templateType)]

    class TemplateDef():
        def NormalizeName(name):
            return Utils.String.ToPascalCase(name)

        def NormalizeType(type):
            return Utils.String.ToPascalCase(type)

        def NormalizeNamespace(namespace):
            return Utils.String.RemoveSpaces(namespace)

        def NormalizeFilename(filename):
            return Utils.String.ToLowerCase(filename)

    class Settings():
        def __init__(self):
            self.settings = FileData()
            self.settings.filename = "UHG.settings.json"

            # Default values
            self.SetInputPath("templates")
            self.SetOutputPath("generated")
            self.SetTemplateExt(".template.json")

            # Load custom values (overwrite if necessary)
            self.settings.Load()

        def GetInputPath(self):
            return self.settings.data["input"]

        def GetOutputPath(self):
            return self.settings.data["output"]

        def GetTemplateExt(self):
            return self.settings.data["templateExt"]

        def SetInputPath(self, value):
            self.settings.data["input"] = value

        def SetOutputPath(self, value):
            self.settings.data["output"] = value

        def SetTemplateExt(self, value):
            self.settings.data["templateExt"] = value

UHG.settings = UHG.Settings()
UHG.templates["Interface"] = '''
UINTERFACE()
class U${name}Interface {
% for func in functions:
    ${func};
% endfor
};

class I${name}Interface {
};

// using ${namespace}::I${name} = I${name}Interface;
''';

class TemplateData(FileData):
    def __init__(self):
        super().__init__()

    def GetFunctionsArray(self):
        self.data["functions"] = [] if self.data["functions"] is None else self.data["functions"]
        return self.data["functions"]

    def GetName(self):
        return UHG.TemplateDef.NormalizeName(self.data["name"])

    def GetType(self):
        return UHG.TemplateDef.NormalizeType(self.data["type"])
    
    def GetNamespace(self):
        return UHG.TemplateDef.NormalizeNamespace(self.data["namespace"])

    def GetFilename(self):
        return UHG.TemplateDef.NormalizeFilename(self.GetName()+UHG.settings.GetTemplateExt())

    def SetName(self, name):
        self.data["name"] = name

    def SetType(self, type):
        self.data["type"] = type

    def SetNamespace(self, namespace):
        self.data["namespace"] = namespace

    def GetFunction(self, index):
        return self.GetFunctionsArray()[index]

    def AddFunction(self, func_definition):
        self.GetFunctionsArray().push(func_definition)

    def RemoveFunction(self, func_definition):
        self.GetFunctionsArray().remove(func_definition)

    def BuildData(self):
        data = {}
        data["name"] = self.GetName()
        data["type"] = self.GetType()
        data["namespace"] = self.GetNamespace()
        data["functions"] = self.GetFunctionsArray()
        return data

    def Render(self):
        return Template(UHG.GetTemplate(self.data["type"])).render(**self.BuildData())

class HeaderFile():
    def __init__(self):
        self.template_data = TemplateData()

    def Template(self):
        return self.template_data
        
    def GetName(self):
        return self.template_data.GetName()

    def GetFilename(self):
        return self.GetName()+'.h'

    def GenerateContent(self):
        return self.template_data.Render()

    def GenerateAndSave(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(os.path.join(folder, self.GetFilename()), "w") as text_file:
            text_file.write(self.GenerateContent())
    
if __name__== "__main__":
    folder_in = UHG.settings.GetInputPath()
    folder_out = UHG.settings.GetOutputPath()
    template_ext = UHG.settings.GetTemplateExt()
    
    # For all files you find in a certain folder (and subfolders recursively)
    # consider each file and generate, from it as a template, the corresponding
    # generated header - by also mantaining the tree structure

    for folder_src, template_filename in Utils.Path.RecurseFilenames(folder_in, '*'+template_ext):
        template_name = template_filename[:template_filename.rfind(template_ext)]
        relative_folder = folder_src[folder_src.find(folder_in)+len(folder_in):].lstrip('\\').lstrip('/')
        folder_dest = os.path.join(folder_out, relative_folder)

        header = HeaderFile()
        
        header.template_data.SetFolder(folder_src)
        header.template_data.SetName(template_name)
        header.template_data.Load()

        header.GenerateAndSave(folder_dest)
            