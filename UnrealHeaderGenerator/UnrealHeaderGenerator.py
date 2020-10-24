
import os
import sys
import pkgutil
import glob
import fnmatch

import json

from mako.template import Template

class Utils():
	class Object():
		def CheckMember(obj, member):
			return member in obj and member is not None

		def AssignIfInvalid(obj, member, default):
			obj[member] = obj[member] if Utils.Object.CheckMember(obj, member) else default

	class String():
		def CapitalFirst(string):
			return string[:1].upper() + string[1:] # string.title()

		def ToLowerCase(string):
			return string.lower()

		def ToPascalCase(string):
			return Utils.String.RemoveSpaces(Utils.String.CapitalFirst(string))

		def RemoveSpaces(string):
			return ''.join(x for x in string if not x.isspace())
		
	class Ext():
		def MatchesExtensions(name,extensions=["*"]):
			for pattern in extensions:
				if fnmatch.fnmatch(name, pattern):
					return True
			return False

		def Split(filename):
			basename = filename
			ext = None
			extFull = ""
			while ext is not "":
				basename, ext = os.path.splitext(basename)
				extFull = ext + extFull
			return basename, extFull


	class Path():
		def RecurseFilenames(folder, extensions=['*']):
			for folder, subs, files in os.walk(folder):
				files = filter(lambda file: Utils.Ext.MatchesExtensions( extensions ), files)
				for filename in files:
					yield folder, filename

		def LoadAllModulesFromDir(dirname, import_globally = True):
			for importer, package_name, _ in pkgutil.iter_modules([dirname]):
				full_package_name = '%s.%s' % (dirname, package_name)
				full_package_name = full_package_name.replace('/', '.')
				if full_package_name not in sys.modules:
					module = importer.find_module(package_name)
					loaded_module = module.load_module(package_name)
					if import_globally:
						sys.modules[full_package_name] = loaded_module
						# __all__[package_name] = loaded_module
					yield loaded_module
		
class FileFactory():
	MapOfFileClasses = {}

	def Generate(filename):
		
		basename, ext = Utils.Ext.Split(filename)

		fileKey = ext if ext in FileFactory.MapOfFileClasses else None
		fileClass = FileFactory.MapOfFileClasses[fileKey]

		file = fileClass()
		file.file_data.SetFilename(filename)

		return file
	
class FileData():
	def __init__(self):
		self.data = None
		self.filename = 'file.dat'
		self.folder = ''

	def SetFolder(self, folder):
		self.folder = folder

	def SetFilename(self, filename):
		self.filename = filename

	def GetFolder(self):
		return self.folder

	def GetFilename(self):
		return self.filename
	
	def GetName(self):
		return Utils.Ext.Split(self.filename)[0]

	def GetExtension(self):
		return Utils.Ext.Split(self.filename)[1]
		
	def Save(self):
		folder = self.GetFolder()
		if not os.path.exists(folder):
			os.makedirs(folder)
		with open(os.path.join(folder, self.GetFilename()), 'w') as f:
			f.write(self.data)

	def Load(self, overwrite = False):
		folder = self.GetFolder()
		if folder and not os.path.exists(folder):
			os.makedirs(folder)
		filename = os.path.join(folder, self.GetFilename())

		if not os.path.exists(filename):
			return

		with open(filename, 'r') as f:
			self.data = f.read()

