
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

class UPFG():
	DEFAULT_RECURSIONS = 10

	settings = None
	templates = {}
	classNames = {}

	TemplateInfo = {}
	TypeAliases = {}

	def ExtendData(data):
		data["TypeAlias"] = UPFG.TypeAliases
		data["TemplateInfo"] = UPFG.TemplateInfo
		data["Settings"] = UPFG.settings
		data["Templates"] = UPFG.templates
		return data

	def RecurseFiles(folder_in = None, folder_out = None):
		folder_in = UPFG.settings.GetInputClassesPath() if folder_in is None else folder_in
		folder_out = UPFG.settings.GetOutputClassesPath() if folder_out is None else folder_out

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

	def RecurseUPFGClasses(folder_in = None, folder_out = None, upfgclass_ext = None):
		folder_in = UPFG.settings.GetInputClassesPath() if folder_in is None else folder_in
		folder_out = UPFG.settings.GetOutputClassesPath() if folder_out is None else folder_out
		upfgclass_ext = UPFG.settings.GetClassExt() if upfgclass_ext is None else upfgclass_ext

		for folder_src, upfgclass_filename in Utils.Path.RecurseFilenames(folder_in, '*'+upfgclass_ext):
			upfgclass_name = upfgclass_filename[:upfgclass_filename.rfind(upfgclass_ext)]
			relative_folder = folder_src[folder_src.find(folder_in)+len(folder_in):].lstrip('\\').lstrip('/')
			folder_dest = os.path.join(folder_out, relative_folder)

			header = HeaderFile()
			
			header.upfgclass_data.SetFolder(folder_src)
			header.upfgclass_data.SetName(upfgclass_name)
			header.upfgclass_data.Load()

			class CustomData():
				FolderSrc = folder_src
				FolderDest = folder_dest
				RelativeFolder = relative_folder
				UPFGClassName = upfgclass_name
				Header = header
				UPFGClass = header.upfgclass_data

			yield CustomData

	def GetTemplate(templateType):
		return UPFG.templates[UPFG.TemplateDef.NormalizeType(templateType)]

	def GetClassNameByTemplateType(templateType):
		return UPFG.classNames[UPFG.TemplateDef.NormalizeType(templateType)]

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
		upfgInputTemplates = 'upfgInputTemplates'
		upfgInputClasses = 'upfgInputClasses'
		upfgOutputClasses = 'upfgOutputClasses'
		upfgTemplateExt = 'upfgTemplateExt'
		upfgClassExt = 'upfgClassExt'
		upfgModuleExt = 'upfgModuleExt'

	class Settings():
		def __init__(self):
			self.settings = JsonFileData()
			self.settings.filename = "UPFG/UPFG.settings.json"

			# Default values
			self.SetInputTemplatesPath("UPFG/UPFGTemplates")
			self.SetInputClassesPath("UPFGSourceClasses")
			self.SetOutputClassesPath("UPFGGeneratedClasses")
			self.SetTemplateExt(".upfgtemplate.json")
			self.SetClassExt(".upfgclass.json")
			self.SetModuleExt(".upfgmodule.json")
			self.SetAPI("UNKNOWN_API")

			# Load custom values (overwrite if necessary)
			self.settings.Load()

		def GetInputTemplatesPath(self):
			return self.settings.data[UPFG.Labels.upfgInputTemplates]
		
		def GetInputClassesPath(self):
			return self.settings.data[UPFG.Labels.upfgInputClasses]

		def GetOutputClassesPath(self):
			return self.settings.data[UPFG.Labels.upfgOutputClasses]

		def GetTemplateExt(self):
			return self.settings.data[UPFG.Labels.upfgTemplateExt]

		def GetClassExt(self):
			return self.settings.data[UPFG.Labels.upfgClassExt]
		
		def GetModuleExt(self):
			return self.settings.data[UPFG.Labels.upfgModuleExt]

		def GetAPI(self):
			return self.settings.data["API"]

		def SetInputTemplatesPath(self, value):
			self.settings.data[UPFG.Labels.upfgInputTemplates] = value

		def SetInputClassesPath(self, value):
			self.settings.data[UPFG.Labels.upfgInputClasses] = value

		def SetOutputClassesPath(self, value):
			self.settings.data[UPFG.Labels.upfgOutputClasses] = value

		def SetTemplateExt(self, value):
			self.settings.data[UPFG.Labels.upfgTemplateExt] = value

		def SetClassExt(self, value):
			self.settings.data[UPFG.Labels.upfgClassExt] = value
			
		def SetModuleExt(self, value):
			self.settings.data[UPFG.Labels.upfgModuleExt] = value

		def SetAPI(self, value):
			self.settings.data["API"] = value

