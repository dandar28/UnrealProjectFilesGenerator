
def GetTemplateInfo():
	className = '${name}'
	templateName = 'ModuleHeader'
	templateContent = '''
#pragma once
#include "ModuleManager.h"

class ${moduleName} : public IModuleInterface
{
public:
	static inline I${moduleName}& Get()
	{
		return FModuleManager::LoadModuleChecked<I${moduleName}>("${moduleName}");
	}

	static inline bool IsAvailable()
	{
		return FModuleManager::Get().IsModuleLoaded("${moduleName}");
	}
};
''';

	return templateName, templateContent, className