class JsonFileData(FileData):
	def __init__(self):
		super().__init__()

		self.data = {}
		
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
	DEFAULT_RECURSIONS = 10

	settings = None
	templates = {}
	classNames = {}

	TemplateInfo = {}
	TypeAliases = {}

	def ExtendData(data):
		data["TypeAlias"] = UHG.TypeAliases
		data["TemplateInfo"] = UHG.TemplateInfo
		data["Settings"] = UHG.settings
		data["Templates"] = UHG.templates
		return data

	def RecurseFiles(folder_in = None, folder_out = None):
		folder_in = UHG.settings.GetInputClassesPath() if folder_in is None else folder_in
		folder_out = UHG.settings.GetOutputClassesPath() if folder_out is None else folder_out

		for folder_src, filename in Utils.Path.RecurseFilenames(folder_in, '*'):
			relative_folder = folder_src[folder_src.find(folder_in)+len(folder_in):].lstrip('\\').lstrip('/')
			folder_dest = os.path.join(folder_out, relative_folder)

			file_object = FileFactory.Generate(filename)
			
			file_object.file_data.SetFolder(folder_src)
			file_object.file_data.Load()

			class CustomData():
				FolderSrc = folder_src
				FolderDest = folder_dest
				RelativeFolder = relative_folder
				File = file_object

			yield CustomData

	def RecurseUHGClasses(folder_in = None, folder_out = None, uhgclass_ext = None):
		folder_in = UHG.settings.GetInputClassesPath() if folder_in is None else folder_in
		folder_out = UHG.settings.GetOutputClassesPath() if folder_out is None else folder_out
		uhgclass_ext = UHG.settings.GetClassExt() if uhgclass_ext is None else uhgclass_ext

		for folder_src, uhgclass_filename in Utils.Path.RecurseFilenames(folder_in, '*'+uhgclass_ext):
			uhgclass_name = uhgclass_filename[:uhgclass_filename.rfind(uhgclass_ext)]
			relative_folder = folder_src[folder_src.find(folder_in)+len(folder_in):].lstrip('\\').lstrip('/')
			folder_dest = os.path.join(folder_out, relative_folder)

			header = HeaderFile()
			
			header.uhgclass_data.SetFolder(folder_src)
			header.uhgclass_data.SetName(uhgclass_name)
			header.uhgclass_data.Load()

			class CustomData():
				FolderSrc = folder_src
				FolderDest = folder_dest
				RelativeFolder = relative_folder
				UHGClassName = uhgclass_name
				Header = header
				UHGClass = header.uhgclass_data

			yield CustomData

	def GetTemplate(templateType):
		return UHG.templates[UHG.TemplateDef.NormalizeType(templateType)]

	def GetClassNameByTemplateType(templateType):
		return UHG.classNames[UHG.TemplateDef.NormalizeType(templateType)]

	class TemplateDef():
		def NormalizeAlias(alias):
			return alias # Utils.String.ToPascalCase(alias)

		def NormalizeName(name):
			return Utils.String.ToPascalCase(name)
		
		def NormalizeClassName(name):
			return Utils.String.ToPascalCase(name)
		
		def NormalizeModuleName(name):
			return Utils.String.ToPascalCase(name)

		def NormalizeType(type):
			return Utils.String.ToPascalCase(type)

		def NormalizeNamespace(namespace):
			return Utils.String.RemoveSpaces(namespace)

		def NormalizeFilename(filename):
			return Utils.String.ToLowerCase(filename)
		
	class Labels():
		uhgInputTemplates = 'uhgInputTemplates'
		uhgInputClasses = 'uhgInputClasses'
		uhgOutputClasses = 'uhgOutputClasses'
		uhgTemplateExt = 'uhgTemplateExt'
		uhgClassExt = 'uhgClassExt'
		uhgModuleExt = 'uhgModuleExt'

	class Settings():
		def __init__(self):
			self.settings = JsonFileData()
			self.settings.filename = "UHG/UHG.settings.json"

			# Default values
			self.SetInputTemplatesPath("UHG/UHGTemplates")
			self.SetInputClassesPath("UHG/UHGClasses")
			self.SetOutputClassesPath("UHGGeneratedClasses")
			self.SetTemplateExt(".uhgtemplate.json")
			self.SetClassExt(".uhgclass.json")
			self.SetModuleExt(".uhgmodule.json")
			self.SetAPI("UNKNOWN_API")

			# Load custom values (overwrite if necessary)
			self.settings.Load()

		def GetInputTemplatesPath(self):
			return self.settings.data[UHG.Labels.uhgInputTemplates]
		
		def GetInputClassesPath(self):
			return self.settings.data[UHG.Labels.uhgInputClasses]

		def GetOutputClassesPath(self):
			return self.settings.data[UHG.Labels.uhgOutputClasses]

		def GetTemplateExt(self):
			return self.settings.data[UHG.Labels.uhgTemplateExt]

		def GetClassExt(self):
			return self.settings.data[UHG.Labels.uhgClassExt]
		
		def GetModuleExt(self):
			return self.settings.data[UHG.Labels.uhgModuleExt]

		def GetAPI(self):
			return self.settings.data["API"]

		def SetInputTemplatesPath(self, value):
			self.settings.data[UHG.Labels.uhgInputTemplates] = value

		def SetInputClassesPath(self, value):
			self.settings.data[UHG.Labels.uhgInputClasses] = value

		def SetOutputClassesPath(self, value):
			self.settings.data[UHG.Labels.uhgOutputClasses] = value

		def SetTemplateExt(self, value):
			self.settings.data[UHG.Labels.uhgTemplateExt] = value

		def SetClassExt(self, value):
			self.settings.data[UHG.Labels.uhgClassExt] = value
			
		def SetModuleExt(self, value):
			self.settings.data[UHG.Labels.uhgModuleExt] = value

		def SetAPI(self, value):
			self.settings.data["API"] = value