class UPFGAbstractTemplateData(JsonFileData):
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
		return UPFG.TemplateDef.NormalizeAlias(self.data["alias"])

	def GetName(self, use_precached=False):
		if 'name' not in self.data:
			return ''
		return UPFG.TemplateDef.NormalizeName(self.data["name"])
	
	def GetType(self, use_precached=False):
		if 'type' not in self.data:
			return ''
		return UPFG.TemplateDef.NormalizeType(self.data["type"])
	
	def GetExtension(self):
		return ""

	def GetFilename(self):
		return UPFG.TemplateDef.NormalizeFilename(self.GetName()+self.GetExtension())

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
		data = UPFG.ExtendData(data)
		return data

	def Render(self, recursions = UPFG.DEFAULT_RECURSIONS):
		template_content = UPFG.GetTemplate(self.GetType())
		return self.RenderSomeContent(template_content, recursions)

	def RenderSomeContent(self, template_content, recursions = 1):
		built_data = self.BuildData()
		return self.RenderSomeContentWithData(template_content, built_data, recursions)

	def RenderSomeContentWithData(self, template_content, built_data, recursions = 1):
		for i in range(recursions):
			try:
				template_content = Template(template_content).render(**built_data, **UPFG.TypeAliases)
			except Exception as error:
				print("Some error occurred while rendering template: \n>>>\t", error, "\n")
		return template_content

class UPFGModuleTemplateData(UPFGAbstractTemplateData):
	def __init__(self):
		super().__init__()
		self.SetType("Module")

	def GetExtension(self):
		return UPFG.settings.GetModuleExt()
	
	def GetModuleName(self, use_precached=False):
		moduleName = ''
		templateType = self.GetType()
		if 'moduleName' in self.data:
			moduleName = UPFG.TemplateDef.NormalizeModuleName(self.data["moduleName"])
		if moduleName or use_precached:
			return moduleName
		return self.GetName() # self.RenderSomeContentWithData(UPFG.GetClassNameByTemplateType(templateType), self.BuildData(use_precached=True))

	def SetModuleName(self, module_name):
		self.data["moduleName"] = module_name
		
	def BuildData(self, use_precached=False):
		data = super().BuildData(use_precached=use_precached)
		moduleName = self.GetModuleName(use_precached=use_precached)

		data["UPFGModule"] = self
		data["moduleName"] = moduleName
		return data

class UPFGClassTemplateData(UPFGAbstractTemplateData):
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
			className = UPFG.TemplateDef.NormalizeClassName(self.data["className"])
		if className or use_precached:
			return className
		return self.RenderSomeContentWithData(UPFG.GetClassNameByTemplateType(templateType), self.BuildData(use_precached=True))

	def GetNamespace(self, use_precached=False):
		if 'namespace' not in self.data:
			return ''
		return UPFG.TemplateDef.NormalizeNamespace(self.data["namespace"])

	def GetExtension(self):
		return UPFG.settings.GetClassExt()

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

		data["UPFGClass"] = self
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
		self.file_data = UPFGClassTemplateData()

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
		self.file_data = UPFGModuleTemplateData()

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

		templateModuleHeader = UPFG.GetTemplate("ModuleHeader")
		templateModuleSource = UPFG.GetTemplate("ModuleSource")

		with open(os.path.join(folder, self.GetFilename()), "w") as text_file:
			text_file.write(self.GenerateContent())
			
		for template, subfolder, ext in [(templateModuleHeader, os.path.join(folder, "Source/Public"), '.h'), (templateModuleSource, os.path.join(folder, "Source/Private"), '.cpp')]:
			if not os.path.exists(subfolder):
				os.makedirs(subfolder)
			with open(os.path.join(subfolder, self.GetName()+ext), "w") as text_file:
				text_file.write(self.file_data.RenderSomeContent(template))

		# \TODO : Also generate the module .h and .cpp, other than .Build.cs only

def SetupFileClasses():
	FileFactory.MapOfFileClasses[UPFG.settings.GetClassExt()] = HeaderFile
	FileFactory.MapOfFileClasses[UPFG.settings.GetModuleExt()] = ModuleFile
	FileFactory.MapOfFileClasses[None] = GenericFile
	
UPFG.settings = UPFG.Settings()

if __name__== "__main__":

	# Setup file classes of the file factory

	SetupFileClasses()

	# Import all templates from template modules

	for module in Utils.Path.LoadAllModulesFromDir(UPFG.settings.GetInputTemplatesPath()):
		print("imported module: ", module)

		if not hasattr(module, 'GetTemplateInfo'):
			continue

		templateName, templateContent, className = module.GetTemplateInfo()
		
		if className is not None:
			UPFG.classNames[templateName] = className

		if templateContent is not None:
			UPFG.templates[templateName] = templateContent

	# Cook all templates in local data

	for data in UPFG.RecurseFiles():
		if not hasattr(data.File.file_data, "GetAlias"):
			continue

		alias = data.File.file_data.GetAlias()
		if alias is not "":
			UPFG.TypeAliases[alias] = data.File.GetName()

	# For all files you find in a certain folder (and subfolders recursively)
	# consider each file and generate, from it as a template, the corresponding
	# generated header - by also mantaining the tree structure

	for data in UPFG.RecurseFiles():
		data.File.GenerateAndSave(data.FolderDest)
			