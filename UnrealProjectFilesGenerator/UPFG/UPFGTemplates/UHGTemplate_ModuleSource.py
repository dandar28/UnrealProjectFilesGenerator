
def GetTemplateInfo():
	className = '${name}'
	templateName = 'ModuleSource'
	templateContent = '''
#include "${moduleName}_PrivatePCH.h"

class F${moduleName} : public I${moduleName}
{
	virtual void StartupModule() override
	{
	}

	virtual void ShutdownModule() override
	{
	}
};

IMPLEMENT_MODULE( F${moduleName}, ${moduleName} )
''';

	return templateName, templateContent, className