class UHGAbstractTemplateData(JsonFileData):
	def __init__(self):
		super().__init__()

	def SetFilename(self, filename):
		basename, ext = Utils.Ext.Split(filename)
		if 'name' not in self.data:
			self.SetName(basename)
		super().SetFilename(filename)

	def GetMetadata(self, use_precached=False):
		Utils.Object.AssignIfInvalid(self.data, "metadata", {})
		return self.data["metadata"]

	def GetAlias(self, use_precached=False):
		if 'alias' not in self.data:
			return ''
		return UHG.TemplateDef.NormalizeAlias(self.data["alias"])

	def GetName(self, use_precached=False):
		if 'name' not in self.data:
			return ''
		return UHG.TemplateDef.NormalizeName(self.data["name"])
	
	def GetType(self, use_precached=False):
		if 'type' not in self.data:
			return ''
		return UHG.TemplateDef.NormalizeType(self.data["type"])
	
	def GetExtension(self):
		return ""

	def GetFilename(self):
		return UHG.TemplateDef.NormalizeFilename(self.GetName()+self.GetExtension())

	def SetAlias(self, alias):
		self.data["alias"] = alias

	def SetName(self, name):
		self.data["name"] = name
		
	def SetType(self, type):
		self.data["type"] = type

	def BuildData(self, use_precached=False):
		data = {}
		templateName = self.GetName(use_precached=use_precached)
		templateType = self.GetType(use_precached=use_precached)

		data["TemplateData"] = self
		data["name"] = templateName
		data["type"] = templateType
		data["metadata"] = self.GetMetadata(use_precached=use_precached)
		data = UHG.ExtendData(data)
		return data

	def Render(self, recursions = UHG.DEFAULT_RECURSIONS):
		template_content = UHG.GetTemplate(self.GetType())
		return self.RenderSomeContent(template_content, recursions)

	def RenderSomeContent(self, template_content, recursions = 1):
		built_data = self.BuildData()
		return self.RenderSomeContentWithData(template_content, built_data, recursions)

	def RenderSomeContentWithData(self, template_content, built_data, recursions = 1):
		for i in range(recursions):
			try:
				template_content = Template(template_content).render(**built_data, **UHG.TypeAliases)
			except Exception as error:
				print("Some error occurred while rendering template: \n>>>\t", error, "\n")
		return template_content

class UHGModuleTemplateData(UHGAbstractTemplateData):
	def __init__(self):
		super().__init__()
		self.SetType("Module")

	def GetExtension(self):
		return UHG.settings.GetModuleExt()
	
	def GetModuleName(self, use_precached=False):
		moduleName = ''
		templateType = self.GetType()
		if 'moduleName' in self.data:
			moduleName = UHG.TemplateDef.NormalizeModuleName(self.data["moduleName"])
		if moduleName or use_precached:
			return moduleName
		return self.GetName() # self.RenderSomeContentWithData(UHG.GetClassNameByTemplateType(templateType), self.BuildData(use_precached=True))

	def SetModuleName(self, module_name):
		self.data["moduleName"] = module_name
		
	def BuildData(self, use_precached=False):
		data = super().BuildData(use_precached=use_precached)
		moduleName = self.GetModuleName(use_precached=use_precached)

		data["UHGModule"] = self
		data["moduleName"] = moduleName
		return data

class UHGClassTemplateData(UHGAbstractTemplateData):
	def __init__(self):
		super().__init__()

	def GetFunctionsObjectArray(self, use_precached=False):
		functions = self.GetFunctionsArray(use_precached=use_precached)

		funcobjects = []
		for funcdef in functions:
			funcobj = {}

			if isinstance(funcdef, object) and not isinstance(funcdef, str):
				funcobj = funcdef
			else:
				funcobj['declaration'] = funcdef
				funcobj['metadata'] = ''
					
			if not Utils.Object.CheckMember(funcobj, "declaration") or not isinstance(funcobj['declaration'], str):
				funcobj['declaration'] = funcdef if isinstance(funcdef, str) else ''
			if not Utils.Object.CheckMember(funcobj, "metadata") or not isinstance(funcobj['metadata'], str):
				funcobj['metadata'] = ''

			funcobjects.append(funcobj)

		return funcobjects

	def GetFunctionsArray(self, use_precached=False):
		Utils.Object.AssignIfInvalid(self.data, "functions", [])
		return self.data["functions"]
	
	def GetMembersObjectArray(self, use_precached=False):
		members = self.GetMembersArray(use_precached=use_precached)

		memberobjects = []
		for memberdef in members:
			memberobj = {}

			if isinstance(memberdef, object) and not isinstance(memberdef, str):
				memberobj = memberdef
			else:
				memberobj['declaration'] = memberdef
				memberobj['metadata'] = ''
					
			if not Utils.Object.CheckMember(memberobj, "declaration") or not isinstance(memberobj['declaration'], str):
				memberobj['declaration'] = memberdef if isinstance(memberdef, str) else ''
			if not Utils.Object.CheckMember(memberobj, "metadata") or not isinstance(memberobj['metadata'], str):
				memberobj['metadata'] = ''

			memberobjects.append(memberobj)

		return memberobjects

	def GetMembersArray(self, use_precached=False):
		Utils.Object.AssignIfInvalid(self.data, "members", {})
		return self.data["members"]
	
	def GetClassName(self, use_precached=False):
		className = ''
		templateType = self.GetType()
		if 'className' in self.data:
			className = UHG.TemplateDef.NormalizeClassName(self.data["className"])
		if className or use_precached:
			return className
		return self.RenderSomeContentWithData(UHG.GetClassNameByTemplateType(templateType), self.BuildData(use_precached=True))

	def GetNamespace(self, use_precached=False):
		if 'namespace' not in self.data:
			return ''
		return UHG.TemplateDef.NormalizeNamespace(self.data["namespace"])

	def GetExtension(self):
		return UHG.settings.GetClassExt()

	def SetClassName(self, class_name):
		self.data["className"] = class_name

	def SetNamespace(self, namespace):
		self.data["namespace"] = namespace

	def GetFunction(self, index):
		return self.GetFunctionsArray()[index]

	def AddFunction(self, func_definition):
		self.GetFunctionsArray().append(func_definition)

	def RemoveFunction(self, func_definition):
		self.GetFunctionsArray().remove(func_definition)

	def BuildData(self, use_precached=False):
		data = super().BuildData(use_precached=use_precached)
		className = self.GetClassName(use_precached=use_precached)

		data["UHGClass"] = self
		data["className"] = className
		data["namespace"] = self.GetNamespace(use_precached=use_precached)
		data["functions"] = self.GetFunctionsObjectArray(use_precached=use_precached)
		data["members"] = self.GetMembersObjectArray(use_precached=use_precached)
		return data

class GenericFile():
	def __init__(self):
		self.file_data = FileData()

	def Data(self):
		return self.file_data
		
	def GetName(self):
		return self.file_data.GetName()
		
	def GetExtension(self):
		return self.file_data.GetExtension()

	def GetFilename(self):
		return self.GetName()+self.GetExtension()

	def GenerateContent(self):
		return self.file_data.data

	def GenerateAndSave(self, folder):
		if not os.path.exists(folder):
			os.makedirs(folder)
		with open(os.path.join(folder, self.GetFilename()), "w") as text_file:
			text_file.write(self.GenerateContent())
			
class HeaderFile(GenericFile):
	def __init__(self):
		self.file_data = UHGClassTemplateData()

	def Template(self):
		return self.file_data
		
	def GetName(self):
		return self.file_data.GetClassName()

	def GetExtension(self):
		return '.h'

	def GenerateContent(self):
		return self.file_data.Render()

class ModuleFile(GenericFile):
	def __init__(self):
		self.file_data = UHGModuleTemplateData()

	def Template(self):
		return self.file_data
		
	def GetName(self):
		return self.file_data.GetModuleName()
	
	def GetExtension(self):
		return '.Build.cs'

	def GenerateContent(self):
		return self.file_data.Render()
	
	def GenerateAndSave(self, folder):
		if not os.path.exists(folder):
			os.makedirs(folder)

		templateModuleHeader = UHG.GetTemplate("ModuleHeader")
		templateModuleSource = UHG.GetTemplate("ModuleSource")

		with open(os.path.join(folder, self.GetFilename()), "w") as text_file:
			text_file.write(self.GenerateContent())
			
		for template, subfolder, ext in [(templateModuleHeader, os.path.join(folder, "Source/Public"), '.h'), (templateModuleSource, os.path.join(folder, "Source/Private"), '.cpp')]:
			if not os.path.exists(subfolder):
				os.makedirs(subfolder)
			with open(os.path.join(subfolder, self.GetName()+ext), "w") as text_file:
				text_file.write(self.file_data.RenderSomeContent(template))

		# \TODO : Also generate the module .h and .cpp, other than .Build.cs only

def SetupFileClasses():
	FileFactory.MapOfFileClasses[UHG.settings.GetClassExt()] = HeaderFile
	FileFactory.MapOfFileClasses[UHG.settings.GetModuleExt()] = ModuleFile
	FileFactory.MapOfFileClasses[None] = GenericFile
	
UHG.settings = UHG.Settings()

if __name__== "__main__":

	# Setup file classes of the file factory

	SetupFileClasses()

	# Import all templates from template modules

	for module in Utils.Path.LoadAllModulesFromDir(UHG.settings.GetInputTemplatesPath()):
		print("imported module: ", module)

		if not hasattr(module, 'GetTemplateInfo'):
			continue

		templateName, templateContent, className = module.GetTemplateInfo()
		
		if className is not None:
			UHG.classNames[templateName] = className

		if templateContent is not None:
			UHG.templates[templateName] = templateContent

	# Cook all templates in local data

	for data in UHG.RecurseFiles():
		if not hasattr(data.File.file_data, "GetAlias"):
			continue

		alias = data.File.file_data.GetAlias()
		if alias is not "":
			UHG.TypeAliases[alias] = data.File.GetName()

	# For all files you find in a certain folder (and subfolders recursively)
	# consider each file and generate, from it as a template, the corresponding
	# generated header - by also mantaining the tree structure

	for data in UHG.RecurseFiles():
		data.File.GenerateAndSave(data.FolderDest)
			